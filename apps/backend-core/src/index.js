const http = require('http');
const express = require('express');
const cors = require('cors');

// Import modul
const mqttClient = require('./config/mqtt');
const { handleIncomingMessage } = require('./services/mqttHandler');
const deviceRoutes = require('./routes/deviceRoutes');
const { initSocket } = require('./config/socket');

const app = express();
const server = http.createServer(app);
const PORT = 3000;

// Inisialisasi Socket.IO
initSocket(server);

app.use(cors());
app.use(express.json());

// mqtt listener initialization
mqttClient.on('connect', () => {
    console.log('[INFO] Terhubung ke MQTT Broker');
    mqttClient.subscribe('devices/+/telemetry', (err) => {
        if (!err) console.log('[INFO] Mendengarkan topik: devices/+/telemetry');
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

// start server HTTP + Socket.IO
server.listen(PORT, () => {
    console.log(`[INFO] Backend Core berjalan di http://localhost:${PORT}`);
});