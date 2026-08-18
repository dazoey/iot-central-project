const prisma = require('../config/db');

// --- DEVICE CONTROLLERS ---

// GET /api/v1/devices (List semua perangkat beserta sensor-nya)
const getAllDevices = async (req, res) => {
    try {
        const devices = await prisma.devices.findMany({
            include: {
                sensors: true
            },
            orderBy: { id: 'desc' }
        });
        res.json(devices);
    } catch (error) {
        console.error('[ERROR] getAllDevices:', error);
        res.status(500).json({ error: error.message });
    }
};

// Helper untuk menyelesaikan deviceId dari Integer ID maupun mqtt_client_id string
const resolveDeviceId = async (paramId) => {
    let deviceId = parseInt(paramId);
    if (isNaN(deviceId)) {
        const device = await prisma.devices.findUnique({
            where: { mqtt_client_id: paramId }
        });
        if (!device) return null;
        return device.id;
    }
    return deviceId;
};

// GET /api/v1/devices/:id (Detail 1 perangkat)
const getDeviceById = async (req, res) => {
    try {
        const deviceId = await resolveDeviceId(req.params.id);
        if (!deviceId) {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }

        const device = await prisma.devices.findUnique({
            where: { id: deviceId },
            include: { sensors: true }
        });

        res.json(device);
    } catch (error) {
        console.error('[ERROR] getDeviceById:', error);
        res.status(500).json({ error: error.message });
    }
};

// POST /api/v1/devices (Tambah perangkat baru)
const createDevice = async (req, res) => {
    try {
        const { device_name, protocol, dev_eui, mqtt_client_id } = req.body;

        if (!device_name || !protocol) {
            return res.status(400).json({ error: 'device_name dan protocol wajib diisi' });
        }

        const newDevice = await prisma.devices.create({
            data: {
                device_name,
                protocol,
                dev_eui: dev_eui || null,
                mqtt_client_id: mqtt_client_id || null,
                status: 'offline'
            }
        });

        console.log(`[INFO] Device baru ditambahkan: ${newDevice.device_name} (ID: ${newDevice.id})`);
        res.status(201).json(newDevice);
    } catch (error) {
        console.error('[ERROR] createDevice:', error);
        if (error.code === 'P2002') {
            return res.status(400).json({ error: 'mqtt_client_id atau dev_eui sudah digunakan' });
        }
        res.status(500).json({ error: error.message });
    }
};

// PUT /api/v1/devices/:id (Update perangkat)
const updateDevice = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const { device_name, protocol, dev_eui, mqtt_client_id, status } = req.body;

        const updatedDevice = await prisma.devices.update({
            where: { id: deviceId },
            data: {
                ...(device_name && { device_name }),
                ...(protocol && { protocol }),
                ...(dev_eui !== undefined && { dev_eui }),
                ...(mqtt_client_id !== undefined && { mqtt_client_id }),
                ...(status && { status })
            }
        });

        console.log(`[INFO] Device ID ${deviceId} diperbarui`);
        res.json(updatedDevice);
    } catch (error) {
        console.error('[ERROR] updateDevice:', error);
        if (error.code === 'P2025') {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }
        res.status(500).json({ error: error.message });
    }
};

// DELETE /api/v1/devices/:id (Hapus perangkat)
const deleteDevice = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        await prisma.devices.delete({
            where: { id: deviceId }
        });

        console.log(`[INFO] Device ID ${deviceId} telah dihapus`);
        res.json({ message: `Perangkat ID ${deviceId} berhasil dihapus` });
    } catch (error) {
        console.error('[ERROR] deleteDevice:', error);
        if (error.code === 'P2025') {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }
        res.status(500).json({ error: error.message });
    }
};

// --- SENSOR CONTROLLERS ---

// POST /api/v1/devices/:id/sensors (Tambah sensor ke perangkat)
const addSensorToDevice = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const { sensor_name, sensor_type, unit } = req.body;

        if (!sensor_name || !sensor_type || !unit) {
            return res.status(400).json({ error: 'sensor_name, sensor_type, dan unit wajib diisi' });
        }

        const device = await prisma.devices.findUnique({ where: { id: deviceId } });
        if (!device) {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }

        const newSensor = await prisma.sensors.create({
            data: {
                device_id: deviceId,
                sensor_name,
                sensor_type,
                unit
            }
        });

        console.log(`[INFO] Sensor ${sensor_name} ditambahkan ke Device ID ${deviceId}`);
        res.status(201).json(newSensor);
    } catch (error) {
        console.error('[ERROR] addSensorToDevice:', error);
        res.status(500).json({ error: error.message });
    }
};

