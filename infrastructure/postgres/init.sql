-- 1. Tabel Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabel Devices
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    protocol VARCHAR(20) NOT NULL,
    dev_eui VARCHAR(16) UNIQUE,
    mqtt_client_id VARCHAR(50) UNIQUE,
    status VARCHAR(20) DEFAULT 'offline',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabel Sensors
CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(id) ON DELETE CASCADE,
    sensor_name VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    unit VARCHAR(10) NOT NULL
);

-- 4. Tabel Telemetry Data (Time-Series)
CREATE TABLE telemetry_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT REFERENCES sensors(id) ON DELETE CASCADE,
    value DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('telemetry_data', 'time');

-- 5. Tabel Control Logs
CREATE TABLE control_logs (
    id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(id) ON DELETE CASCADE,
    command VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    executed_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);