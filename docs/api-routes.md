# API Documentation & Postman Testing Guide
**IoT Central Management System**

Panduan lengkap seluruh REST API Endpoints yang tersedia pada sistem ini untuk pengujian manual via Postman / cURL.

---

## 🟢 1. Backend Core Endpoints (Port 3000)
> **Base URL**: `http://localhost:3000`

### A. Core & Device Management

#### 1. Server Health / Root Check
- **Method**: `GET`
- **URL**: `http://localhost:3000/`
- **Description**: Mengecek apakah Backend Core berjalan aktif.

#### 2. Get All Devices
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices`
- **Description**: Mengambil semua daftar perangkat IoT beserta sensor-sensor yang terpasang.

#### 3. Get Device by ID / Client ID
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id`
- **Examples**:
  - `http://localhost:3000/api/v1/devices/2`
  - `http://localhost:3000/api/v1/devices/DEV_TEST_01`
- **Description**: Mengambil detail 1 perangkat spesifik menggunakan ID angka DB atau Client ID String.

#### 4. Create New Device
- **Method**: `POST`
- **URL**: `http://localhost:3000/api/v1/devices`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "device_name": "Sensor Tangki Air Utama",
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
    "device_name": "Sensor Tangki Air Utama (Updated)",
    "status": "online"
  }
  ```

#### 6. Delete Device
- **Method**: `DELETE`
- **URL**: `http://localhost:3000/api/v1/devices/:id`
- **Description**: Menghapus perangkat beserta relasi sensornya.

---

### B. Sensor Management

#### 7. Add Sensor to Device
- **Method**: `POST`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:
  ```json
  {
    "sensor_name": "Sensor Ketinggian Air",
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
    "sensor_name": "Sensor Ketinggian Air Kalibrasi",
    "unit": "cm"
  }
  ```

#### 9. Delete Sensor
- **Method**: `DELETE`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId`

---

### C. Telemetry, Control, & AI/ML Integrations

#### 10. Get Device Telemetry History
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/telemetry?limit=50`
- **Examples**:
  - `http://localhost:3000/api/v1/devices/DEV_TEST_01/telemetry?limit=20`

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

#### 12. Query AI LLM Diagnostic Advisor
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/ai-advisor`
- **Description**: Mengambil diagnosa AI Gemini (problem & solution) untuk kondisi sensor terkini.

#### 13. Telemetry Forecasting & Time-to-Threshold-Violation (TTV)
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/forecast?steps=5&threshold=85.0&lower_threshold=10.0`
- **Description**: Memprediksi angka telemetri N langkah ke depan, 95% Confidence Intervals, dan estimasi waktu pelanggaran batas kritis.

#### 14. Device Health Index (DHI) Evaluation
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/health?min=20.0&max=35.0`
- **Description**: Mengevaluasi skor kesehatan perangkat (0% - 100%), status warna, dan rincian penalti.

#### 15. Remaining Useful Life (RUL) Prediction
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/rul?lifespan_days=365`
- **Description**: Memprediksi sisa usia operasional perangkat dalam hari/jam sebelum mengalami kerusakan.

#### 16. Auto Maintenance Schedule & Work Order
- **Method**: `GET`
- **URL**: `http://localhost:3000/api/v1/devices/:id/sensors/:sensorId/maintenance-schedule`
- **Description**: Menghasilkan rekomendasi tanggal perawatan dan Work Order teknis otomatis.

---

## 🔵 2. Internal Machine Learning Service Endpoints (Port 8000)
> **Base URL**: `http://localhost:8000` *(FastAPI Microservice)*

#### 17. Health Check
- **Method**: `GET`
- **URL**: `http://localhost:8000/health`

#### 18. Anomaly Detection + AI Advisor
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/detect-anomaly`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "device_name": "Sensor Suhu Ruangan",
    "sensor_name": "Temperature Sensor",
    "value": 92.5,
    "unit": "°C",
    "history_values": [25.0, 25.2, 25.1, 24.9, 25.3]
  }
  ```

#### 19. Predict Telemetry Forecasting & TTV
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

#### 20. Device Health Evaluation
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

#### 21. RUL Prediction
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

#### 22. Auto Maintenance Scheduler
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/schedule-maintenance`
- **Body (JSON)**:
  ```json
  {
    "sensor_id": 2,
    "device_name": "Sensor Suhu Ruangan 1",
    "sensor_name": "Temperature Sensor",
    "health_score": 65.0,
    "rul_days": 12.0,
    "recent_anomalies_count": 2,
    "trend_direction": "increasing"
  }
  ```
