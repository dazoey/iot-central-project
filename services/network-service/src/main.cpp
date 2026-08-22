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

    // 2. Start UDP Socket Gateway Server on Port 8080
    SocketServer udpServer(8080);
    if (udpServer.start()) {
        std::cout << "[INFO] UDP Gateway Active on Port 8080. Press Ctrl+C or kill to stop." << std::endl;
    } else {
        std::cerr << "[FATAL] Failed to start UDP Socket Gateway!" << std::endl;
        return 1;
    }

    // Keep main thread alive for server loop
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    return 0;
}
