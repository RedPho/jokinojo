cmake_minimum_required(VERSION 3.27)
project(JoKinoJo)

set(CMAKE_CXX_STANDARD 20)
find_package(Protobuf REQUIRED)
include_directories(${Protobuf_INCLUDE_DIRS})

find_package(wxWidgets REQUIRED COMPONENTS core base)
include(${wxWidgets_USE_FILE})

find_package(PkgConfig REQUIRED)
pkg_check_modules(MPV REQUIRED mpv)

include_directories(${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/libraries/asio/include ${wxWidgets_INCLUDE_DIRS} ${MPV_INCLUDE_DIRS})

add_executable(JoKinoJo
        main.cpp
        Networker.cpp
        Networker.hh
        MediaPlayer.cpp
        MediaPlayer.hh
        network.pb.cc
)


target_link_libraries(JoKinoJo ${wxWidgets_LIBRARIES} ${MPV_LIBRARIES} ${Protobuf_LIBRARIES}
        absl_log_internal_check_op
        absl_log_internal_message
        absl_base
        absl_strings
        absl_synchronization
        absl_status
        absl_raw_logging_internal
        absl_throw_delegate

)
