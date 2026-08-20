#ifndef PAYLOAD_DECODER_HPP
#define PAYLOAD_DECODER_HPP

#include <string>
#include <vector>
#include <cstdint>

// Structure representing parsed IoT sensor data
struct DecodedTelemetry {
    std::string client_id;
    std::string sensor_type;
    double value;
    bool isValid;
    std::string errorMessage;
};

class PayloadDecoder {
public:
    PayloadDecoder();
    ~PayloadDecoder();

    /**
     * Decodes raw binary / hex payload bytes from hardware sensors
     * Format byte stream:
     * [Byte 0-1]: Client ID length (uint16)
     * [Byte 2..N]: Client ID string
     * [Byte N+1]: Sensor type ID (1: Temp, 2: Humidity, 3: Distance/Ultrasonic, 4: Voltage)
     * [Byte N+2..N+5]: Float Value (IEEE 754 Big-Endian / 4 bytes)
     */
    DecodedTelemetry decodeBinaryPayload(const std::vector<uint8_t>& rawBytes);

    /**
     * Decodes hex string format (e.g. "000544455630310141e40000")
     */
    DecodedTelemetry decodeHexString(const std::string& hexStr);

    /**
     * Serializes decoded telemetry structure to JSON string for Backend Core consumption
     */
    std::string toJsonString(const DecodedTelemetry& telemetry);

private:
    std::vector<uint8_t> hexToBytes(const std::string& hex);
};

#endif // PAYLOAD_DECODER_HPP
