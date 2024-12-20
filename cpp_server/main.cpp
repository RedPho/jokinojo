#include <iostream>
#include <vector>
#include <thread>
#include <mutex>
#include <asio.hpp>
#include "network.pb.h"

int userCount{0};
int roomCount{0};

struct User {
    int id;
    std::string username;
    asio::ip::tcp::socket* socket;
    int roomId;
    bool operator==(const User& other) const {
        return id == other.id && username == other.username && socket == other.socket && roomId == other.roomId;
    }
};

struct Room {
    int id;
    std::vector<User> users;
    bool operator==(const Room& other) const {
        return id == other.id && users == other.users;
    }
};

Room* getRoom(int id, std::vector<Room>& rooms) {
    for (Room& room : rooms) {
        if (room.id == id) {
            return &room;
        }
    }
    return nullptr; // Indicate the room was not found.
}


void serializeAndSendData(asio::ip::tcp::socket* socket ,const jokinojo::ResponseData& networkData) {
    std::string serializedData;
    if (!networkData.SerializeToString(&serializedData)) {
        std::cerr << "Failed to serialize data." << std::endl;
        return;
    }

    std::error_code error;
    asio::write(*socket, asio::buffer(serializedData), error);
    if (error) {
        std::cerr << "Failed to send data: " << error.message() << std::endl;
    }
}

void broadcastToRoom(const Room& room, const jokinojo::ResponseData& data) {
    std::cout << "broadcasting room: " + std::to_string(room.id) + "\n";
    for (const User& user: room.users) {
        serializeAndSendData(user.socket, data);
        std::cout << "sent to: " + user.username + "\n";
    }
}

void accept_loop(asio::ip::tcp::acceptor& acceptor, std::vector<User>& allUsers, std::mutex& clientMutex, asio::io_context& io_context)
{
    while(true) {
    auto* client = new asio::ip::tcp::socket(io_context);

        try {
            std::cout << "trying new connections\n";
            // Accept the connection
            acceptor.accept(*client);
            // Retrieve the remote IP address
            std::string remote_ip = client->remote_endpoint().address().to_string();
            std::cout << "TCP client connected: " << remote_ip << "\n";

            // Lock the mutex before modifying the vector
            {
                std::lock_guard<std::mutex> lock(clientMutex);
                allUsers.push_back(User{userCount, "defaultName", client, -1});
                std::cout << "Added to all users: " << remote_ip << "\n";
            }
            ++userCount;
            std::cout << "user count: " << userCount << "\n";

        } catch (const std::exception& e) {
            std::cerr << "Exception: " << e.what() << "\n";
            delete client;
        }

    }
}

std::vector<User> allUsers;
std::vector<Room> allRooms;

