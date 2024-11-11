cmake_minimum_required(VERSION 3.27)
project(JoKinoJo)

set(CMAKE_CXX_STANDARD 14)

find_package(wxWidgets REQUIRED COMPONENTS core base)
include(${wxWidgets_USE_FILE})

find_package(PkgConfig REQUIRED)
pkg_check_modules(MPV REQUIRED mpv)

include_directories(${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/libraries/asio/include ${wxWidgets_INCLUDE_DIRS} ${MPV_INCLUDE_DIRS})

add_executable(JoKinoJo
        main.cpp
        Networking.cpp
        Networking.hh
        MediaPlayer.cpp
        MediaPlayer.hh
)

target_link_libraries(JoKinoJo ${wxWidgets_LIBRARIES} ${MPV_LIBRARIES})
