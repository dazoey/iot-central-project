#include <iostream>
#include "PayloadDecoder.hpp"

int main() {
    std::cout << "[INFO] Network Protocol Service (C++) Started" << std::endl;

    PayloadDecoder decoder;

    // Contoh Hex payload mentah dari hardware sensor:
    // "000B4445565F544553545F30310141e80000"
    // 000B -> Client ID length = 11 ("DEV_TEST_01")
    // 4445565F544553545F3031 -> "DEV_TEST_01"
    // 01 -> Sensor Type (1: temperature)
    // 41e80000 -> IEEE 754 Float 29.0
    std::string sampleHexPayload = "000B4445565F544553545F30310141e80000";

    std::cout << "[INFO] Testing C++ Binary Payload Decoder..." << std::endl;
    std::cout << "[INFO] Input Hex Payload: " << sampleHexPayload << std::endl;

    DecodedTelemetry result = decoder.decodeHexString(sampleHexPayload);

    if (result.isValid) {
        std::cout << "[SUCCESS] Decoded JSON Output: " << decoder.toJsonString(result) << std::endl;
    } else {
        std::cout << "[ERROR] Decoding Failed: " << result.errorMessage << std::endl;
    }

    std::cout << "[INFO] Network Protocol Service C++ Core Ready." << std::endl;
    return 0;
}
