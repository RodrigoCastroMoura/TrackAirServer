#!/usr/bin/env python3
"""
GV50 GPS Tracking Service
Main entry point for the TCP server service.
"""

import asyncio
import signal
import sys
from .tcp_server import tcp_server
from .mongodb_client import mongodb_client
from .logger import get_logger, setup_logging
from .config import config

logger = get_logger(__name__)

class GPSTrackingService:
    """Main service class."""
    
    def __init__(self):
        self.running = False
        
    async def start(self):
        """Start the GPS tracking service."""
        try:
            logger.info("Starting GPS Tracking Service")
            logger.info(f"Configuration: TCP {config.tcp_host}:{config.tcp_port}, MongoDB: {config.mongodb_database}")
            
            # Connect to MongoDB
            await mongodb_client.connect()
            
            # Start TCP server
            self.running = True
            await tcp_server.start()
            
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the GPS tracking service."""
        if not self.running:
            return
            
        logger.info("Stopping GPS Tracking Service")
        self.running = False
        
        try:
            # Stop TCP server
            await tcp_server.stop()
            
            # Disconnect from MongoDB
            await mongodb_client.disconnect()
            
        except Exception as e:
            logger.error(f"Error stopping service: {e}")
        
        logger.info("GPS Tracking Service stopped")

def setup_signal_handlers(service: GPSTrackingService):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown")
        asyncio.create_task(service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main function."""
    # Setup logging
    setup_logging()
    
    # Create service instance
    service = GPSTrackingService()
    
    # Setup signal handlers
    setup_signal_handlers(service)
    
    try:
        # Start the service
        await service.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Service error: {e}")
    finally:
        await service.stop()
        sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
