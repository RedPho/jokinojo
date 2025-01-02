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

bool MediaPlayer::initialize(Networker* networker) {
    m_networker = networker;

    // Create new mpv instance
    std::cout << "mpv_create calling\n";
    mpv = mpv_create();
    std::cout << "mpv_create called\n";

    if (!mpv) {
        std::cout << "failed creating context\n";
        return false;
    }

    std::cout << "key bindings setting.\n";

    // key bindings
    int val = 1;
    if (isHost()) {
        check_mpv_error(mpv_set_option_string(mpv, "input-default-bindings", "yes"));
        check_mpv_error(mpv_set_option_string(mpv, "input-vo-keyboard", "yes"));
    } else {
        check_mpv_error(mpv_set_option_string(mpv, "input-default-bindings", "no"));
        check_mpv_error(mpv_set_option_string(mpv, "input-vo-keyboard", "no"));
        val = 0;
    }

    check_mpv_error(mpv_set_option(mpv, "osc", MPV_FORMAT_FLAG, &val));
    std::cout << "mpv_initialize calling.\n";
    check_mpv_error(mpv_initialize(mpv));
    std::cout << "mpv_initialize called.\n";

    const char *idle_cmd[] = {"loadfile", "no", NULL};
    check_mpv_error(mpv_command(mpv, idle_cmd));
    const char *force_window_cmd[] = {"set", "force-window", "yes", NULL};
    check_mpv_error(mpv_command(mpv, force_window_cmd));
    std::cout << "media player init is successful.\n";

    return true;
}

void MediaPlayer::setMediaStatus(bool isPaused, int timePosition) {
    int pausedFlag{0};
    if (isPaused) {
        pausedFlag = 1;
    }
    check_mpv_error(mpv_set_property(mpv, "pause", MPV_FORMAT_FLAG, (void *) &(pausedFlag)));
    double timePosSeconds = timePosition/1000.0;
    check_mpv_error(mpv_set_property(mpv, "time-pos", MPV_FORMAT_DOUBLE, &(timePosSeconds)));
}

void MediaPlayer::setMediaPausedStatus(bool isPaused) {
    check_mpv_error(mpv_set_property(mpv, "pause", MPV_FORMAT_FLAG, (void *) &(isPaused)));
}

std::string MediaPlayer::getFileName() {
    const char* filename = nullptr; // Pointer to hold the filename string
    int error = mpv_get_property(mpv, "filename/no-ext", MPV_FORMAT_STRING, &filename);
    if (error < 0 || filename == nullptr) { // Handle errors
        check_mpv_error(error); // Log the error or handle it as needed
        return {};
    }

    std::string result(filename); // Convert to std::string
    mpv_free(const_cast<char*>(filename)); // Free the memory allocated by libmpv
    return result;
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
    return isPaused == 1;
}

void MediaPlayer::destroy() {
    if (mpv) {
        mpv_terminate_destroy(mpv);  // Properly destroy the MPV instance
        mpv = nullptr;  // Reset the pointer
        m_paused = false;
    }
}

MediaPlayer::~MediaPlayer() {
    destroy();
}

void MediaPlayer::handleMediaActions() {
    while (!m_stopMediaActions) {
        if(!mpv) {
            std::cout << "there is no mpv context. handlmediaactions thread.\n";
            return;
        }
        mpv_event *event = mpv_wait_event(mpv, 0);
        if (isHost()) {
            bool oldIsPaused = m_paused; // Capture the current paused state.
            bool currentPaused = getIsPaused();

            if (oldIsPaused != currentPaused || event->event_id == MPV_EVENT_SEEK) {
                m_paused = currentPaused;
                int timePosData = getTimePositionMiliseconds();
                bool pausedData = currentPaused;
                m_networker->sendMediaStatus(timePosData, pausedData);
            } else if (event->event_id == MPV_EVENT_FILE_LOADED) {
                std::string fileName = getFileName();
                m_networker->sendFileName(fileName);
                setMediaPausedStatus(true);
                
            }
        } else { // is not host(client)

            if (event->event_id == MPV_EVENT_FILE_LOADED) {
                std::cout << "not host\n";
                m_networker->sendReadyStatus();
                setMediaPausedStatus(true);
            }
        }
    }
    return;
}

void MediaPlayer::stopMediaActions() {
    m_stopMediaActions = true;
}