# IoT Central Management System

An enterprise-grade, microservice-based centralized system for real-time IoT device monitoring, high-throughput protocol parsing, machine learning anomaly detection, predictive maintenance, and remote device control.

---

## 1. System Architecture

The project consists of three core microservices working alongside distributed database and messaging infrastructure:

- **Backend Core (`apps/backend-core`)**: Node.js Express REST API, Prisma ORM, Socket.IO real-time event broadcasting, MQTT ingestion handler, and LoRaWAN webhook endpoints.
- **Machine Learning Service (`services/ml-service`)**: Python FastAPI microservice providing Z-Score & Isolation Forest Anomaly Detection, Google Gemini AI LLM Advisor, Telemetry Forecasting with 95% Confidence Intervals, Device Health Index (DHI) Evaluation, Remaining Useful Life (RUL) Prediction, Auto Maintenance Scheduler, and an Automated 24-Hour Retraining Pipeline.
- **Network Protocol Service (`services/network-service`)**: High-performance C++17 gateway providing a multithreaded Dual-Protocol UDP (Port 8080) and TCP (Port 8081) listener, custom binary payload decoding, packet throughput metrics tracking, and direct MQTT broker publishing.
- **Infrastructure (`infrastructure/`)**: TimescaleDB (PostgreSQL 15 extension for time-series telemetry data), Eclipse Mosquitto MQTT Broker, Redis 7 cache, and ChirpStack v4 LoRaWAN Network Server configuration.

---

## 2. Tech Stack

| Service / Layer | Technology Stack |
|---|---|
| **Database** | PostgreSQL 15 + TimescaleDB extension |
| **Backend Core** | Node.js (CommonJS), Express, Prisma ORM (v5), Socket.IO |
| **Machine Learning** | Python 3.10+, FastAPI, Scikit-Learn, NumPy, Pandas, Google Gemini API, APScheduler |
| **Network Gateway** | C++17, AppleClang / GCC, CMake, POSIX Sockets |
| **Messaging & Cache** | Eclipse Mosquitto MQTT Broker, Redis 7 |
| **LoRaWAN Server** | ChirpStack v4 |

---

## 3. Quick Start Guide

### Prerequisites
- Docker Desktop installed and running
- Node.js (v20+)
- Python 3.10+
- CMake & C++17 compiler (GCC / Clang)

### 1. Launch Docker Infrastructure
```bash
docker-compose up -d
```
*Starts PostgreSQL (TimescaleDB), Mosquitto MQTT Broker, and Redis in the background.*

### 2. Start Machine Learning Service
```bash
cd services/ml-service
./venv/bin/python3 main.py
```
*Listens on `http://localhost:8000` with background auto-retraining active.*

### 3. Start C++ Network Protocol Service
```bash
cd services/network-service
rm -rf build && mkdir build && cd build && cmake .. && make
./network_service
```
*Listens on UDP `0.0.0.0:8080` and TCP `0.0.0.0:8081`.*

### 4. Start Backend Core Service
```bash
cd apps/backend-core
npm start
```
*Listens on `http://localhost:3000` and connects to Socket.IO, MQTT, & ML Service.*

---

## 4. Documentation References

Comprehensive technical documentation and manual testing guides are available in the `docs/` directory:

- **API Routes Reference**: [`docs/api-routes.md`](docs/api-routes.md)
- **Step-by-Step Testing Guide**: [`docs/testing-guide.md`](docs/testing-guide.md)

---

## 5. Key Features Summary

- **Multi-Protocol Telemetry Ingestion**: Native MQTT, LoRaWAN ChirpStack Webhooks with Auto-Provisioning, and C++ UDP/TCP Binary Payloads.
- **AI Diagnostics**: Google Gemini LLM integration providing structured problem and solution analysis for telemetry anomalies.
- **Predictive Maintenance**: 95% CI Telemetry Forecasting, Time-to-Threshold-Violation (TTV) alerts, Device Health Index (0-100%), RUL lifespan estimation, and automated Work Order generation.
- **Automatic Model Retraining**: Periodic 24-hour background scheduler continuously updating Isolation Forest models from TimescaleDB historical records.
