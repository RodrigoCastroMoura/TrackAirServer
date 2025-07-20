# GPS Tracking System

## Overview

This is a comprehensive GPS tracking system designed to manage and monitor GPS devices (specifically GV50 trackers). The system consists of a React frontend, Express.js backend, and a Python TCP service for handling GPS device communications. It provides real-time tracking, device management, and command execution capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modern full-stack architecture with clear separation of concerns:

### Frontend Architecture
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS with shadcn/ui component library
- **State Management**: TanStack Query for server state
- **Routing**: Wouter for client-side routing
- **Build Tool**: Vite for development and building

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **Database**: PostgreSQL with Drizzle ORM
- **Session Management**: connect-pg-simple for PostgreSQL-backed sessions
- **API Style**: RESTful API with JSON responses

### TCP Service Architecture
- **Language**: Python with asyncio for concurrent connections
- **Database**: MongoDB for GPS data storage
- **Protocol**: Custom GV50 GPS device protocol parser
- **Concurrency**: Asynchronous TCP server handling multiple device connections

## Key Components

### Database Schema
The system uses two main database technologies:
- **PostgreSQL** (via Drizzle): User management and application data
- **MongoDB** (via Motor): GPS tracking data and device communications

Key entities include:
- Vehicles with IMEI tracking
- Vehicle tracking data (GPS coordinates, speed, ignition status)
- Commands for device control (block/unblock, configuration)
- Device configurations and status management

### GPS Protocol Handler
- Parses incoming GPS messages (+RESP, +BUFF, +ACK protocols)
- Supports various command types (GTFRI, GTIGN, GTIGF, GTOUT, GTSRI, GTBSI)
- Handles bidirectional communication with GPS devices
- Manages device connection states and timeouts

### Command System
- Queue-based command management for GPS devices
- Support for blocking/unblocking vehicles
- Server and APN configuration capabilities
- Command status tracking (pending, sent, acknowledged, failed)

### Frontend Components
- Dashboard with vehicle statistics and status overview
- Device management interface with real-time status updates
- Command center for sending device commands
- Responsive design with mobile support

## Data Flow

1. **GPS Data Ingestion**: GPS devices connect to Python TCP service via TCP sockets
2. **Protocol Processing**: Python service parses incoming GPS messages and stores data in MongoDB
3. **Command Execution**: Commands queued through web interface are sent to devices via TCP connection
4. **Real-time Updates**: Frontend queries backend APIs to display current vehicle status and tracking data
5. **Data Persistence**: All vehicle and command data stored in PostgreSQL, GPS coordinates in MongoDB

## External Dependencies

### Frontend Dependencies
- React ecosystem (React, React DOM, React Query)
- UI components from Radix UI primitives
- Form handling with React Hook Form
- Date manipulation with date-fns
- Styling with Tailwind CSS and class-variance-authority

### Backend Dependencies
- Express.js web framework
- PostgreSQL client via @neondatabase/serverless
- Drizzle ORM for database operations
- Session management with connect-pg-simple

### Python Service Dependencies
- AsyncIO for concurrent TCP handling
- Motor for MongoDB async operations
- Pydantic for data validation and modeling
- Python-dotenv for configuration management

## Deployment Strategy

The application is designed for containerized deployment:

### Development Environment
- Vite dev server for frontend with HMR
- TSX for TypeScript execution in development
- Environment-based configuration via .env files

### Production Build
- Frontend built as static assets via Vite
- Backend compiled to ESM bundle via esbuild
- Python service runs as standalone TCP server
- Database migrations handled via Drizzle Kit

### Infrastructure Requirements
- PostgreSQL database for application data
- MongoDB for GPS tracking data storage
- Network access for GPS devices to connect to TCP service
- Web server to serve frontend assets and API endpoints

The system is architected to handle multiple concurrent GPS device connections while providing a responsive web interface for monitoring and management. The separation of concerns between the web application and GPS protocol handling allows for independent scaling and maintenance of each component.