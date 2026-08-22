#ifndef SOCKET_SERVER_HPP
#define SOCKET_SERVER_HPP

#include <string>
#include <vector>
#include <atomic>
#include "PayloadDecoder.hpp"

class SocketServer {
public:
    SocketServer(int udpPort = 8080, const std::string& backendUrl = "http://localhost:3000");
    ~SocketServer();

    /**
     * Starts UDP Socket Server loop in a non-blocking / multithreaded manner
     */
    bool start();

    /**
     * Stops the UDP Socket Server
     */
    void stop();

    /**
     * Helper to forward decoded JSON telemetry directly to Backend Core / MQTT Broker
     */
    bool forwardToBackend(const std::string& jsonPayload);

private:
    int m_udpPort;
    int m_socketFd;
    std::string m_backendUrl;
    std::atomic<bool> m_isRunning;
    PayloadDecoder m_decoder;

    void listenLoop();
};

#endif // SOCKET_SERVER_HPP
