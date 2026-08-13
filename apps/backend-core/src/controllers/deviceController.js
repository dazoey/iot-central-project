const prisma = require('../config/db');
const mqttClient = require('../config/mqtt'); // Tambahkan import MQTT Client

const getAllDevices = async (req, res) => {
    try {
        const devices = await prisma.devices.findMany();
        res.json(devices);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getDeviceTelemetry = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const telemetry = await prisma.telemetry_data.findMany({
            where: { sensor: { device_id: deviceId } },
            include: { sensor: { select: { sensor_name: true, unit: true } } },
            orderBy: { time: 'desc' },
            take: 50
        });
        res.json(telemetry);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const sendCommand = async (req, res) => {
    try {
        const deviceId = parseInt(req.params.id);
        const { command, parameters } = req.body;

        const device = await prisma.devices.findUnique({
            where: { id: deviceId }
        });

        if (!device) {
            return res.status(404).json({ error: 'Perangkat tidak ditemukan' });
        }

        const topic = `devices/${device.mqtt_client_id}/control`;
        const payload = JSON.stringify({
            command: command,
            parameters: parameters || {},
            timestamp: new Date().toISOString()
        });

        mqttClient.publish(topic, payload, { qos: 1 }, async (err) => {
            if (err) {
                console.error('Gagal mengirim perintah MQTT:', err);
                return res.status(500).json({ error: 'Gagal mengirim perintah' });
            }

            await prisma.control_logs.create({
                data: {
                    device_id: device.id,
                    command: command,
                    status: 'sent'
                }
            });

            console.log(`Perintah terkirim ke [${topic}]:`, payload);
            res.json({ message: 'Perintah berhasil dikirim', topic, command });
        });

    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = { getAllDevices, getDeviceTelemetry, sendCommand };