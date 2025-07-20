# GV50 GPS Tracking Service

A complete Python TCP service for receiving GPS data from GV50 devices and managing bidirectional communication.

## Features

- **Asynchronous TCP Server**: Handles multiple device connections simultaneously
- **Protocol Parser**: Complete GV50 protocol support (+RESP, +BUFF, +ACK)
- **Command Management**: Send commands to devices (block/unblock, configuration)
- **Network Configuration**: Remote IP/port and APN configuration
- **MongoDB Integration**: Persistent data storage
- **Device Management**: Connection tracking and status management
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Supported Messages

### Incoming Messages
- **GTFRI**: Fixed Report Information (GPS data)
- **GTIGN/GTIGF**: Ignition On/Off events
- **GTOUT**: Output control acknowledgments

### Outgoing Commands
- **GTOUT**: Block/unblock device
- **GTSRI**: Server Registration Info (IP/port configuration)
- **GTBSI**: Bearer Setting Info (APN configuration)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
