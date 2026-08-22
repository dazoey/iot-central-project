#include "SocketServer.hpp"
#include <iostream>
#include <cstring>
#include <thread>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

SocketServer::SocketServer(int udpPort) 
    : m_udpPort(udpPort), m_socketFd(-1), m_isRunning(false) {}

SocketServer::~SocketServer() {
    stop();
}

bool SocketServer::start() {
    // Create UDP Socket
    m_socketFd = socket(AF_INET, SOCK_DGRAM, 0);
    if (m_socketFd < 0) {
        std::cerr << "[ERROR] Failed to create UDP socket" << std::endl;
        return false;
    }

    // Bind Socket to Port
    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(m_udpPort);

    if (bind(m_socketFd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        std::cerr << "[ERROR] Failed to bind UDP socket to port " << m_udpPort << std::endl;
        close(m_socketFd);
        return false;
    }

    m_isRunning = true;
    std::cout << "[INFO] C++ UDP Socket Gateway Server listening on 0.0.0.0:" << m_udpPort << std::endl;

    // Launch Listener Thread
    std::thread(&SocketServer::listenLoop, this).detach();
    return true;
}

void SocketServer::stop() {
    if (m_isRunning) {
        m_isRunning = false;
        if (m_socketFd >= 0) {
            close(m_socketFd);
            m_socketFd = -1;
        }
        std::cout << "[INFO] UDP Socket Server stopped." << std::endl;
    }
}

void SocketServer::listenLoop() {
    uint8_t buffer[2048];
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);

    while (m_isRunning) {
        ssize_t bytesRead = recvfrom(m_socketFd, buffer, sizeof(buffer), 0, 
                                     (struct sockaddr*)&clientAddr, &clientLen);

        if (bytesRead > 0 && m_isRunning) {
            char clientIp[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(clientAddr.sin_addr), clientIp, INET_ADDRSTRLEN);

            std::cout << "[UDP RECEIVE] Received " << bytesRead << " bytes from " 
                      << clientIp << ":" << ntohs(clientAddr.sin_port) << std::endl;

            // Convert to vector bytes
            std::vector<uint8_t> rawBytes(buffer, buffer + bytesRead);

            // Decode binary payload using C++ PayloadDecoder
            DecodedTelemetry telemetry = m_decoder.decodeBinaryPayload(rawBytes);

            if (telemetry.isValid) {
                std::string jsonStr = m_decoder.toJsonString(telemetry);
                std::cout << "[UDP DECODED] " << jsonStr << std::endl;
            } else {
                std::cerr << "[UDP DECODE ERROR] " << telemetry.errorMessage << std::endl;
            }
        }
    }
}
