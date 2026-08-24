#include "SocketServer.hpp"
#include <iostream>
#include <cstring>
#include <thread>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <cstdlib>

SocketServer::SocketServer(int udpPort, int tcpPort) 
    : m_udpPort(udpPort), 
      m_tcpPort(tcpPort), 
      m_udpSocketFd(-1), 
      m_tcpSocketFd(-1),
      m_mqttHost("localhost"),
      m_mqttPort(1883),
      m_isRunning(false),
      m_totalPacketsReceived(0),
      m_totalBytesReceived(0),
      m_totalDecodeErrors(0) {}

SocketServer::~SocketServer() {
    stop();
}

bool SocketServer::start() {
    // 1. Setup UDP Socket (Port 8080)
    m_udpSocketFd = socket(AF_INET, SOCK_DGRAM, 0);
    if (m_udpSocketFd < 0) {
        std::cerr << "[ERROR] Failed to create UDP socket" << std::endl;
        return false;
    }

    int opt = 1;
    setsockopt(m_udpSocketFd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in udpAddr{};
    udpAddr.sin_family = AF_INET;
    udpAddr.sin_addr.s_addr = INADDR_ANY;
    udpAddr.sin_port = htons(m_udpPort);

    if (bind(m_udpSocketFd, (struct sockaddr*)&udpAddr, sizeof(udpAddr)) < 0) {
        std::cerr << "[ERROR] Failed to bind UDP socket to port " << m_udpPort << std::endl;
        close(m_udpSocketFd);
        return false;
    }

    // 2. Setup TCP Socket (Port 8081)
    m_tcpSocketFd = socket(AF_INET, SOCK_STREAM, 0);
    if (m_tcpSocketFd < 0) {
        std::cerr << "[ERROR] Failed to create TCP socket" << std::endl;
        close(m_udpSocketFd);
        return false;
    }

    setsockopt(m_tcpSocketFd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in tcpAddr{};
    tcpAddr.sin_family = AF_INET;
    tcpAddr.sin_addr.s_addr = INADDR_ANY;
    tcpAddr.sin_port = htons(m_tcpPort);

    if (bind(m_tcpSocketFd, (struct sockaddr*)&tcpAddr, sizeof(tcpAddr)) < 0) {
        std::cerr << "[ERROR] Failed to bind TCP socket to port " << m_tcpPort << std::endl;
        close(m_udpSocketFd);
        close(m_tcpSocketFd);
        return false;
    }

    if (listen(m_tcpSocketFd, 20) < 0) {
        std::cerr << "[ERROR] Failed to listen on TCP socket" << std::endl;
        close(m_udpSocketFd);
        close(m_tcpSocketFd);
        return false;
    }

    m_isRunning = true;
    std::cout << "[INFO] C++ UDP Gateway active on 0.0.0.0:" << m_udpPort << std::endl;
    std::cout << "[INFO] C++ TCP Gateway active on 0.0.0.0:" << m_tcpPort << std::endl;

    // Launch Listener Threads for UDP & TCP
    std::thread(&SocketServer::listenUdpLoop, this).detach();
    std::thread(&SocketServer::listenTcpLoop, this).detach();
    return true;
}

void SocketServer::stop() {
    if (m_isRunning) {
        m_isRunning = false;
        if (m_udpSocketFd >= 0) {
            close(m_udpSocketFd);
            m_udpSocketFd = -1;
        }
        if (m_tcpSocketFd >= 0) {
            close(m_tcpSocketFd);
            m_tcpSocketFd = -1;
        }
        std::cout << "[INFO] Dual UDP/TCP Gateway Servers stopped." << std::endl;
    }
}

bool SocketServer::publishToMqttBroker(const std::string& clientId, const std::string& jsonPayload) {
    // Sanitasi payload agar tidak merusak shell command
    std::string safeClientId = clientId;
    for (char &c : safeClientId) {
        if (!isalnum(c) && c != '_' && c != '-') c = '_';
    }

    // Command eksekusi aman via docker / mosquitto_pub
    std::string topic = "devices/" + safeClientId + "/telemetry";
    std::string cmd = "docker exec iot_mqtt_broker mosquitto_pub -h " + m_mqttHost + " -t \"" + topic + "\" -m '" + jsonPayload + "' > /dev/null 2>&1 &";
    int ret = std::system(cmd.c_str());
    return (ret == 0);
}

void SocketServer::printMetrics() const {
    std::cout << "\n--- [C++ GATEWAY METRICS SUMMARY] ---" << std::endl;
    std::cout << "Total Packets Received: " << m_totalPacketsReceived << std::endl;
    std::cout << "Total Bytes Received  : " << m_totalBytesReceived << " bytes" << std::endl;
    std::cout << "Total Decode Errors   : " << m_totalDecodeErrors << std::endl;
    std::cout << "------------------------------------\n" << std::endl;
}

void SocketServer::listenUdpLoop() {
    uint8_t buffer[2048];
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);

    while (m_isRunning) {
        ssize_t bytesRead = recvfrom(m_udpSocketFd, buffer, sizeof(buffer), 0, 
                                     (struct sockaddr*)&clientAddr, &clientLen);

        if (bytesRead > 0 && m_isRunning) {
            m_totalPacketsReceived++;
            m_totalBytesReceived += bytesRead;

            char clientIp[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(clientAddr.sin_addr), clientIp, INET_ADDRSTRLEN);

            std::cout << "[UDP RECEIVE] " << bytesRead << " bytes from " 
                      << clientIp << ":" << ntohs(clientAddr.sin_port) << std::endl;

            std::vector<uint8_t> rawBytes(buffer, buffer + bytesRead);
            DecodedTelemetry telemetry = m_decoder.decodeBinaryPayload(rawBytes);

            if (telemetry.isValid) {
                std::string jsonStr = m_decoder.toJsonString(telemetry);
                std::cout << "[UDP DECODED & MQTT PUBLISHING] " << jsonStr << std::endl;
                
                // Publish directly to MQTT Broker
                publishToMqttBroker(telemetry.client_id, jsonStr);
            } else {
                m_totalDecodeErrors++;
                std::cerr << "[UDP DECODE ERROR] " << telemetry.errorMessage << std::endl;
            }
        }
    }
}

void SocketServer::listenTcpLoop() {
    while (m_isRunning) {
        sockaddr_in clientAddr{};
        socklen_t clientLen = sizeof(clientAddr);
        int clientSocket = accept(m_tcpSocketFd, (struct sockaddr*)&clientAddr, &clientLen);

        if (clientSocket >= 0 && m_isRunning) {
            char clientIp[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(clientAddr.sin_addr), clientIp, INET_ADDRSTRLEN);

            // Handle TCP client connection in a separate worker thread
            std::thread(&SocketServer::handleTcpClient, this, clientSocket, std::string(clientIp)).detach();
        }
    }
}

void SocketServer::handleTcpClient(int clientSocket, std::string clientIp) {
    // Set TCP Recv Timeout (3 detik) untuk mencegah socket menggantung
    struct timeval tv;
    tv.tv_sec = 3;
    tv.tv_usec = 0;
    setsockopt(clientSocket, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));

    uint8_t buffer[2048];
    ssize_t bytesRead = recv(clientSocket, buffer, sizeof(buffer), 0);

    if (bytesRead > 0 && m_isRunning) {
        m_totalPacketsReceived++;
        m_totalBytesReceived += bytesRead;

        std::cout << "[TCP RECEIVE] " << bytesRead << " bytes from " << clientIp << std::endl;

        std::vector<uint8_t> rawBytes(buffer, buffer + bytesRead);
        DecodedTelemetry telemetry = m_decoder.decodeBinaryPayload(rawBytes);

        if (telemetry.isValid) {
            std::string jsonStr = m_decoder.toJsonString(telemetry);
            std::cout << "[TCP DECODED & MQTT PUBLISHING] " << jsonStr << std::endl;
            
            // Publish directly to MQTT Broker
            publishToMqttBroker(telemetry.client_id, jsonStr);
        } else {
            m_totalDecodeErrors++;
            std::cerr << "[TCP DECODE ERROR] " << telemetry.errorMessage << std::endl;
        }
    }

    close(clientSocket);
}
