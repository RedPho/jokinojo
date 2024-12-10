//
// Created by emin on 31.10.2024.
//

#include <iostream>
#include "MediaPlayer.hh"
#include "Networker.hh"

void MediaPlayer::check_mpv_error(int status) {
    if (status < 0) {
        std::cout << "mpv API error:\n" << mpv_error_string(status);
    }
}

bool MediaPlayer::initialize() {
    if (!mpv) {
        std::cout << "failed creating context\n";
        return false;
    }

    // Enable default key bindings
    check_mpv_error(mpv_set_option_string(mpv, "input-default-bindings", "yes"));
    check_mpv_error(mpv_set_option_string(mpv, "input-vo-keyboard", "yes"));
    int val = 1;
    check_mpv_error(mpv_set_option(mpv, "osc", MPV_FORMAT_FLAG, &val));
    check_mpv_error(mpv_initialize(mpv));
    const char *idle_cmd[] = {"loadfile", "no", NULL};
    check_mpv_error(mpv_command(mpv, idle_cmd));
    const char *force_window_cmd[] = {"set", "force-window", "yes", NULL};
    check_mpv_error(mpv_command(mpv, force_window_cmd));
    return true;
}

void MediaPlayer::setMediaStatus(bool isPaused, int timePosition) {
    check_mpv_error(mpv_set_property(mpv, "pause", MPV_FORMAT_FLAG, (void *) &(isPaused)));
    check_mpv_error(mpv_set_property(mpv, "time-pos", MPV_FORMAT_DOUBLE, &(timePosition)));
}

void MediaPlayer::setMediaPausedStatus(bool isPaused) {
    check_mpv_error(mpv_set_property(mpv, "pause", MPV_FORMAT_FLAG, (void *) &(isPaused)));
}

std::string MediaPlayer::getFileName() {
    std::string filename{};
    check_mpv_error(mpv_get_property(mpv, "filename/no-ext", MPV_FORMAT_STRING, &filename));
    return filename;
}

double MediaPlayer::getTimePositionSeconds() {
    double timePosition{};
    check_mpv_error(mpv_get_property(mpv, "time-pos", MPV_FORMAT_DOUBLE, &(timePosition)));
    return timePosition;
}

int MediaPlayer::getTimePositionMiliseconds() {
    return (int)(getTimePositionSeconds()*1000);
}

bool MediaPlayer::getIsPaused() {
    int isPaused{};
    mpv_get_property(mpv, "pause", MPV_FORMAT_FLAG, &isPaused);
    if (isPaused == 0) {
        m_paused = false;
    } else if (isPaused == 1) {
        m_paused = true;
    }
    return m_paused;
}

void MediaPlayer::handleMediaActions() {
    while (true) {
        mpv_event *event = mpv_wait_event(mpv, 0);
        if (isHost()) {
            bool oldIsPaused = m_paused;;
            if (oldIsPaused != getIsPaused() || event->event_id == MPV_EVENT_SEEK) { // this get also sets the m_paused property. I will change it to look more stateless.
                int timePosData = getTimePositionMiliseconds();
                bool pausedData = getIsPaused();
                m_networker.sendMediaStatus(timePosData, pausedData);
            } else if (event->event_id == MPV_EVENT_FILE_LOADED) {
                std::string fileName = getFileName();
                m_networker.sendFileName(fileName);
            }
        } else { // is not host(client)
            if (event->event_id == MPV_EVENT_FILE_LOADED) {
                m_networker.sendReadyStatus();
            }
        }

    }
}