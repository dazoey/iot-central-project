const express = require('express');
const router = express.Router();
const prisma = require('../config/db');
const axios = require('axios');

/**
 * POST /api/v1/lora/uplink
 * Endpoint Webhook listener untuk event Uplink dari ChirpStack (LoRaWAN Network Server).
 * Format Payload ChirpStack Uplink v4:
 * {
 *   "deviceInfo": {
 *     "devEui": "0102030405060708",
 *     "deviceName": "LoRa Soil Moisture Sensor"
 *   },
 *   "object": {
 *     "temperature": 27.5,
 *     "humidity": 60.0
 *   }
 * }
 */
router.post('/uplink', async (req, res) => {
    try {
        const { deviceInfo, object } = req.body;

        if (!deviceInfo || !deviceInfo.devEui) {
            return res.status(400).json({ error: 'Payload LoRaWAN tidak valid. deviceInfo.devEui wajib ada.' });
        }

        const devEui = deviceInfo.devEui;
        console.log(`[LORA UPLINK] Menerima data LoRaWAN dari DevEUI: ${devEui}`);

        // 1. Cari perangkat di database berdasarkan dev_eui
        let device = await prisma.devices.findUnique({
            where: { dev_eui: devEui },
            include: { sensors: true }
        });

        // Jika perangkat belum ada di DB, daftarkan otomatis (Auto-Provisioning)
        if (!device) {
            console.log(`[LORA AUTO-PROVISION] Mendaftarkan perangkat LoRaWAN baru: ${deviceInfo.deviceName || devEui}`);
            device = await prisma.devices.create({
                data: {
                    device_name: deviceInfo.deviceName || `LoRa Device ${devEui}`,
                    protocol: 'LoRaWAN',
                    dev_eui: devEui,
                    status: 'online'
                },
                include: { sensors: true }
            });
        }

        // 2. Proses pembacaan sensor dari object telemetry payload
        if (object && typeof object === 'object') {
            for (const [sensorType, value] of Object.entries(object)) {
                if (typeof value !== 'number') continue;

                // Cari atau buat sensor untuk tipe ini
                let sensor = device.sensors.find(s => s.sensor_type === sensorType);
                if (!sensor) {
                    sensor = await prisma.sensors.create({
                        data: {
                            device_id: device.id,
                            sensor_name: `LoRa ${sensorType}`,
                            sensor_type: sensorType,
                            unit: sensorType === 'temperature' ? '°C' : (sensorType === 'humidity' ? '%' : 'unit')
                        }
                    });
                    device.sensors.push(sensor);
                }

                // 3. Simpan data telemetri ke TimescaleDB
                await prisma.telemetry_data.create({
                    data: {
                        time: new Date(),
                        sensor_id: sensor.id,
                        value: parseFloat(value)
                    }
                });

                console.log(`[LORA TELEMETRY STORED] Device ID ${device.id} | Sensor: ${sensorType} | Value: ${value}`);

                // 4. Deteksi anomali via ML Service secara asynchronous
                axios.post('http://localhost:8000/api/v1/ml/detect-anomaly', {
                    sensor_id: sensor.id,
                    device_name: device.device_name,
                    sensor_name: sensor.sensor_name,
                    value: parseFloat(value),
                    unit: sensor.unit
                }, { timeout: 3000 }).catch(err => {
                    console.log('[WARN] Async ML check skipped for LoRaWAN:', err.message);
                });
            }
        }

        res.json({ status: 'success', message: 'LoRaWAN Uplink berhasil diproses', dev_eui: devEui });

    } catch (error) {
        console.error('[ERROR] LoRaWAN Uplink Controller:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
