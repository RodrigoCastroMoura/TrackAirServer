import asyncio
from typing import Optional
from .models import VehicleData, Vehicle, DeviceStatus
from .protocol_parser import GV50ProtocolParser
from .mongodb_client import mongodb_client
from .command_manager import command_manager
from .device_manager import device_manager
from .config import config
from .logger import get_logger

logger = get_logger(__name__)

class GV50TCPServer:
    """TCP Server for GV50 GPS devices."""
    
    def __init__(self):
        self.server: Optional[asyncio.Server] = None
        self.parser = GV50ProtocolParser()
        
    async def start(self):
        """Start the TCP server."""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                config.tcp_host,
                config.tcp_port,
                limit=1024 * 1024  # 1MB buffer limit
            )
            
            addr = self.server.sockets[0].getsockname()
            logger.info(f"GV50 TCP Server started on {addr[0]}:{addr[1]}")
            
            # Start device manager
            await device_manager.start()
            
            # Start serving
            await self.server.serve_forever()
            
        except Exception as e:
            logger.error(f"Error starting TCP server: {e}")
            raise
    
    async def stop(self):
        """Stop the TCP server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
        await device_manager.stop()
        logger.info("TCP Server stopped")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection."""
        remote_addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {remote_addr}")
        
        client_imei = None
        
        try:
            while True:
                # Read data with timeout
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=30.0)
                except asyncio.TimeoutError:
                    logger.debug(f"Connection timeout for {remote_addr}")
                    break
                
                if not data:
                    logger.debug(f"Connection closed by client {remote_addr}")
                    break
                
                # Decode and parse message
                raw_message = data.decode('utf-8', errors='ignore').strip()
                
                if not raw_message:
                    continue
                
                logger.info(f"Received from {remote_addr}: {raw_message}")
                await self._save_raw_log(raw_message)
                
                # Parse the message
                parsed_msg = self.parser.parse_message(raw_message)
                if not parsed_msg:
                    logger.warning(f"Failed to parse message: {raw_message}")
                    continue
                
                # Register device if first valid message
                if client_imei is None and parsed_msg.imei:
                    client_imei = parsed_msg.imei
                    await device_manager.register_device(client_imei, writer, str(remote_addr))
                
                # Update device activity
                if client_imei:
                    await device_manager.update_device_activity(client_imei)
                
                # Process the message
                await self._process_message(parsed_msg, writer)
                
        except Exception as e:
            logger.error(f"Error handling client {remote_addr}: {e}")
        finally:
            # Clean up connection
            if client_imei:
                await device_manager.unregister_device(client_imei)
            
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            
            logger.info(f"Connection closed for {remote_addr}")
    
    async def _process_message(self, parsed_msg, writer):
        """Process parsed message based on type."""
        try:
            if parsed_msg.message_type.value in ["+RESP", "+BUFF"]:
                await self._process_data_message(parsed_msg, writer)
            elif parsed_msg.message_type.value == "+ACK":
                await self._process_ack_message(parsed_msg)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _process_data_message(self, parsed_msg, writer):
        """Process data messages (+RESP, +BUFF)."""
        try:
            # Extract vehicle data
            vehicle_data = self.parser.extract_vehicle_data(parsed_msg)
            if vehicle_data:
                # Save vehicle data to database
                await mongodb_client.insert_vehicle_data(vehicle_data)
                
                # Update vehicle status based on message type
                if parsed_msg.command_type.value in ["GTIGN", "GTIGF"]:
                    await self._update_vehicle_ignition(parsed_msg)
            
            # Send pending commands to device
            await self._send_pending_commands(parsed_msg.imei, writer)
            
        except Exception as e:
            logger.error(f"Error processing data message: {e}")
    
    async def _process_ack_message(self, parsed_msg):
        """Process acknowledgment messages (+ACK)."""
        try:
            # Process command acknowledgment
            await command_manager.process_command_acknowledgment(
                parsed_msg.imei, 
                parsed_msg.raw_data
            )
            
        except Exception as e:
            logger.error(f"Error processing ACK message: {e}")
    
    async def _update_vehicle_ignition(self, parsed_msg):
        """Update vehicle ignition status."""
        try:
            vehicle = await mongodb_client.get_vehicle_by_imei(parsed_msg.imei)
            if vehicle:
                vehicle.ignition = (parsed_msg.command_type.value == "GTIGN")
                await mongodb_client.upsert_vehicle(vehicle)
                
        except Exception as e:
            logger.error(f"Error updating vehicle ignition: {e}")
    
    async def _send_pending_commands(self, imei: str, writer: asyncio.StreamWriter):
        """Send pending commands to device."""
        try:
            pending_commands = await command_manager.get_pending_commands_for_device(imei)
            
            for command in pending_commands:
                success = await command_manager.send_command_to_device(writer, command)
                if not success:
                    logger.error(f"Failed to send command {command.id} to device {imei}")
                    
        except Exception as e:
            logger.error(f"Error sending pending commands: {e}")
    
    async def _save_raw_log(self, raw_message: str):
        """Save raw message to log file for debugging."""
        try:
            timestamp = asyncio.get_event_loop().time()
            log_entry = f"{timestamp}: {raw_message}\n"
            
            # This could be enhanced to write to a separate log file
            logger.debug(f"Raw message: {raw_message}")
            
        except Exception as e:
            logger.error(f"Error saving raw log: {e}")

# Global instance
tcp_server = GV50TCPServer()
