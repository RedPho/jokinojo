//
// Created by emin on 31.10.2024.
//

#ifndef JOKINOJO_MEDIA_PLAYER_HH
#define JOKINOJO_MEDIA_PLAYER_HH
#include <string>
#include <mpv/client.h>
#include <network.pb.h>
#include "Networker.hh"

class MediaPlayer {
private:
    Networker* m_networker;
    mpv_handle *mpv;
    int m_paused{};
    bool m_isHost{};
    bool m_stopMediaActions;
public:
    void handleMediaActions();
    void setIsHost(bool h) {
        m_isHost = h;
    }
    bool isHost() {
        return m_isHost;
    }
    void check_mpv_error(int status);
    bool initialize(Networker* networker);
    void setMediaStatus(bool isPaused, int timePosition);
    void setMediaPausedStatus(bool isPaused);
    void setMpvHandle(mpv_handle* mpvHandle) {
        mpv = mpvHandle;
    }

    bool getIsPaused();
    double getTimePositionSeconds();
    int getTimePositionMiliseconds();
    std::string getFileName();
    void destroy();
    ~MediaPlayer();

    void stopMediaActions();
};


#endif //JOKINOJO_MEDIA_PLAYER_HH
