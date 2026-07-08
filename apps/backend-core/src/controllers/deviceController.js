const prisma = require('../config/db');

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

module.exports = { getAllDevices, getDeviceTelemetry };