//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_NETWORKER_HH
#define JOKINOJO_NETWORKER_HH

#include <string>
#include <asio.hpp>
#include <network.pb.h>

class Networker {
public:
    void setDataCallback(std::function<void(jokinojo::ResponseData)> callback) {
        m_dataCallback = callback;
    }

    static Networker& get_instance();

    bool initialize(std::string ip, int port);
    bool handleIncomingData();

    bool requestCreateRoom(const std::string username);
    bool requestJoinRoom(int roomId, const std::string username);
    bool requestQuit();
    bool sendReadyStatus();

    bool sendChatMessage(std::string message);
    bool sendFileName(std::string fileName);
    bool serializeAndSendData(jokinojo::RequestData);

    bool sendMediaStatus(int timePosition, bool isPaused);

private:
    asio::io_context m_io_context;
    asio::ip::tcp::socket m_socket;
    std::function<void(jokinojo::ResponseData)> m_dataCallback;

    Networker() : m_socket(m_io_context) {}
    ~Networker() = default;

    // Delete copy constructor and assignment operator to prevent copying
    Networker(const Networker&) = delete;
    Networker& operator=(const Networker&) = delete;
};


#endif //JOKINOJO_NETWORKER_HH
