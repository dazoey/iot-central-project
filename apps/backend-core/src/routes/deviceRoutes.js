const express = require('express');
const router = express.Router();
const {
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
    getAIAdvisorAnalysis
} = require('../controllers/deviceController');

// Device Routes
router.get('/', getAllDevices);
router.get('/:id', getDeviceById);
router.post('/', createDevice);
router.put('/:id', updateDevice);
router.delete('/:id', deleteDevice);

// Sensor Routes
router.post('/:id/sensors', addSensorToDevice);
router.put('/:id/sensors/:sensorId', updateSensor);
router.delete('/:id/sensors/:sensorId', deleteSensor);

// Telemetry, Control, & AI Advisor Routes
router.get('/:id/telemetry', getDeviceTelemetry);
router.post('/:id/control', sendCommand);
router.get('/:id/ai-advisor', getAIAdvisorAnalysis);

module.exports = router;