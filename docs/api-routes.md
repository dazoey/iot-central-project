# API Documentation and Testing Reference
**IoT Central Management System**

Comprehensive list of all REST API Endpoints available in this system for manual testing via Postman or cURL.

---

## 1. Backend Core Endpoints (Port 3000)
> **Base URL**: `http://localhost:3000`

### A. Core and Device Management

#### 1. Server Health / Root Check
- **Method**: `GET`
- **URL**: `http://localhost:3000/`
- **Description**: Verifies if the Backend Core service is active.

#### 2. Get All Devices
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices`
- **Description**: Retrieves all IoT devices along with their attached sensors.

#### 3. Get Device by ID or Client ID
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id`
- **Examples**:
  - `http://localhost:3000/api/v1/devices/2`
  - `http://localhost:3000/api/v1/devices/DEV_TEST_01`
  - `http://localhost:3000/api/v1/devices/0102030405060708`
- **Description**: Retrieves details for a specific device using DB integer ID, Client ID string, or LoRaWAN DevEUI string.

#### 4. Create New Device
- **Method**: `POST`
- **URL**: `http://localhost:3000/api/v1/devices`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "device_name": "Main Water Tank Sensor",
    "protocol": "MQTT",
    "mqtt_client_id": "ULTRASONIC_TANK_01"
  }
  ```

#### 5. Update Device
- **Method**: `PUT`
- **URL**: `http://localhost:3000/api/v1/devices/:id`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "device_name": "Main Water Tank Sensor (Updated)",
    "status": "online"
  }
  ```

#### 6. Delete Device
- **Method**: `DELETE`
- **URL**: `http://localhost:3000/api/v1/devices/:id`
- **Description**: Deletes a device and all associated sensors.

---

### B. Sensor Management

#### 7. Add Sensor to Device
- **Method**: `POST`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "sensor_name": "Water Level Sensor",
    "sensor_type": "distance",
    "unit": "cm"
  }
  ```

#### 8. Update Sensor
- **Method**: `PUT`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "sensor_name": "Calibrated Water Level Sensor",
    "unit": "cm"
  }
  ```

#### 9. Delete Sensor
- **Method**: `DELETE`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId`

---

### C. Telemetry, Remote Control, LoRaWAN, and AI/ML Integrations

#### 10. Get Device Telemetry History
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/telemetry?limit=50`

#### 11. Send MQTT Control Command
- **Method**: `POST`
- **URL**: `http://localhost:3000/api/v1/devices/:id/control`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "command": "PUMP_ON",
    "parameters": { "speed": 80 }
  }
  ```

#### 12. LoRaWAN ChirpStack Webhook Uplink Listener
- **Method**: `POST`
- **URL**: `http://localhost:3000/api/v1/lora/uplink`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "deviceInfo": {
      "devEui": "0102030405060708",
      "deviceName": "LoRa Soil Moisture Sensor 01"
    },
    "object": {
      "temperature": 27.5,
      "humidity": 62.0
    }
  }
  ```

#### 13. Query AI LLM Diagnostic Advisor
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/ai-advisor`
- **Description**: Fetches Gemini AI diagnostics (`problem` and `solution`) for latest telemetry.

#### 14. Telemetry Forecasting and Time-to-Threshold-Violation (TTV)
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/forecast?steps=5&threshold=85.0&lower_threshold=10.0`
- **Description**: Predicts N steps ahead, 95% Confidence Intervals, and critical threshold violation time.

#### 15. Device Health Index (DHI) Evaluation
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/health?min=20.0&max=35.0`
- **Description**: Evaluates overall device health score (0% - 100%), status color, and penalty breakdown.

#### 16. Remaining Useful Life (RUL) Prediction
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/rul?lifespan_days=365`
- **Description**: Estimates remaining operational lifespan in days and hours before failure.

#### 17. Auto Maintenance Schedule and Work Order Generator
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/maintenance-schedule`
- **Description**: Generates recommended maintenance date, priority level, and Work Order object.

---

## 2. Internal Machine Learning Service Endpoints (Port 8000)
> **Base URL**: `http://localhost:8000` *(FastAPI Microservice)*

#### 18. Health Check
- **Method**: `GET`
- **URL**: `http://localhost:8000/health`

#### 19. Anomaly Detection and AI Advisor
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/detect-anomaly`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "device_name": "Room Temperature Sensor",
    "sensor_name": "Temperature Sensor",
    "value": 92.5,
    "unit": "°C",
    "history_values": [25.0, 25.2, 25.1, 24.9, 25.3]
  }
  ```

#### 20. Trigger Auto-Retraining Pipeline
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/trigger-auto-retrain`
- **Description**: Triggers an immediate ML model retraining cycle in the background.

#### 21. Predict Telemetry Forecasting and TTV
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/predict-telemetry`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "steps_ahead": 5,
    "critical_threshold": 85.0,
    "lower_critical_threshold": 10.0,
    "history_values": [78.0, 76.0, 74.0, 72.0, 70.0]
  }
  ```

#### 22. Device Health Evaluation
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/device-health`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "recent_anomalies_count": 1,
    "normal_min": 20.0,
    "normal_max": 30.0,
    "history_values": [25.0, 25.5, 26.0, 32.0, 25.1]
  }
  ```

#### 23. RUL Prediction
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/predict-rul`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "current_health_score": 76.3,
    "expected_lifespan_days": 365.0,
    "health_score_history": [100.0, 95.0, 90.0, 82.0, 76.3]
  }
  ```

#### 24. Auto Maintenance Scheduler
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/schedule-maintenance`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "device_name": "Room Temperature Sensor 1",
    "sensor_name": "Temperature Sensor",
    "health_score": 65.0,
    "rul_days": 12.0,
    "recent_anomalies_count": 2,
    "trend_direction": "increasing"
  }
  ```
