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

// GET /api/v1/devices/:id (Detail 1 perangkat)
const getDeviceById = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const device = await prisma.devices.findUnique({
            where: { id: deviceId },
            include: { sensors: true }
        });

        if (!device) {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }

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
        const deviceId = parseInt(req.params.id);
        const limit = parseInt(req.query.limit) || 50;

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
    sendCommand
};