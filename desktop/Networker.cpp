//
// Created by emin on 31.10.2024.
//

#include "Networker.hh"
#include <asio.hpp>
#include <iostream>
#include <thread>
#include <network.pb.h>
using asio::ip::tcp;

Networker::Networker() = default;

Networker::~Networker() {
    cleanup();
}

bool Networker::initialize(std::string ip, int port) {
    cleanup(); // Cleanup any existing connection

    try {
        tcp::resolver resolver(m_io_context);
        tcp::resolver::results_type endpoints = resolver.resolve(ip, std::to_string(port));

        asio::connect(m_socket, endpoints);

        // Start network thread
        m_networkThread = std::thread(&Networker::handleIncomingData, this);

        std::cout << "Connected to server\n";
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Failed to connect: " << e.what() << "\n";
        return false;
    }
}

void Networker::handleIncomingData() {
    std::cout << "handlingIncomingData" << "\n";
    if (!m_socket.is_open()) {
        std::cerr << "Socket is not open.\n";
        return;
    }

    while (true) {
        try {
            char data[1024];
            if (!m_socket.is_open()) break;

            std::cout << "trying to read" << "\n";
            std::size_t bytesRead = m_socket.read_some(asio::buffer(data, sizeof(data)));

            std::string receivedData(data, bytesRead);
            std::cout << bytesRead << "bytes and the data: " << receivedData << "\n";

            jokinojo::ResponseData responseData;
            if (responseData.ParseFromString(receivedData)) {
                if (m_dataCallback) {
                    m_dataCallback(responseData);
                }
            }
        } catch (std::exception& e) {
            std::cerr << "Connection lost: " << e.what() << "\n";
            return;
        }
    }
}

bool Networker::requestJoinRoom(int roomId, std::string username) {
    jokinojo::RequestData networkData;

    // Set data in the protobuf object
    networkData.set_datatype(jokinojo::RequestData_DataType_JOIN_ROOM);
    networkData.set_roomid(roomId);
    networkData.set_username(username);

    return serializeAndSendData(networkData);
}



bool Networker::requestCreateRoom(std::string username) {
    jokinojo::RequestData networkData;
    networkData.set_datatype(jokinojo::RequestData_DataType_CREATE_ROOM);
    networkData.set_username(username);

    return serializeAndSendData(networkData);

}

bool Networker::sendMediaStatus(int timePosition, bool isPaused) {
    jokinojo::RequestData networkData;

    networkData.set_datatype(jokinojo::RequestData_DataType_SYNC);
    networkData.set_timeposition(timePosition); // miliseconds
    networkData.set_resumed(!isPaused);

    return serializeAndSendData(networkData);
}

bool Networker::sendFileName(std::string fileName) {
    jokinojo::RequestData networkData;
    networkData.set_datatype(jokinojo::RequestData_DataType_VIDEO_NAME);
    networkData.set_videoname(fileName);
    return serializeAndSendData(networkData);
}

bool Networker::requestQuit() {
    jokinojo::RequestData networkData;
    networkData.set_datatype(jokinojo::RequestData_DataType_QUIT);
    serializeAndSendData(networkData);
    m_socket.close();
    return true;
}

bool Networker::sendReadyStatus() {
    jokinojo::RequestData networkData;
    networkData.set_datatype(jokinojo::RequestData_DataType_READY);
    return serializeAndSendData(networkData);
}

bool Networker::sendChatMessage(std::string message) {
    jokinojo::RequestData networkData;
    networkData.set_datatype(jokinojo::RequestData_DataType_CHAT);
    networkData.set_chatmessage(message);
    return serializeAndSendData(networkData);
}

bool Networker::serializeAndSendData(jokinojo::RequestData networkData) {
    std::string serializedData;
    if (!networkData.SerializeToString(&serializedData)) {
        std::cerr << "Failed to serialize data." << std::endl;
        return false;
    }

    std::error_code error;
    asio::write(m_socket, asio::buffer(serializedData), error);
    if (error) {
        std::cerr << "Failed to send data: " << error.message() << std::endl;
        return false;
    }
    return true;
}

void Networker::cleanup() {

    if (m_socket.is_open()) {
        std::error_code ec;
        m_socket.shutdown(asio::ip::tcp::socket::shutdown_both, ec);
        m_socket.close();
    }

    m_io_context.stop();

    // Join the thread if it's running
    if (m_networkThread.joinable()) {
        m_networkThread.join();
    }

    // Reset io_context to allow reuse
    m_io_context.restart();
}