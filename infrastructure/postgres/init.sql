CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    protocol VARCHAR(20) NOT NULL,
    dev_eui VARCHAR(16) UNIQUE,
    mqtt_client_id VARCHAR(50) UNIQUE,
    status VARCHAR(20) DEFAULT 'offline',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(id) ON DELETE CASCADE,
    sensor_name VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    unit VARCHAR(10) NOT NULL
);

CREATE TABLE telemetry_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT REFERENCES sensors(id) ON DELETE CASCADE,
    value DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('telemetry_data', 'time');

CREATE TABLE control_logs (
    id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(id) ON DELETE CASCADE,
    command VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    executed_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);