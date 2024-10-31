//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_MEDIA_PLAYER_HH
#define JOKINOJO_MEDIA_PLAYER_HH
#include <string>
#include <mpv/client.h>

class MediaPlayer {
private:
    mpv_handle *mpv;
public:
    void check_mpv_error(int status);
    bool initialize();
    bool setMediaStatus(bool isPaused, int timePosition);
    std::string getFileName();
};


#endif //JOKINOJO_MEDIA_PLAYER_HH
