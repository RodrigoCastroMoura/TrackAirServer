import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from .models import Vehicle, DeviceStatus
from .mongodb_client import mongodb_client
from .logger import get_logger

logger = get_logger(__name__)

class DeviceManager:
    """Manages device connections and status."""
    
    def __init__(self):
        self.connected_devices: Dict[str, dict] = {}
        self.device_writers: Dict[str, asyncio.StreamWriter] = {}
        self.device_timeouts: Dict[str, datetime] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the device manager."""
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Device manager started")
        
    async def stop(self):
        """Stop the device manager."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            
        # Close all connections
        for writer in self.device_writers.values():
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
                
        logger.info("Device manager stopped")
    
    async def register_device(self, imei: str, writer: asyncio.StreamWriter, remote_addr: str):
        """Register a device connection."""
        try:
            # Store connection info
            self.connected_devices[imei] = {
                "remote_addr": remote_addr,
                "connected_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            self.device_writers[imei] = writer
            self.device_timeouts[imei] = datetime.utcnow() + timedelta(seconds=300)  # 5 minute timeout
            
            # Update vehicle status in database
            vehicle = await mongodb_client.get_vehicle_by_imei(imei)
            if vehicle:
                vehicle.status = DeviceStatus.ONLINE
                vehicle.last_seen = datetime.utcnow()
                await mongodb_client.upsert_vehicle(vehicle)
            else:
                # Create new vehicle record
                vehicle = Vehicle(
                    imei=imei,
                    status=DeviceStatus.ONLINE,
                    last_seen=datetime.utcnow()
                )
                await mongodb_client.upsert_vehicle(vehicle)
            
            logger.info(f"Device {imei} connected from {remote_addr}")
            
        except Exception as e:
            logger.error(f"Error registering device {imei}: {e}")
    
    async def unregister_device(self, imei: str):
        """Unregister a device connection."""
        try:
            # Remove from tracking
            if imei in self.connected_devices:
                del self.connected_devices[imei]
            
            if imei in self.device_writers:
                del self.device_writers[imei]
                
            if imei in self.device_timeouts:
                del self.device_timeouts[imei]
            
            # Update vehicle status
            vehicle = await mongodb_client.get_vehicle_by_imei(imei)
            if vehicle:
                vehicle.status = DeviceStatus.OFFLINE
                vehicle.last_seen = datetime.utcnow()
                await mongodb_client.upsert_vehicle(vehicle)
            
            logger.info(f"Device {imei} disconnected")
            
        except Exception as e:
            logger.error(f"Error unregistering device {imei}: {e}")
    
    async def update_device_activity(self, imei: str):
        """Update device last activity timestamp."""
        if imei in self.connected_devices:
            self.connected_devices[imei]["last_activity"] = datetime.utcnow()
            self.device_timeouts[imei] = datetime.utcnow() + timedelta(seconds=300)
    
    def get_device_writer(self, imei: str) -> Optional[asyncio.StreamWriter]:
        """Get the writer for a connected device."""
        return self.device_writers.get(imei)
    
    def is_device_connected(self, imei: str) -> bool:
        """Check if device is currently connected."""
        return imei in self.connected_devices
    
    def get_connected_devices(self) -> Set[str]:
        """Get set of currently connected device IMEIs."""
        return set(self.connected_devices.keys())
    
    def get_device_info(self, imei: str) -> Optional[dict]:
        """Get connection info for a device."""
        return self.connected_devices.get(imei)
    
    async def _cleanup_loop(self):
        """Background task to cleanup timed out devices."""
        while True:
            try:
                now = datetime.utcnow()
                timed_out_devices = []
                
                # Find timed out devices
                for imei, timeout in self.device_timeouts.items():
                    if now > timeout:
                        timed_out_devices.append(imei)
                
                # Cleanup timed out devices
                for imei in timed_out_devices:
                    logger.info(f"Device {imei} timed out, cleaning up")
                    await self.unregister_device(imei)
                
                # Sleep for 30 seconds before next cleanup
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in device cleanup loop: {e}")
                await asyncio.sleep(30)

# Global instance
device_manager = DeviceManager()
