import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from .models import ParsedMessage, MessageType, CommandType, VehicleData
from .logger import get_logger

logger = get_logger(__name__)

class GV50ProtocolParser:
    """Parser for GV50 GPS device protocol messages."""
    
    def __init__(self):
        self.message_pattern = re.compile(r'^(\+RESP|\+BUFF|\+ACK):(.+)')
    
    def parse_message(self, raw_data: str) -> Optional[ParsedMessage]:
        """Parse raw TCP message from GV50 device."""
        try:
            raw_data = raw_data.strip()
            logger.debug(f"Parsing raw message: {raw_data}")
            
            match = self.message_pattern.match(raw_data)
            if not match:
                logger.warning(f"Invalid message format: {raw_data}")
                return None
            
            message_type = MessageType(match.group(1))
            payload = match.group(2)
            
            # Split payload by comma
            parts = payload.split(',')
            if len(parts) < 3:
                logger.warning(f"Insufficient message parts: {raw_data}")
                return None
            
            command_type_str = parts[0]
            try:
                command_type = CommandType(command_type_str)
            except ValueError:
                logger.warning(f"Unknown command type: {command_type_str}")
                return None
            
            # Extract IMEI (usually at index 2)
            imei = parts[2] if len(parts) > 2 else ""
            
            return ParsedMessage(
                message_type=message_type,
                command_type=command_type,
                imei=imei,
                parameters=parts,
                raw_data=raw_data
            )
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}, raw_data: {raw_data}")
            return None
    
    def extract_vehicle_data(self, parsed_msg: ParsedMessage) -> Optional[VehicleData]:
        """Extract vehicle tracking data from parsed message."""
        try:
            if parsed_msg.command_type == CommandType.GTFRI:
                return self._extract_gtfri_data(parsed_msg)
            elif parsed_msg.command_type in [CommandType.GTIGN, CommandType.GTIGF]:
                return self._extract_ignition_data(parsed_msg)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting vehicle data: {e}")
            return None
    
    def _extract_gtfri_data(self, parsed_msg: ParsedMessage) -> Optional[VehicleData]:
        """Extract data from GTFRI (Fixed Report Information) message."""
        params = parsed_msg.parameters
        
        if parsed_msg.message_type == MessageType.RESP:
            # +RESP:GTFRI format
            if len(params) < 14:
                return None
                
            return VehicleData(
                imei=params[2],
                speed=params[8],
                altitude=params[10],
                longitude=params[11],
                latitude=params[12],
                device_time=params[13],
                timestamp=datetime.utcnow(),
                raw_data=parsed_msg.raw_data
            )
            
        elif parsed_msg.message_type == MessageType.BUFF:
            # +BUFF:GTFRI format
            if len(params) < 14:
                return None
                
            device_time = params[13]
            timestamp = self._parse_device_time(device_time) if device_time else datetime.utcnow()
            
            return VehicleData(
                imei=params[2],
                speed=params[8],
                altitude=params[10],
                longitude=params[11],
                latitude=params[12],
                device_time=device_time,
                timestamp=timestamp,
                raw_data=parsed_msg.raw_data
            )
        
        return None
    
    def _extract_ignition_data(self, parsed_msg: ParsedMessage) -> Optional[VehicleData]:
        """Extract data from GTIGN/GTIGF (Ignition On/Off) messages."""
        params = parsed_msg.parameters
        
        if len(params) < 12:
            return None
        
        ignition_state = parsed_msg.command_type == CommandType.GTIGN
        
        return VehicleData(
            imei=params[2],
            speed=params[6],
            altitude=params[8],
            longitude=params[9],
            latitude=params[10],
            device_time=params[11],
            ignition=ignition_state,
            timestamp=datetime.utcnow(),
            raw_data=parsed_msg.raw_data
        )
    
    def _parse_device_time(self, device_time_str: str) -> Optional[datetime]:
        """Parse device timestamp string to datetime object."""
        try:
            if len(device_time_str) >= 12:
                # Format: YYYYMMDDHHMMSS
                year = int(device_time_str[0:4])
                month = int(device_time_str[4:6])
                day = int(device_time_str[6:8])
                hour = int(device_time_str[8:10])
                minute = int(device_time_str[10:12])
                second = int(device_time_str[12:14]) if len(device_time_str) >= 14 else 0
                
                return datetime(year, month, day, hour, minute, second)
        except (ValueError, IndexError):
            pass
        
        return None
    
    def generate_command(self, command_type: str, imei: str, parameters: Dict[str, Any]) -> str:
        """Generate command string for device."""
        try:
            if command_type == "GTOUT":
                return self._generate_gtout_command(imei, parameters)
            elif command_type == "GTSRI":
                return self._generate_gtsri_command(imei, parameters)
            elif command_type == "GTBSI":
                return self._generate_gtbsi_command(imei, parameters)
            
            return ""
            
        except Exception as e:
            logger.error(f"Error generating command: {e}")
            return ""
    
    def _generate_gtout_command(self, imei: str, parameters: Dict[str, Any]) -> str:
        """Generate GTOUT (Output Control) command for blocking/unblocking."""
        tracker_model = parameters.get("tracker_model", "GV50")
        password = parameters.get("password", "")
        block = parameters.get("block", False)
        
        bit = "1" if block else "0"
        counter = parameters.get("counter", f"000{bit}")
        
        if tracker_model == "GMT200":
            return f"AT+GTOUT={password},{bit},0,0,0,,,,,,,,,,{counter}$"
        elif tracker_model == "GV300":
            return f"AT+GTOUT={password},{bit},,,0,0,0,0,5,1,0,,1,1,,,{counter}$"
        elif tracker_model == "GV50":
            return f"AT+GTOUT={password},{bit},,,,,,0,,,,,,,{counter}$"
        else:
            # Default GV50 format
            return f"AT+GTOUT={password},{bit},,,,,,0,,,,,,,{counter}$"
    
    def _generate_gtsri_command(self, imei: str, parameters: Dict[str, Any]) -> str:
        """Generate GTSRI (Server Registration Info) command for server configuration."""
        password = parameters.get("password", "")
        server_ip = parameters.get("server_ip", "")
        server_port = parameters.get("server_port", "")
        counter = parameters.get("counter", "0001")
        
        return f"AT+GTSRI={password},{server_ip},{server_port},,,{counter}$"
    
    def _generate_gtbsi_command(self, imei: str, parameters: Dict[str, Any]) -> str:
        """Generate GTBSI (Bearer Setting Info) command for APN configuration."""
        password = parameters.get("password", "")
        apn_name = parameters.get("apn_name", "")
        apn_username = parameters.get("apn_username", "")
        apn_password = parameters.get("apn_password", "")
        counter = parameters.get("counter", "0001")
        
        return f"AT+GTBSI={password},{apn_name},{apn_username},{apn_password},,,{counter}$"
