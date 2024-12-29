cmake_minimum_required(VERSION 3.27)
project(JoKinoJo)
set(CMAKE_CXX_STANDARD 20)

if (APPLE)
    # macOS specific configuration
    find_package(Protobuf REQUIRED)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(MPV REQUIRED mpv)
    find_package(wxWidgets REQUIRED COMPONENTS core base)
    
    # On macOS, you might want to use brew-installed libraries
    include_directories(/usr/local/include)
    link_directories(/usr/local/lib)
elseif (WIN32)
    add_definitions(-D_WIN32_WINNT=0x0A00) # Windows 10
    # On Windows, let vcpkg handle finding dependencies
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_SOURCE_DIR}/libraries/vcpkg/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_PREFIX_PATH "${CMAKE_SOURCE_DIR}/libraries/vcpkg/installed/x64-windows/share" ${CMAKE_PREFIX_PATH})
    find_package(Protobuf CONFIG REQUIRED)
    set(Protobuf_LIBRARIES "${CMAKE_SOURCE_DIR}/libraries/vcpkg/installed/x64-windows/lib/libprotobuf.lib")
    find_package(wxWidgets CONFIG REQUIRED COMPONENTS core base)
    find_package(absl CONFIG REQUIRED)
    include_directories("${CMAKE_SOURCE_DIR}/libraries/libmpv/include")
    set(MPV_LIBRARIES "${CMAKE_SOURCE_DIR}/libraries/libmpv/libmpv.dll.a")
else()
    # Linux configuration
    find_package(Protobuf REQUIRED)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(MPV REQUIRED mpv)
    find_package(wxWidgets REQUIRED COMPONENTS core base)
endif()

if(wxWidgets_USE_FILE)
    include(${wxWidgets_USE_FILE})
endif()

include_directories(${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/libraries/asio/include
    ${wxWidgets_INCLUDE_DIRS}
    ${Protobuf_INCLUDE_DIRS}
)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS network.proto)
include_directories(${CMAKE_CURRENT_BINARY_DIR})

if (WIN32)
    add_executable(JoKinoJo WIN32
        main.cpp
        Networker.cpp
        Networker.hh
        MediaPlayer.cpp
        MediaPlayer.hh
        ${PROTO_SRCS}
        ${PROTO_HDRS}
    )
    target_link_libraries(JoKinoJo
        ${Protobuf_LIBRARIES}
        ${wxWidgets_LIBRARIES}
        ${MPV_LIBRARIES}
        absl::base
        absl::log
        absl::strings
        absl::synchronization
        absl::status
    )
else()
    add_executable(JoKinoJo
        main.cpp
        Networker.cpp
        Networker.hh
        MediaPlayer.cpp
        MediaPlayer.hh
        ${PROTO_SRCS}
        ${PROTO_HDRS}
    )
    target_link_libraries(JoKinoJo
        ${wxWidgets_LIBRARIES}
        ${MPV_LIBRARIES}
        ${Protobuf_LIBRARIES}
        absl_log_internal_check_op
        absl_log_internal_message
        absl_base
        absl_strings
        absl_synchronization
        absl_status
        absl_raw_logging_internal
        absl_throw_delegate
    )
endif()
