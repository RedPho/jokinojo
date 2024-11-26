//
// Created by emin on 31.10.2024.
//

#include "Networking.hh"
#include <asio.hpp>
#include <iostream>
#include <thread>
#include <network.pb.h>
using asio::ip::tcp;

Networking& Networking::get_instance(){
    static Networking n;
    return n;
}

bool Networking::initialize() {
    Networking& networker = get_instance(); // Assuming get_instance() returns a reference

    // Create and store io_context and socket locally (or manage via member variables)
    asio::io_context asio_io_context;
    tcp::socket socket(asio_io_context);

    // Set the io_context and socket in the Networking instance
    networker.set_io_context(&asio_io_context);
    networker.set_socket(&socket);

    while (true) {
        try {
            tcp::resolver resolver(asio_io_context);
            // Resolve the server's IP address and port
            tcp::resolver::results_type endpoints = resolver.resolve(m_ip, std::to_string(m_port));

            // Perform synchronous connection
            asio::connect(socket, endpoints);

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


bool Networking::requestJoinRoom(int roomId, std::string username) {
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

    // Send the size of the serialized data first (optional, helps receiver know the size)
    uint32_t size = htonl(serializedData.size());
    asio::write(*m_socket, asio::buffer(&size, sizeof(size)), error);
    if (error) {
        std::cerr << "Failed to send data size: " << error.message() << "\n";
        return false;
    }

    // Send the serialized data
    asio::write(*m_socket, asio::buffer(serializedData), error);
    if (error) {
        std::cerr << "Failed to send serialized data: " << error.message() << "\n";
        return false;
    }

    return true;
}



bool Networking::requestCreateRoom(std::string username) {
    jokinojo::RequestData networkData;
    std::error_code error;
    networkData.set_datatype(jokinojo::RequestData_DataType_CREATE_ROOM);
    networkData.set_username(username);
    asio::write(*m_socket, asio::buffer(&networkData, sizeof(networkData)), error);
    return true;
}

