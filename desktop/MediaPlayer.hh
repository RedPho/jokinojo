//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_MEDIA_PLAYER_HH
#define JOKINOJO_MEDIA_PLAYER_HH
#include <string>
#include <mpv/client.h>

class MediaPlayer {
private:
    mpv_handle *mpv = mpv_create();
    int m_paused{};
    bool m_isHost{};
public:
    void setIsHost(bool h) {
        m_isHost = h;
    }
    bool isHost() {
        return m_isHost;
    }
    void check_mpv_error(int status);
    bool initialize();
    void setMediaStatus(bool isPaused, int timePosition);
    void setMpvHandle(mpv_handle* mpvHandle) {
        mpv = mpvHandle;
    }

    bool getIsPaused();
    int getTimePosition();
    std::string getFileName();
    void handleMediaChanges();
};


#endif //JOKINOJO_MEDIA_PLAYER_HH
