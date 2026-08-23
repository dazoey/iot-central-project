#include <iostream>
#include <thread>
#include <chrono>
#include "PayloadDecoder.hpp"
#include "SocketServer.hpp"

int main() {
    std::cout << "==================================================" << std::endl;
    std::cout << "[INFO] Network Protocol Service (C++) Starting..." << std::endl;
    std::cout << "==================================================" << std::endl;

    // 1. Test Static Hex Decoder
    PayloadDecoder decoder;
    std::string sampleHexPayload = "000B4445565F544553545F30310141e80000";
    DecodedTelemetry result = decoder.decodeHexString(sampleHexPayload);

    if (result.isValid) {
        std::cout << "[SELF-TEST] Decoded JSON: " << decoder.toJsonString(result) << std::endl;
    } else {
        std::cerr << "[SELF-TEST ERROR] Decoding Failed: " << result.errorMessage << std::endl;
    }

    // 2. Start Dual UDP (8080) & TCP (8081) Socket Gateway Server
    SocketServer gatewayServer(8080, 8081);
    if (gatewayServer.start()) {
        std::cout << "[INFO] Dual Gateway Active: UDP (Port 8080) | TCP (Port 8081)." << std::endl;
        std::cout << "[INFO] Direct MQTT Publishing Target: Mosquitto (Port 1883)." << std::endl;
    } else {
        std::cerr << "[FATAL] Failed to start Dual Socket Gateway!" << std::endl;
        return 1;
    }

    // Keep main thread alive & print metrics every 30 seconds
    int loopCount = 0;
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        loopCount++;
        if (loopCount % 30 == 0) {
            gatewayServer.printMetrics();
        }
    }

    return 0;
}
