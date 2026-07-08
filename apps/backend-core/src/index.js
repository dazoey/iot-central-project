const express = require('express');
const cors = require('cors');

// Import modul yang sudah dipecah
const mqttClient = require('./config/mqtt');
const { handleIncomingMessage } = require('./services/mqttHandler');
const deviceRoutes = require('./routes/deviceRoutes');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// mqtt listener initialization
mqttClient.on('connect', () => {
    console.log('Terhubung ke MQTT Broker');
    mqttClient.subscribe('devices/+/telemetry', (err) => {
        if (!err) console.log('Mendengarkan topik: devices/+/telemetry');
    });
});

// setiap pesan masuk ke fungsi handler
mqttClient.on('message', handleIncomingMessage);

// api routes
app.get('/', (req, res) => {
    res.send('IoT Central API Running');
});

// Daftarkan route device
app.use('/api/v1/devices', deviceRoutes);

// start server
app.listen(PORT, () => {
    console.log(`Backend Core berjalan di http://localhost:${PORT}`);
});