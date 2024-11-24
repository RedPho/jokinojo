//
// Created by emin on 31.10.2024.
//

#include "Networking.hh"
#include <asio.hpp>
#include <iostream>
#include <thread>
#include <network.pb.h>

Networking& Networking::get_instance(){
    static Networking n;
    return n;
}

bool Networking::initialize() {
    using asio::ip::tcp;
    Networking networker = get_instance();
    networker.set_io_context(new asio::io_context());

    networker.set_socket(new tcp::socket(*networker.get_io_context()));
    while (true) {
        try {
            tcp::resolver resolver(*networker.get_io_context());
            tcp::resolver::results_type endpoints = resolver.resolve(networker.get_ip(), std::to_string(port));
            asio::connect(*networker.get_socket(), endpoints);
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
    networkData.set_datatype(jokinojo::RequestData_DataType_JOIN_ROOM);
    networkData.set_roomid(roomId);
    networkData.set_username(username);
    asio::write(*socket, asio::buffer(&networkData, sizeof(networkData)), error);
    return true;
}

