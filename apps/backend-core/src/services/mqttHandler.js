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

                // Emit event real-time ke semua client WebSocket yang terhubung
                try {
                    const { getIO } = require('../config/socket');
                    const io = getIO();
                    io.emit('realtime-telemetry', {
                        device_id: device.id,
                        client_id: device.mqtt_client_id,
                        device_name: device.device_name,
                        sensor_id: sensor.id,
                        sensor_name: sensor.sensor_name,
                        sensor_type: sensor.sensor_type,
                        value: item.value,
                        unit: sensor.unit,
                        time: telemetryRecord.time
                    });
                } catch (socketErr) {
                    // Jika Socket.IO belum siap, log warning tanpa menghentikan proses DB
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