void handleData(User& user, const jokinojo::RequestData& requestData) {
    std::cout << "handling data\n";
    switch (requestData.datatype()) {
        case jokinojo::RequestData_DataType_CREATE_ROOM: {
            std::cout <<"create data\n";

            user.username = requestData.username();
            std::vector<User> usersInRoom{};
            usersInRoom.push_back(user);
            Room room = Room{roomCount, usersInRoom};
            std::cout << "new room with id: " << room.id << "\n";
            user.roomId = room.id;
            ++roomCount;
            allRooms.push_back(room);

            jokinojo::ResponseData responseData;
            responseData.set_datatype(jokinojo::ResponseData_DataType_CREATE_ROOM);
            responseData.set_roomid(room.id);
            serializeAndSendData(user.socket, responseData);
            break;
        }
        case jokinojo::RequestData_DataType_JOIN_ROOM: {
            std::cout <<"join data\n";

            user.username = requestData.username();
            int roomId = requestData.roomid();
            jokinojo::ResponseData responseData;
            Room* room = getRoom(roomId, allRooms);
            if (room->id >= 0) {
                room->users.push_back(user);
                user.roomId = room->id;
                responseData.set_datatype(jokinojo::ResponseData_DataType_JOIN_ROOM);
                responseData.set_username(user.username);
                broadcastToRoom(*room, responseData);
            } else {
                responseData.set_datatype(jokinojo::ResponseData_DataType_ERROR);
                responseData.set_errormessage("Room could not found.");
                serializeAndSendData(user.socket, responseData);
            }
            break;
        }
        case jokinojo::RequestData_DataType_QUIT:
            break;
        case jokinojo::RequestData_DataType_SYNC: {
            std::cout <<"sync data\n";
            jokinojo::ResponseData responseData;
            responseData.set_datatype(jokinojo::ResponseData_DataType_SYNC);
            responseData.set_timeposition(requestData.timeposition());
            responseData.set_resumed(requestData.resumed());
            Room* room = getRoom(user.roomId, allRooms);
            broadcastToRoom(*room, responseData);
            break;
        }
        case jokinojo::RequestData_DataType_VIDEO_NAME: {
            std::cout <<"video name data\n";
            jokinojo::ResponseData responseData;
            responseData.set_datatype(jokinojo::ResponseData_DataType_VIDEO_NAME);
            responseData.set_videoname(requestData.videoname());
            Room* room = getRoom(user.roomId, allRooms);
            broadcastToRoom(*room, responseData);
            break;
        }
        case jokinojo::RequestData_DataType_READY: {
            std::cout <<"ready data\n";

            jokinojo::ResponseData responseData;
            responseData.set_datatype(jokinojo::ResponseData_DataType_READY);
            responseData.set_username(user.username);
            Room* room = getRoom(user.roomId, allRooms);
            broadcastToRoom(*room, responseData);
            break;
        }
        case jokinojo::RequestData_DataType_CHAT: {
            std::cout << "chat message\n";

            jokinojo::ResponseData responseData;
            responseData.set_datatype(jokinojo::ResponseData_DataType_CHAT);
            responseData.set_username(user.username);
            responseData.set_chatmessage(requestData.chatmessage());
            Room* room = getRoom(user.roomId, allRooms);
            broadcastToRoom(*room, responseData);
            break;
        }
        case jokinojo::RequestData_DataType_NULL_:
            std::cout << "unknown data\n";
            break;
        default:
            std::cout << "unknown data\n";
            break;
    }
}

int main(int argc, char *argv[]) {

    std::mutex clientMutex;

    try {

        int port = 5000;

        asio::io_context io_context;
        asio::ip::tcp::acceptor acceptor(io_context, asio::ip::tcp::endpoint(asio::ip::tcp::v4(), port));
        std::thread accept_thread(accept_loop, std::ref(acceptor), std::ref(allUsers), std::ref(clientMutex), std::ref(io_context));

        while (true) {
            // Lock the mutex to safely access the shared client list
            try {
                std::lock_guard<std::mutex> lock(clientMutex);
                for (User& user: allUsers) {
                    if (user.socket->available() > 0) {
                        char data[1024];
                        std::size_t bytesRead = (*user.socket).read_some(asio::buffer(data, sizeof(data)));
                        if (bytesRead > 0) {
                            std::cout << "data came\n";
                            std::string receivedData(data, bytesRead);
                            std::cout << bytesRead << "bytes and the data: " << receivedData << "\n";
                            jokinojo::RequestData requestData;
                            requestData.ParseFromString(receivedData);
                            handleData(user, requestData);
                        }
                    }
                }
            } catch (std::exception& e) {
                std::cout << e.what();
            }
        }

        // Cleanup
        acceptor.close();  // Close the acceptor to stop the accept loop
        io_context.stop(); // Stop the io_context to break out of the event loop
        accept_thread.join();  // Join the thread to make sure it has finished

        for (User u: allUsers) {
            delete u.socket;
        }
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        for (User u: allUsers) {
            delete u.socket;
        }
        return 1;
    }

    return 0;
}
