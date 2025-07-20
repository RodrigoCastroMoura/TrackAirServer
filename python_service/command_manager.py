import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .models import Command, Vehicle, Message, DeviceStatus
from .protocol_parser import GV50ProtocolParser
from .mongodb_client import mongodb_client
from .logger import get_logger

logger = get_logger(__name__)

class CommandManager:
    """Manages device commands and communication."""
    
    def __init__(self):
        self.parser = GV50ProtocolParser()
        self.command_queue: Dict[str, asyncio.Queue] = {}
        
    async def queue_block_command(self, imei: str, block: bool, tracker_model: str = "GV50", password: str = "") -> str:
        """Queue a block/unblock command for a device."""
        try:
            # Generate command
            command_data = self.parser.generate_command("GTOUT", imei, {
                "block": block,
                "tracker_model": tracker_model,
                "password": password
            })
            
            if not command_data:
                raise ValueError("Failed to generate command")
            
            # Create command record
            command = Command(
                imei=imei,
                command_type="GTOUT",
                command_data=command_data,
                parameters={
                    "block": block,
                    "tracker_model": tracker_model,
                    "action": "block" if block else "unblock"
                }
            )
            
            # Insert into database
            command_id = await mongodb_client.insert_command(command)
            
            # Update vehicle status
            vehicle = await mongodb_client.get_vehicle_by_imei(imei)
            if vehicle:
                vehicle.block_command_pending = True
                await mongodb_client.upsert_vehicle(vehicle)
            
            logger.info(f"Queued {'block' if block else 'unblock'} command for IMEI: {imei}")
            return command_id
            
        except Exception as e:
            logger.error(f"Error queuing block command: {e}")
            raise
    
    async def queue_server_config_command(self, imei: str, server_ip: str, server_port: int, password: str = "") -> str:
        """Queue a server configuration command."""
        try:
            command_data = self.parser.generate_command("GTSRI", imei, {
                "server_ip": server_ip,
                "server_port": server_port,
                "password": password
            })
            
            if not command_data:
                raise ValueError("Failed to generate server config command")
            
            command = Command(
                imei=imei,
                command_type="GTSRI",
                command_data=command_data,
                parameters={
                    "server_ip": server_ip,
                    "server_port": server_port,
                    "action": "server_config"
                }
            )
            
            command_id = await mongodb_client.insert_command(command)
            
            logger.info(f"Queued server config command for IMEI: {imei}")
            return command_id
            
        except Exception as e:
            logger.error(f"Error queuing server config command: {e}")
            raise
    
    async def queue_apn_config_command(self, imei: str, apn_name: str, apn_username: str = "", apn_password: str = "", password: str = "") -> str:
        """Queue an APN configuration command."""
        try:
            command_data = self.parser.generate_command("GTBSI", imei, {
                "apn_name": apn_name,
                "apn_username": apn_username,
                "apn_password": apn_password,
                "password": password
            })
            
            if not command_data:
                raise ValueError("Failed to generate APN config command")
            
            command = Command(
                imei=imei,
                command_type="GTBSI",
                command_data=command_data,
                parameters={
                    "apn_name": apn_name,
                    "apn_username": apn_username,
                    "action": "apn_config"
                }
            )
            
            command_id = await mongodb_client.insert_command(command)
            
            logger.info(f"Queued APN config command for IMEI: {imei}")
            return command_id
            
        except Exception as e:
            logger.error(f"Error queuing APN config command: {e}")
            raise
    
    async def get_pending_commands_for_device(self, imei: str) -> List[Command]:
        """Get all pending commands for a device."""
        try:
            commands = await mongodb_client.get_pending_commands(imei)
            return commands
        except Exception as e:
            logger.error(f"Error getting pending commands for {imei}: {e}")
            return []
    
    async def send_command_to_device(self, writer: asyncio.StreamWriter, command: Command) -> bool:
        """Send command to device over TCP connection."""
        try:
            command_bytes = command.command_data.encode('utf-8')
            writer.write(command_bytes)
            await writer.drain()
            
            # Update command status
            await mongodb_client.update_command_status(command.id, "sent")
            
            logger.info(f"Sent command to device {command.imei}: {command.command_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to device: {e}")
            await mongodb_client.update_command_status(command.id, "failed", error=str(e))
            return False
    
    async def process_command_acknowledgment(self, imei: str, ack_data: str) -> bool:
        """Process command acknowledgment from device."""
        try:
            # Find the most recent sent command for this device
            # This is a simplified approach - in production you might want more sophisticated matching
            commands = await mongodb_client.get_pending_commands(imei)
            
            for command in commands:
                if command.status == "sent":
                    # Process based on command type
                    if command.command_type == "GTOUT":
                        await self._process_gtout_ack(command, ack_data)
                    
                    # Mark as acknowledged
                    await mongodb_client.update_command_status(command.id, "acknowledged")
                    
                    logger.info(f"Processed acknowledgment for command {command.id}")
                    return True
            
            logger.warning(f"No matching command found for ACK from {imei}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing command acknowledgment: {e}")
            return False
    
    async def _process_gtout_ack(self, command: Command, ack_data: str):
        """Process GTOUT (block/unblock) command acknowledgment."""
        try:
            # Parse ACK data to determine if command was successful
            # +ACK:GTOUT,<device_id>,<imei>,<result_code>,...
            parts = ack_data.split(',')
            if len(parts) >= 4:
                result_code = parts[4]
                success = (result_code == "0000")
                
                # Update vehicle status
                vehicle = await mongodb_client.get_vehicle_by_imei(command.imei)
                if vehicle:
                    vehicle.block_command_pending = False
                    vehicle.block_warning_sent = True
                    vehicle.blocked = success and command.parameters.get("block", False)
                    await mongodb_client.upsert_vehicle(vehicle)
                    
                    # Create user message
                    action = "bloqueado" if command.parameters.get("block", False) else "desbloqueado"
                    status = "com sucesso" if success else "falhou"
                    
                    message = Message(
                        cpf=vehicle.cpf,
                        imei=command.imei,
                        message_type_id=2 if command.parameters.get("block", False) else 1,
                        message=f"Veiculo com placa: {vehicle.plate}, foi {action} {status}!",
                        read=False
                    )
                    
                    await mongodb_client.insert_message(message)
                    
                logger.info(f"Processed GTOUT ACK for {command.imei}: {'success' if success else 'failed'}")
                
        except Exception as e:
            logger.error(f"Error processing GTOUT ACK: {e}")
    
    async def cleanup_expired_commands(self):
        """Clean up expired and failed commands."""
        try:
            # This would typically be run as a background task
            # Implementation depends on your specific requirements
            logger.debug("Cleaning up expired commands")
        except Exception as e:
            logger.error(f"Error cleaning up expired commands: {e}")

# Global instance
command_manager = CommandManager()
