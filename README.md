# Smart Home Energy Monitoring with Conversational AI

A modern platform for monitoring and understanding home energy consumption through natural language queries and interactive visualizations.

## Quick Start with Docker 🚀

The easiest way to run the application is using Docker. All prerequisites are handled automatically.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-home-energy-monitoring.git
   cd smart-home-energy-monitoring
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your OpenAI API key for the chat service.

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Generate sample data (optional):
   ```bash
   # This will run inside a temporary container
   docker-compose run --rm telemetry python /app/scripts/simulate_telemetry.py
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - API Documentation:
     - Auth Service: http://localhost:8000/docs
     - Telemetry Service: http://localhost:8001/docs
     - Chat Service: http://localhost:8002/docs

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f auth
docker-compose logs -f telemetry
docker-compose logs -f chat

# Stop all services
docker-compose down

# Rebuild services after changes
docker-compose up -d --build

# Remove all containers and volumes
docker-compose down -v
```

## System Architecture

The application consists of the following services:

- **Frontend** (Port 3000)
  - React application with Material-UI
  - Real-time charts and device management
  - Natural language query interface

- **Auth Service** (Port 8000)
  - User registration and authentication
  - JWT token management
  - Role-based access control

- **Telemetry Service** (Port 8001)
  - Device telemetry ingestion
  - Time-series data storage
  - Device management

- **Chat Service** (Port 8002)
  - Natural language query processing
  - Energy consumption analytics
  - OpenAI integration

- **PostgreSQL** (Port 5432)
  - Persistent data storage
  - Shared database for all services

## Development

### Running Tests

```bash
# Using Docker
docker-compose run --rm auth pytest
docker-compose run --rm telemetry pytest
docker-compose run --rm chat pytest
docker-compose run --rm frontend npm test
```

### API Documentation

Interactive API documentation is available through Swagger UI:
- Auth Service: http://localhost:8000/docs
- Telemetry Service: http://localhost:8001/docs
- Chat Service: http://localhost:8002/docs

## Features

- 🔐 Secure user authentication with JWT
- 📊 Real-time energy consumption monitoring
- 💬 Natural language queries about energy usage
- 📱 Responsive Material-UI design
- 📈 Interactive charts and statistics
- 🤖 AI-powered insights
- 🔄 Real-time data updates

## License

MIT

## Acknowledgments

- OpenAI for LLM integration capabilities
- FastAPI for the excellent Python web framework
- React team for the frontend framework 