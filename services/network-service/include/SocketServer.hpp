#ifndef SOCKET_SERVER_HPP
#define SOCKET_SERVER_HPP

#include <string>
#include <vector>
#include <atomic>
#include "PayloadDecoder.hpp"

class SocketServer {
public:
    SocketServer(int udpPort = 8080, int tcpPort = 8081);
    ~SocketServer();

    /**
     * Starts Dual UDP & TCP Socket Server loops in a non-blocking / multithreaded manner
     */
    bool start();

    /**
     * Stops UDP & TCP Socket Servers
     */
    void stop();

    /**
     * Helper to publish decoded JSON telemetry directly to MQTT Broker via Mosquitto CLI
     */
    bool publishToMqttBroker(const std::string& clientId, const std::string& jsonPayload);

    /**
     * Print Server Metrics & Throughput Statistics
     */
    void printMetrics() const;

private:
    int m_udpPort;
    int m_tcpPort;
    int m_udpSocketFd;
    int m_tcpSocketFd;
    std::string m_mqttHost;
    int m_mqttPort;

    std::atomic<bool> m_isRunning;
    std::atomic<uint64_t> m_totalPacketsReceived;
    std::atomic<uint64_t> m_totalBytesReceived;
    std::atomic<uint64_t> m_totalDecodeErrors;

    PayloadDecoder m_decoder;

    void listenUdpLoop();
    void listenTcpLoop();
    void handleTcpClient(int clientSocket, std::string clientIp);
};

#endif // SOCKET_SERVER_HPP
