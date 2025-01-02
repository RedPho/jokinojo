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
    Networker();
    ~Networker();

    using DataCallback = std::function<void(jokinojo::ResponseData)>;

    bool initialize(std::string ip, int port);
    void cleanup();
    bool isConnected() const { return m_socket.is_open(); }
    void setDataCallback(DataCallback callback) { m_dataCallback = std::move(callback); }

    // Request methods
    bool requestJoinRoom(int roomId, std::string username);
    bool requestCreateRoom(std::string username);
    bool sendMediaStatus(int timePosition, bool isPaused);
    bool sendFileName(std::string fileName);
    bool requestQuit();
    bool sendReadyStatus();
    bool sendChatMessage(std::string message);

private:
    asio::io_context m_io_context;
    asio::ip::tcp::socket m_socket{m_io_context};
    DataCallback m_dataCallback;
    std::thread m_networkThread;

    void handleIncomingData();
    bool serializeAndSendData(jokinojo::RequestData networkData);
};

#endif //JOKINOJO_NETWORKER_HH
