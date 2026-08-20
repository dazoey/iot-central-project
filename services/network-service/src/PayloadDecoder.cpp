#include "PayloadDecoder.hpp"
#include <sstream>
#include <iomanip>
#include <cstring>
#include <iostream>

PayloadDecoder::PayloadDecoder() {}
PayloadDecoder::~PayloadDecoder() {}

std::vector<uint8_t> PayloadDecoder::hexToBytes(const std::string& hex) {
    std::vector<uint8_t> bytes;
    for (size_t i = 0; i < hex.length(); i += 2) {
        std::string byteString = hex.substr(i, 2);
        uint8_t byte = (uint8_t) strtol(byteString.c_str(), NULL, 16);
        bytes.push_back(byte);
    }
    return bytes;
}

DecodedTelemetry PayloadDecoder::decodeBinaryPayload(const std::vector<uint8_t>& rawBytes) {
    DecodedTelemetry result;
    result.isValid = false;

    if (rawBytes.size() < 7) {
        result.errorMessage = "Payload size too small (minimum 7 bytes required)";
        return result;
    }

    // 1. Read Client ID length (2 bytes, big-endian)
    uint16_t idLen = (static_cast<uint16_t>(rawBytes[0]) << 8) | rawBytes[1];

    if (rawBytes.size() < 2 + idLen + 1 + 4) {
        result.errorMessage = "Invalid payload length matching client_id size";
        return result;
    }

    // 2. Read Client ID string
    result.client_id = std::string(reinterpret_cast<const char*>(&rawBytes[2]), idLen);

    size_t offset = 2 + idLen;

    // 3. Read Sensor Type Code
    uint8_t sensorCode = rawBytes[offset];
    offset += 1;

    switch (sensorCode) {
        case 1: result.sensor_type = "temperature"; break;
        case 2: result.sensor_type = "humidity"; break;
        case 3: result.sensor_type = "distance"; break;
        case 4: result.sensor_type = "voltage"; break;
        default: result.sensor_type = "generic_sensor"; break;
    }

    // 4. Read Float Value (4 bytes IEEE 754)
    uint32_t rawValue = (static_cast<uint32_t>(rawBytes[offset]) << 24) |
                        (static_cast<uint32_t>(rawBytes[offset + 1]) << 16) |
                        (static_cast<uint32_t>(rawBytes[offset + 2]) << 8) |
                        (static_cast<uint32_t>(rawBytes[offset + 3]));

    float floatVal;
    std::memcpy(&floatVal, &rawValue, sizeof(floatVal));
    result.value = static_cast<double>(floatVal);
    result.isValid = true;

    return result;
}

DecodedTelemetry PayloadDecoder::decodeHexString(const std::string& hexStr) {
    std::vector<uint8_t> bytes = hexToBytes(hexStr);
    return decodeBinaryPayload(bytes);
}

std::string PayloadDecoder::toJsonString(const DecodedTelemetry& telemetry) {
    if (!telemetry.isValid) {
        return "{\"error\":\"" + telemetry.errorMessage + "\"}";
    }

    std::stringstream ss;
    ss << std::fixed << std::setprecision(2);
    ss << "{"
       << "\"client_id\":\"" << telemetry.client_id << "\","
       << "\"data\":[{"
       << "\"sensor_type\":\"" << telemetry.sensor_type << "\","
       << "\"value\":" << telemetry.value
       << "}]"
       << "}";

    return ss.str();
}
