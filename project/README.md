# VigilanceOS (Python Version)

A full-stack, real-time device monitoring and anomaly detection platform built with modern technologies.

## 🚀 Features

- **Real-time Device Monitoring** - <br> Live telemetry data streaming via WebSockets
- **ML-Powered Anomaly Detection** - Smart fault detection using machine learning
- **Admin Portal** - React-based dashboard with live charts and device management
- **JWT Authentication** - Enterprise-grade security with RBAC
- **Audit Logging** - Complete action tracking for compliance
- **Dockerized Microservices** - Production-ready containerized architecture
- **PostgreSQL Database** - Robust data persistence with migrations
- **Real-time Alerts** - Slack/Email notifications for critical events

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Portal  │    │   Backend API   │    │  Anomaly ML     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (Python)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, WebSockets, JWT
- **Frontend**: React, Recharts, WebSocket Client
- **Database**: PostgreSQL with Alembic migrations
- **ML**: Scikit-learn for anomaly detection
- **Infrastructure**: Docker, Nginx, Docker Compose

## 🚀 Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd vigilance-os-python
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Admin Portal: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Default admin: admin@vigilance.com / admin123

## 📊 Database Schema

- **admins** - User management with RBAC
- **devices** - Device registry with location and thresholds
- **telemetry** - Real-time sensor data
- **anomalies** - ML-detected issues
- **audit_logs** - Complete action tracking

## 🔧 Development

### Backend Setup
```bash
cd backend-api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd admin-portal
npm install
npm start
```

### Database Migrations
```bash
cd backend-api
alembic upgrade head
```

## 🧪 Testing

```bash
# Backend tests
cd backend-api
pytest

# Frontend tests
cd admin-portal
npm test
```

## 📈 Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: System dashboards
- **Health Checks**: Automated monitoring

## 🔐 Security

- JWT authentication with RS256 signing
- Role-based access control (RBAC)
- Audit logging for all actions
- Input validation and sanitization

## 📱 API Endpoints

- `POST /auth/login` - User authentication
- `GET /devices` - Device listing
- `POST /telemetry` - Submit device data
- `WS /ws` - Real-time data streaming
- `GET /anomalies` - Anomaly reports

## 🎯 Production Deployment

The platform is designed for enterprise deployment with:
- Horizontal scaling capabilities
- Load balancing with Nginx
- Database connection pooling
- Comprehensive logging
- Health monitoring

