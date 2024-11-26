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

    bool requestCreateRoom(const std::string username);
    bool requestJoinRoom(int roomId, const std::string username);
    bool requestQuit();
    bool sendReadyStatus();

    bool sendChatMessage();
    bool sendFile(void* fileData);
    bool sendMediaStatus(int timePosition, bool isPaused);

    std::string get_ip() {
        return m_ip;
    }
    void set_ip(std::string ip) {
        m_ip = ip;
    }
    int get_port() {
        return m_port;
    }
    void set_port(int port) {
        m_port = port;
    }

    asio::io_context* get_io_context() {
        return m_io_context;
    }
    void set_io_context(asio::io_context* io_context){
        m_io_context = io_context;
    }
    asio::ip::tcp::socket* get_socket() {
        return m_socket;
    }
    void set_socket(asio::ip::tcp::socket* socket) {
        m_socket = socket;
    }

private:
    std::string m_ip = "127.0.0.1";
    int m_port = 1234;
    asio::io_context* m_io_context;
    asio::ip::tcp::socket* m_socket;
};


#endif //JOKINOJO_NETWORKING_HH
