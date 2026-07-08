const mqtt = require('mqtt');
const mqttClient = mqtt.connect('mqtt://localhost:1883');

module.exports = mqttClient;