// DELETE /api/v1/devices/:id/sensors/:sensorId (Hapus sensor dari perangkat)
const deleteSensor = async (req, res) => {
    try {
        const sensorId = parseInt(req.params.sensorId);

        await prisma.sensors.delete({
            where: { id: sensorId }
        });

        console.log(`[INFO] Sensor ID ${sensorId} dihapus`);
        res.json({ message: `Sensor ID ${sensorId} berhasil dihapus` });
    } catch (error) {
        console.error('[ERROR] deleteSensor:', error);
        if (error.code === 'P2025') {
            return res.status(404).json({ error: 'Sensor tidak ditemukan' });
        }
        res.status(500).json({ error: error.message });
    }
};

// --- TELEMETRY & CONTROL CONTROLLERS ---

// GET /api/v1/devices/:id/telemetry (Ambil data telemetri historis)
const getDeviceTelemetry = async (req, res) => {
    try {
        const paramId = req.params.id;
        const limit = parseInt(req.query.limit) || 50;

        // Cari ID perangkat berdasarkan integer ID atau mqtt_client_id
        let deviceId = parseInt(paramId);
        if (isNaN(deviceId)) {
            const device = await prisma.devices.findUnique({
                where: { mqtt_client_id: paramId }
            });
            if (!device) {
                return res.status(404).json({ error: `Perangkat '${paramId}' tidak ditemukan` });
            }
            deviceId = device.id;
        }

        const telemetry = await prisma.telemetry_data.findMany({
            where: { sensors: { device_id: deviceId } },
            include: { sensors: { select: { sensor_name: true, sensor_type: true, unit: true } } },
            orderBy: { time: 'desc' },
            take: limit
        });
        res.json(telemetry);
    } catch (error) {
        console.error('[ERROR] getDeviceTelemetry:', error);
        res.status(500).json({ error: error.message });
    }
};

// PUT /api/v1/devices/:id/sensors/:sensorId (Update sensor)
const updateSensor = async (req, res) => {
    try {
        const sensorId = parseInt(req.params.sensorId);
        const { sensor_name, sensor_type, unit } = req.body;

        const updatedSensor = await prisma.sensors.update({
            where: { id: sensorId },
            data: {
                ...(sensor_name && { sensor_name }),
                ...(sensor_type && { sensor_type }),
                ...(unit && { unit })
            }
        });

        console.log(`[INFO] Sensor ID ${sensorId} diperbarui`);
        res.json(updatedSensor);
    } catch (error) {
        console.error('[ERROR] updateSensor:', error);
        if (error.code === 'P2025') {
            return res.status(404).json({ error: 'Sensor tidak ditemukan' });
        }
        res.status(500).json({ error: error.message });
    }
};

// POST /api/v1/devices/:id/control (Kirim perintah kontrol MQTT)
const sendCommand = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const { command, parameters } = req.body;

        if (!command) {
            return res.status(400).json({ error: 'command wajib diisi' });
        }

        const mqttClient = require('../config/mqtt');

        const device = await prisma.devices.findUnique({
            where: { id: deviceId }
        });

        if (!device) {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }

        const topic = `devices/${device.mqtt_client_id || device.id}/control`;
        const payload = JSON.stringify({
            command: command,
            parameters: parameters || {},
            timestamp: new Date().toISOString()
        });

        mqttClient.publish(topic, payload, { qos: 1 }, async (err) => {
            if (err) {
                console.error('[ERROR] Gagal mengirim perintah MQTT:', err);
                return res.status(500).json({ error: 'Gagal mengirim perintah ke broker MQTT' });
            }

            const controlLog = await prisma.control_logs.create({
                data: {
                    device_id: device.id,
                    command: command,
                    status: 'sent'
                }
            });

            // Broadcast real-time log ke Socket.IO
            try {
                const { getIO } = require('../config/socket');
                const io = getIO();
                io.emit('control-log', {
                    id: controlLog.id,
                    device_id: device.id,
                    device_name: device.device_name,
                    command: command,
                    status: 'sent',
                    timestamp: new Date().toISOString()
                });
            } catch (socketErr) {
                console.log('[WARN] Socket.IO control-log emit skipped:', socketErr.message);
            }

            console.log(`[INFO] Perintah terkirim ke [${topic}]:`, payload);
            res.json({ message: 'Perintah berhasil dikirim', topic, command });
        });

    } catch (error) {
        console.error('[ERROR] sendCommand:', error);
        res.status(500).json({ error: error.message });
    }
};

