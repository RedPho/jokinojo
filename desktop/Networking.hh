//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_NETWORKING_HH
#define JOKINOJO_NETWORKING_HH
#include <asio.hpp>

class Networking {
public:
    bool initialize();
    bool handleIncomingData();
    bool requestCreateRoom();
    bool requestJoinRoom();
    bool sendChatMessage();
    bool sendFile(void* fileData);
    bool sendMediaStatus(bool isPaused, int timePosition);
private:
    int socketId;
};


#endif //JOKINOJO_NETWORKING_HH
