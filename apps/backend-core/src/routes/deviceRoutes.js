const express = require('express');
const router = express.Router();
const { getAllDevices, getDeviceTelemetry } = require('../controllers/deviceController');

router.get('/', getAllDevices);
router.get('/:id/telemetry', getDeviceTelemetry);

module.exports = router;