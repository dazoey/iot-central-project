# Comprehensive System Testing Guide
**IoT Central Management System**

This document provides step-by-step instructions for testing all microservices and features of the **IoT Central Management System**, including Docker infrastructure, C++ Network Service, Python ML Service, and Node.js Backend Core REST APIs.

---

## 1. Environment Setup

### A. Start Docker Infrastructure (Database and MQTT Broker)
Open a terminal in the root directory (`iot-central-project`) and run:
```bash
docker-compose up -d
```
> **Verification:**
> Run `docker ps`. The following containers must be active: `iot_postgres` (Port 5432), `iot_mqtt_broker` (Port 1883/9001), and `iot_redis` (Port 6379).

---

### B. Start Python Machine Learning Service (Port 8000)
Open a new terminal in `services/ml-service`:
```bash
cd services/ml-service
./venv/bin/python3 main.py
```
> ML Service will listen on `http://localhost:8000` with the 24-hour Auto-Retraining Background Scheduler active.

---

### C. Start C++ Network Protocol Service (Port 8080 UDP / 8081 TCP)
Open a new terminal in `services/network-service`:
```bash
cd services/network-service
./build/network_service
```
> C++ Network Service will listen on `0.0.0.0:8080` (UDP) and `0.0.0.0:8081` (TCP).

---

### D. Start Node.js Backend Core (Port 3000)
Open a new terminal in `apps/backend-core`:
```bash
cd apps/backend-core
npm start
```
> Backend Core will listen on `http://localhost:3000` and connect to Socket.IO, MQTT, & ML Service.

---

## 2. Step-by-Step Test Scenarios

---

### SCENARIO 1: Native MQTT Data Ingestion and AI Anomaly Detection

Use `docker exec` commands to simulate hardware sensors publishing data over MQTT:

#### 1. Normal Telemetry Data Test (Room Temperature 25.5 C)
```bash
docker exec iot_mqtt_broker mosquitto_pub \
  -t "devices/DEV_TEST_01/telemetry" \
  -m '{"client_id":"DEV_TEST_01","data":[{"sensor_type":"temperature","value":25.5}]}'
```
- **Expected Outcome**: Backend stores data in TimescaleDB (`is_anomaly: false`).

#### 2. Extreme Anomaly Test and Gemini AI Advisor Diagnosis (Spike to 95.0 C)
```bash
docker exec iot_mqtt_broker mosquitto_pub \
  -t "devices/DEV_TEST_01/telemetry" \
  -m '{"client_id":"DEV_TEST_01","data":[{"sensor_type":"temperature","value":95.0}]}'
```
- **Expected Outcome**:
  - Z-Score ML detects anomaly ($Z > 3.0$).
  - Gemini AI Advisor produces structured JSON (`problem` and `solution`).
  - Result is broadcasted real-time over Socket.IO.

---

### SCENARIO 2: C++ Dual-Protocol Network Service (UDP and TCP Binary Payloads)

Test C++ Payload Decoder converting raw binary hardware bytes to JSON:

#### 1. UDP Binary Payload Test (Port 8080)
Run Python UDP test script:
```bash
python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# DEV_TEST_01, sensor temperature (01), value 28.5 C (IEEE 754 float: 41e40000)
payload = bytes.fromhex('000B4445565F544553545F30310141e40000')
s.sendto(payload, ('127.0.0.1', 8080))
print('Sent 18 bytes UDP binary payload')
"
```
- **Expected Outcome**: C++ log displays `[UDP DECODED & MQTT PUBLISHING]` and forwards JSON to Mosquitto MQTT Broker.

#### 2. TCP Binary Payload Test (Port 8081)
Run Python TCP test script:
```bash
python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8081))
# DEV_TEST_01, sensor humidity (02), value 65.0 % (IEEE 754 float: 42820000)
payload = bytes.fromhex('000B4445565F544553545F30310242820000')
s.sendall(payload)
s.close()
print('Sent 18 bytes TCP binary payload')
"
```
- **Expected Outcome**: C++ log displays `[TCP DECODED & MQTT PUBLISHING]`.

---

### SCENARIO 3: LoRaWAN ChirpStack Webhook and Auto-Provisioning

Simulate ChirpStack v4 LoRaWAN Network Server sending an Uplink Webhook event:

```bash
curl -s -X POST http://localhost:3000/api/v1/lora/uplink \
  -H "Content-Type: application/json" \
  -d '{
    "deviceInfo": {
      "devEui": "0102030405060708",
      "deviceName": "LoRa Soil Moisture Sensor 01"
    },
    "object": {
      "temperature": 27.5,
      "humidity": 62.0
    }
  }'
```
- **Expected Outcome**:
  - Backend automatically registers device and sensors (Auto-Provisioning).
  - Returns `{"status":"success","message":"LoRaWAN Uplink berhasil diproses"}`.

---

### SCENARIO 4: Advanced Machine Learning Features via REST API

Use `curl` or Postman to test ML capabilities:

#### 1. Telemetry Forecasting and Time-to-Threshold-Violation (TTV)
```bash
curl -s "http://localhost:3000/api/v1/devices/2/sensors/2/forecast?steps=5&threshold=85.0"
```
- **Output**: N-step future projection, 95% Confidence Interval (`lower_bound` / `upper_bound`), and TTV estimation.

#### 2. Device Health Index (DHI) Evaluation
```bash
curl -s "http://localhost:3000/api/v1/devices/2/sensors/2/health?min=20.0&max=30.0"
```
- **Output**: Health score (0% - 100%), status color (`green`, `yellow`, `red`), and penalty breakdown.

#### 3. Remaining Useful Life (RUL) Prediction Engine
```bash
curl -s "http://localhost:3000/api/v1/devices/2/sensors/2/rul?lifespan_days=365"
```
- **Output**: Estimated remaining operational days and hours before failure.

#### 4. Auto Maintenance Schedule and Work Order Generator
```bash
curl -s "http://localhost:3000/api/v1/devices/2/sensors/2/maintenance-schedule"
```
- **Output**: Recommended maintenance date (`recommended_maintenance_date`), priority level, and Work Order object.

#### 5. Trigger Auto-Retraining Pipeline
```bash
curl -s -X POST http://localhost:8000/api/v1/ml/trigger-auto-retrain
```
- **Output**: Retrains Isolation Forest models for active sensors using latest TimescaleDB records.

---

### SCENARIO 5: MQTT Remote Control Downlink Command

Send a control command to a device from Backend Core:

```bash
curl -s -X POST http://localhost:3000/api/v1/devices/2/control \
  -H "Content-Type: application/json" \
  -d '{
    "command": "RELAY_ON",
    "parameters": { "pin": 4 }
  }'
```
- **Expected Outcome**:
  - Message published to MQTT topic `devices/<mqtt_client_id>/control`.
  - Log saved to DB `control_logs` and broadcasted over Socket.IO.
