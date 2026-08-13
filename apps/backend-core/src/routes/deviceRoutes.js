const express = require('express');
const router = express.Router();
const { getAllDevices, getDeviceTelemetry, sendCommand } = require('../controllers/deviceController');

router.get('/', getAllDevices);
router.get('/:id/telemetry', getDeviceTelemetry);
router.post('/:id/control', sendCommand); // Route untuk kontrol perangkat

module.exports = router;