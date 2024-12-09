//
// Created by emin on 31.10.2024.
//

#include "Networker.hh"
#include <asio.hpp>
#include <iostream>
#include <thread>
#include <network.pb.h>
using asio::ip::tcp;

Networker& Networker::get_instance(){
    static Networker n;
    return n;
}

bool Networker::initialize(std::string ip, int port) {
    Networker& networker = get_instance();

    while (true) {
        try {
            tcp::resolver resolver(m_io_context);
            // Resolve the server's IP address and port
            tcp::resolver::results_type endpoints = resolver.resolve(ip, std::to_string(port));

            // Perform synchronous connection
            asio::connect(m_socket, endpoints);

            std::cout << "Connected to server\n";
            return true;
        } catch (const std::exception& e) {
            std::cerr << "Failed to connect: " << e.what() << "\n";
            std::cout << "Reconnecting in 5 seconds...\n";
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
    }

    return false;
}

bool Networker::handleIncomingData(){
    std::cout << "handlingIncomingData" << "\n";
    char data[1024];
    if (!m_socket.is_open()) {
        std::cerr << "Socket is not open.\n";
        return false;
    }
    while (true) {
        try{
            std::cout << "trying to read" << "\n";
            std::size_t bytesRead = m_socket.read_some(asio::buffer(data, sizeof(data)));
            std::string receivedData(data, bytesRead);
            std::cout << bytesRead << "bytes and the data: " << receivedData << "\n";
            jokinojo::ResponseData responseData;
            responseData.ParseFromString(receivedData);
            if (m_dataCallback) {
                m_dataCallback(responseData);
            }
        } catch  (std::exception& e) {
            std::cerr << "Connection lost: " << e.what() << "\n";
        }
    }
}

bool Networker::requestJoinRoom(int roomId, std::string username) {
    jokinojo::RequestData networkData;
    std::error_code error;

    // Set data in the protobuf object
    networkData.set_datatype(jokinojo::RequestData_DataType_JOIN_ROOM);
    networkData.set_roomid(roomId);
    networkData.set_username(username);

    // Serialize the Protobuf object into a string
    std::string serializedData;
    if (!networkData.SerializeToString(&serializedData)) {
        std::cerr << "Failed to serialize Protobuf object.\n";
        return false;
    }


    // Send the serialized data
    asio::write(m_socket, asio::buffer(serializedData), error);
    if (error) {
        std::cerr << "Failed to send serialized data: " << error.message() << "\n";
        return false;
    }

    return true;
}



bool Networker::requestCreateRoom(std::string username) {
    jokinojo::RequestData networkData;
    std::error_code error;
    networkData.set_datatype(jokinojo::RequestData_DataType_CREATE_ROOM);
    networkData.set_username(username);

    std::string serializedData;
    if (!networkData.SerializeToString(&serializedData)) {
        std::cerr << "Failed to serialize data." << std::endl;
        return false;
    }

    asio::write(m_socket, asio::buffer(serializedData), error);

    if (error) {
        std::cerr << "Failed to send data: " << error.message() << std::endl;
        return false;
    }
    return true;
}

