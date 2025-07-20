import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
from .models import VehicleData, Vehicle, Message, Command, DeviceConfiguration
from .config import config
from .logger import get_logger

logger = get_logger(__name__)

class MongoDBClient:
    """MongoDB client for GPS tracking service."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """Connect to MongoDB and setup collections."""
        try:
            self.client = AsyncIOMotorClient(config.mongodb_url)
            self.database = self.client[config.mongodb_database]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            # Setup indexes
            await self._setup_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _setup_indexes(self):
        """Setup database indexes for optimal performance."""
        try:
            # Vehicle data indexes
            await self.database.dados_veiculo.create_indexes([
                IndexModel([("imei", ASCENDING), ("timestamp", DESCENDING)]),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("imei", ASCENDING)])
            ])
            
            # Vehicle indexes
            await self.database.veiculo.create_indexes([
                IndexModel([("imei", ASCENDING)], unique=True),
                IndexModel([("cpf", ASCENDING)]),
                IndexModel([("status", ASCENDING)])
            ])
            
            # Command indexes
            await self.database.comandos_pendentes.create_indexes([
                IndexModel([("imei", ASCENDING), ("status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("status", ASCENDING)])
            ])
            
            # Configuration indexes
            await self.database.configuracoes_dispositivo.create_indexes([
                IndexModel([("imei", ASCENDING)], unique=True),
                IndexModel([("updated_at", DESCENDING)])
            ])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # Vehicle Data operations
    async def insert_vehicle_data(self, data: VehicleData) -> str:
        """Insert vehicle tracking data."""
        try:
            result = await self.database.dados_veiculo.insert_one(data.dict(by_alias=True, exclude={"id"}))
            logger.debug(f"Inserted vehicle data for IMEI: {data.imei}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting vehicle data: {e}")
            raise
    
    async def get_vehicle_data_by_imei(self, imei: str, limit: int = 100) -> List[VehicleData]:
        """Get recent vehicle data by IMEI."""
        try:
            cursor = self.database.dados_veiculo.find(
                {"imei": imei}
            ).sort("timestamp", DESCENDING).limit(limit)
            
            results = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(VehicleData(**doc))
            
            return results
        except Exception as e:
            logger.error(f"Error getting vehicle data: {e}")
            return []
    
    # Vehicle operations
    async def get_vehicle_by_imei(self, imei: str) -> Optional[Vehicle]:
        """Get vehicle by IMEI."""
        try:
            doc = await self.database.veiculo.find_one({"imei": imei})
            if doc:
                doc["_id"] = str(doc["_id"])
                return Vehicle(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting vehicle: {e}")
            return None
    
    async def upsert_vehicle(self, vehicle: Vehicle) -> str:
        """Insert or update vehicle."""
        try:
            vehicle_dict = vehicle.dict(by_alias=True, exclude={"id"})
            result = await self.database.veiculo.update_one(
                {"imei": vehicle.imei},
                {"$set": vehicle_dict},
                upsert=True
            )
            
            if result.upserted_id:
                logger.debug(f"Inserted new vehicle: {vehicle.imei}")
                return str(result.upserted_id)
            else:
                logger.debug(f"Updated vehicle: {vehicle.imei}")
                # Get existing ID
                doc = await self.database.veiculo.find_one({"imei": vehicle.imei})
                return str(doc["_id"]) if doc else ""
                
        except Exception as e:
            logger.error(f"Error upserting vehicle: {e}")
            raise
    
    async def get_all_vehicles(self) -> List[Vehicle]:
        """Get all vehicles."""
        try:
            cursor = self.database.veiculo.find()
            results = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(Vehicle(**doc))
            return results
        except Exception as e:
            logger.error(f"Error getting all vehicles: {e}")
            return []
    
    # Message operations
    async def insert_message(self, message: Message) -> str:
        """Insert system message."""
        try:
            result = await self.database.mensagem.insert_one(message.dict(by_alias=True, exclude={"id"}))
            logger.debug(f"Inserted message for CPF: {message.cpf}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting message: {e}")
            raise
    
    async def get_messages_by_cpf(self, cpf: str, limit: int = 50) -> List[Message]:
        """Get messages by CPF."""
        try:
            cursor = self.database.mensagem.find(
                {"cpf": cpf}
            ).sort("dt_mensagem", DESCENDING).limit(limit)
            
            results = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(Message(**doc))
            
            return results
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    # Command operations
    async def insert_command(self, command: Command) -> str:
        """Insert pending command."""
        try:
            result = await self.database.comandos_pendentes.insert_one(command.dict(by_alias=True, exclude={"id"}))
            logger.info(f"Inserted command for IMEI: {command.imei}, type: {command.command_type}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting command: {e}")
            raise
    
    async def get_pending_commands(self, imei: str) -> List[Command]:
        """Get pending commands for device."""
        try:
            cursor = self.database.comandos_pendentes.find(
                {"imei": imei, "status": "pending"}
            ).sort("created_at", ASCENDING)
            
            results = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(Command(**doc))
            
            return results
        except Exception as e:
            logger.error(f"Error getting pending commands: {e}")
            return []
    
    async def update_command_status(self, command_id: str, status: str, **kwargs) -> bool:
        """Update command status."""
        try:
            update_data = {"status": status}
            
            if status == "sent":
                update_data["sent_at"] = datetime.utcnow()
            elif status == "acknowledged":
                update_data["acknowledged_at"] = datetime.utcnow()
            
            update_data.update(kwargs)
            
            result = await self.database.comandos_pendentes.update_one(
                {"_id": command_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating command status: {e}")
            return False
    
    # Device Configuration operations
    async def get_device_configuration(self, imei: str) -> Optional[DeviceConfiguration]:
        """Get device configuration."""
        try:
            doc = await self.database.configuracoes_dispositivo.find_one({"imei": imei})
            if doc:
                doc["_id"] = str(doc["_id"])
                return DeviceConfiguration(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting device configuration: {e}")
            return None
    
    async def upsert_device_configuration(self, config_data: DeviceConfiguration) -> str:
        """Insert or update device configuration."""
        try:
            config_dict = config_data.dict(by_alias=True, exclude={"id"})
            result = await self.database.configuracoes_dispositivo.update_one(
                {"imei": config_data.imei},
                {"$set": config_dict},
                upsert=True
            )
            
            if result.upserted_id:
                return str(result.upserted_id)
            else:
                doc = await self.database.configuracoes_dispositivo.find_one({"imei": config_data.imei})
                return str(doc["_id"]) if doc else ""
                
        except Exception as e:
            logger.error(f"Error upserting device configuration: {e}")
            raise

# Global instance
mongodb_client = MongoDBClient()