// GET /api/v1/devices/:id/ai-advisor (Minta saran AI Advisor langsung dari Backend)
const getAIAdvisorAnalysis = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const { sensor_id } = req.query;

        const device = await prisma.devices.findUnique({
            where: { id: deviceId },
            include: { sensors: true }
        });

        if (!device) {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }

        // Cari sensor terkait atau ambil sensor pertama
        const targetSensor = sensor_id 
            ? device.sensors.find(s => s.id === parseInt(sensor_id))
            : device.sensors[0];

        if (!targetSensor) {
            return res.status(404).json({ error: 'Sensor tidak ditemukan pada perangkat ini' });
        }

        // Ambil bacaan telemetri terakhir
        const lastTelemetry = await prisma.telemetry_data.findFirst({
            where: { sensor_id: targetSensor.id },
            orderBy: { time: 'desc' }
        });

        const currentValue = lastTelemetry ? lastTelemetry.value : 0.0;

        // Panggil ML Service
        const axios = require('axios');
        const mlRes = await axios.post('http://localhost:8000/api/v1/ml/detect-anomaly', {
            sensor_id: targetSensor.id,
            device_name: device.device_name,
            sensor_name: targetSensor.sensor_name,
            value: currentValue,
            unit: targetSensor.unit
        }, { timeout: 4000 });

        res.json({
            device_id: device.id,
            device_name: device.device_name,
            sensor_name: targetSensor.sensor_name,
            current_value: currentValue,
            unit: targetSensor.unit,
            is_anomaly: mlRes.data.is_anomaly,
            ai_recommendation: mlRes.data.ai_recommendation
        });
    } catch (error) {
        console.error('[ERROR] getAIAdvisorAnalysis:', error.message);
        res.status(500).json({ error: 'Gagal mendapatkan analisa AI Advisor' });
    }
};

// GET /api/v1/devices/:id/sensors/:sensorId/forecast (Prediksi tren telemetri mendatang + TTV)
const getDeviceTelemetryForecast = async (req, res) => {
    try {
        const sensorId = parseInt(req.params.sensorId);
        const steps = parseInt(req.query.steps) || 5;
        const threshold = req.query.threshold ? parseFloat(req.query.threshold) : null;
        const lowerThreshold = req.query.lower_threshold ? parseFloat(req.query.lower_threshold) : null;

        // Panggil ML Service
        const axios = require('axios');
        const mlRes = await axios.post('http://localhost:8000/api/v1/ml/predict-telemetry', {
            sensor_id: sensorId,
            steps_ahead: steps,
            critical_threshold: threshold,
            lower_critical_threshold: lowerThreshold
        }, { timeout: 4000 });

        res.json(mlRes.data);
    } catch (error) {
        console.error('[ERROR] getDeviceTelemetryForecast:', error.message);
        res.status(500).json({ error: 'Gagal mendapatkan prediksi telemetri' });
    }
};

// GET /api/v1/devices/:id/sensors/:sensorId/health (Evaluasi Indeks Kesehatan Perangkat)
const getDeviceHealthIndex = async (req, res) => {
    try {
        const sensorId = parseInt(req.params.sensorId);
        const minVal = req.query.min ? parseFloat(req.query.min) : null;
        const maxVal = req.query.max ? parseFloat(req.query.max) : null;

        // Panggil ML Service
        const axios = require('axios');
        const mlRes = await axios.post('http://localhost:8000/api/v1/ml/device-health', {
            sensor_id: sensorId,
            normal_min: minVal,
            normal_max: maxVal
        }, { timeout: 4000 });

        res.json(mlRes.data);
    } catch (error) {
        console.error('[ERROR] getDeviceHealthIndex:', error.message);
        res.status(500).json({ error: 'Gagal mengevaluasi kesehatan perangkat' });
    }
};

// GET /api/v1/devices/:id/sensors/:sensorId/rul (Estimasi Sisa Usia Pakai / RUL)
const getDeviceRULPrediction = async (req, res) => {
    try {
        const sensorId = parseInt(req.params.sensorId);
        const lifespanDays = req.query.lifespan_days ? parseFloat(req.query.lifespan_days) : 365.0;

        // 1. Dapatkan dulu skor kesehatan saat ini
        const axios = require('axios');
        const healthRes = await axios.post('http://localhost:8000/api/v1/ml/device-health', {
            sensor_id: sensorId
        }, { timeout: 4000 });

        const currentHealth = healthRes.data ? healthRes.data.health_score : 100.0;

        // 2. Panggil RUL Predictor Engine
        const mlRes = await axios.post('http://localhost:8000/api/v1/ml/predict-rul', {
            sensor_id: sensorId,
            current_health_score: currentHealth,
            expected_lifespan_days: lifespanDays
        }, { timeout: 4000 });

        res.json(mlRes.data);
    } catch (error) {
        console.error('[ERROR] getDeviceRULPrediction:', error.message);
        res.status(500).json({ error: 'Gagal memprediksi sisa usia pakai (RUL) perangkat' });
    }
};

module.exports = {
    getAllDevices,
    getDeviceById,
    createDevice,
    updateDevice,
    deleteDevice,
    addSensorToDevice,
    updateSensor,
    deleteSensor,
    getDeviceTelemetry,
    sendCommand,
    getAIAdvisorAnalysis,
    getDeviceTelemetryForecast,
    getDeviceHealthIndex,
    getDeviceRULPrediction
};