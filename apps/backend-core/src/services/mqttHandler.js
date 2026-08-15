const prisma = require('../config/db');

const handleIncomingMessage = async (topic, message) => {
    try {
        const payload = JSON.parse(message.toString());
        console.log(`\nData masuk [${topic}]:`, payload);
        
        const device = await prisma.devices.findUnique({
            where: { mqtt_client_id: payload.client_id }
        });

        if (!device) {
            console.log(`Perangkat dengan ID ${payload.client_id} tidak terdaftar di database.`);
            return;
        }

        for (const item of payload.data) {
            const sensor = await prisma.sensors.findFirst({
                where: { 
                    device_id: device.id, 
                    sensor_type: item.sensor_type 
                }
            });

            if (sensor) {
                const telemetryRecord = await prisma.telemetry_data.create({
                    data: {
                        time: payload.timestamp ? new Date(payload.timestamp) : new Date(),
                        sensor_id: sensor.id,
                        value: item.value
                    }
                });
                console.log(`[INFO] Tersimpan di DB: ${sensor.sensor_name} = ${item.value} ${sensor.unit}`);

                // 1. Panggil ML Service dari Backend Core (Internal Microservice Communication)
                let aiRecommendation = null;
                try {
                    const axios = require('axios');
                    const mlRes = await axios.post('http://localhost:8000/api/v1/ml/detect-anomaly', {
                        sensor_id: sensor.id,
                        device_name: device.device_name,
                        sensor_name: sensor.sensor_name,
                        value: item.value,
                        unit: sensor.unit
                    }, { timeout: 3000 });

                    if (mlRes.data && mlRes.data.is_anomaly) {
                        console.log(`[ALERT] ML Service mendeteksi anomali pada ${device.device_name}!`);
                        aiRecommendation = mlRes.data.ai_recommendation;
                    }
                } catch (mlErr) {
                    // Jika ML Service sedang offline, backend tetap berjalan lancar
                }

                // 2. Emit event real-time ke Socket.IO (Frontend menerima data telemetri + indikator anomali + AI Advisor dari backend)
                try {
                    const { getIO } = require('../config/socket');
                    const io = getIO();
                    const telemetryEvent = {
                        device_id: device.id,
                        client_id: device.mqtt_client_id,
                        device_name: device.device_name,
                        sensor_id: sensor.id,
                        sensor_name: sensor.sensor_name,
                        sensor_type: sensor.sensor_type,
                        value: item.value,
                        unit: sensor.unit,
                        time: telemetryRecord.time,
                        is_anomaly: !!aiRecommendation,
                        ai_recommendation: aiRecommendation
                    };

                    // Broadcast ke semua client via Backend Socket.IO
                    io.emit('realtime-telemetry', telemetryEvent);
                    io.to(`device_${device.id}`).emit('device-telemetry', telemetryEvent);
                } catch (socketErr) {
                    console.log('[WARN] Socket.IO emit skipped:', socketErr.message);
                }
            } else {
                console.log(`Sensor tipe '${item.sensor_type}' tidak ditemukan pada perangkat ini.`);
            }
        }
    } catch (error) {
        console.error('Gagal memproses payload MQTT:', error);
    }
};

module.exports = { handleIncomingMessage };