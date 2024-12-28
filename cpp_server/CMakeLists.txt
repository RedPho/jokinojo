cmake_minimum_required(VERSION 3.27)
project(JoKinoJo)

set(CMAKE_CXX_STANDARD 20)

if (NOT WIN32)
    find_package(Protobuf REQUIRED)
    find_package(PkgConfig REQUIRED)
else()
    add_definitions(-D_WIN32_WINNT=0x0A00) # Windows 10
    # On Windows, let vcpkg handle finding dependencies
    set(CMAKE_TOOLCHAIN_FILE "C:/Users/emin/vcpkg/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_PREFIX_PATH "C:/Users/emin/vcpkg/installed/x64-windows/share" ${CMAKE_PREFIX_PATH})


    find_package(Protobuf CONFIG REQUIRED)
    set(Protobuf_LIBRARIES "C:/Users/emin/vcpkg/installed/x64-windows/lib/libprotobuf.lib")
    find_package(absl CONFIG REQUIRED)

    include_directories("C:/Program Files (x86)/Libmpv/include")  # Adjust this path
    set(MPV_LIBRARIES "C:/Program Files (x86)/Libmpv/libmpv.dll.a")  # Adjust this path

endif()

include_directories(${Protobuf_INCLUDE_DIRS})
include_directories(${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/libraries/asio/include)


if (WIN32)
    add_executable(JoKinoJo
        main.cpp
        network.pb.cc
    )
    target_link_libraries(JoKinoJo
        ${Protobuf_LIBRARIES}
        absl::base
        absl::log
        absl::strings
        absl::synchronization
        absl::status
    )
else()
    add_executable(JoKinoJo
        main.cpp
        network.pb.cc
    )

    target_link_libraries(JoKinoJo 
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
