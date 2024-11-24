//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_NETWORKING_HH
#define JOKINOJO_NETWORKING_HH

#include <string>
#include <asio.hpp>

class Networking {
public:
    static Networking& get_instance();

    bool initialize();
    bool handleIncomingData();

    bool requestCreateRoom();
    bool requestJoinRoom(int roomId, std::string username);
    bool requestQuit();
    bool sendReadyStatus();

    bool sendChatMessage();
    bool sendFile(void* fileData);
    bool sendMediaStatus(bool isPaused, int timePosition);

    std::string get_ip();
    void set_ip(std::string ip);
    int get_port();
    void set_port(int port);

    asio::io_context* get_io_context();
    void set_io_context(asio::io_context* io_context);
    asio::ip::tcp::socket* get_socket();
    void set_socket(asio::ip::tcp::socket* socket);

private:
    std::string ip = "127.0.0.1";
    int port = 1234;
    asio::io_context* io_context;
    asio::ip::tcp::socket* socket;
};


#endif //JOKINOJO_NETWORKING_HH
