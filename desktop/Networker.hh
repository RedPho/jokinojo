//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_NETWORKER_HH
#define JOKINOJO_NETWORKER_HH

#include <string>
#include <asio.hpp>

class Networker {
public:
    static Networker& get_instance();

    bool initialize(std::string ip, int port);
    bool handleIncomingData();

    bool requestCreateRoom(const std::string username);
    bool requestJoinRoom(int roomId, const std::string username);
    bool requestQuit();
    bool sendReadyStatus();

    bool sendChatMessage();
    bool sendFile(void* fileData);
    bool sendMediaStatus(int timePosition, bool isPaused);

private:
    asio::io_context m_io_context;
    asio::ip::tcp::socket m_socket;
    Networker() : m_socket(m_io_context) {}
    ~Networker() = default;

    // Delete copy constructor and assignment operator to prevent copying
    Networker(const Networker&) = delete;
    Networker& operator=(const Networker&) = delete;
};


#endif //JOKINOJO_NETWORKER_HH
