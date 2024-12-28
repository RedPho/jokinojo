# JoKinoJo

## Overview
**JoKinoJo** is a multimedia application that integrates networking and media playback capabilities, leveraging libraries like wxWidgets, MPV, Protobuf, and Asio.

## Prerequisites
Ensure the following dependencies are installed on your system:

1. **CMake** version 3.27 or newer.
2. **C++ Compiler** supporting C++20.
3. Libraries:
   - [Protobuf](https://github.com/protocolbuffers/protobuf)
   - [wxWidgets](https://www.wxwidgets.org/)
   - [MPV](https://mpv.io/)
   - [Asio](https://think-async.com/Asio/) (header-only library, you don't need to install that.)
   - [abseil-cpp](https://github.com/abseil/abseil-cpp)

Use your package manager or build these from source, depending on your environment.

## Build Instructions

### Step 1: Clone the Repository

### Step 2: Configure the Build Environment
Run CMake to configure the project:
```bash
cmake -S . -B build
```

### Step 3: Build the Application
Compile the project:
```bash
cmake --build build
```

### Step 4: Run the Application
Navigate to the `build` directory and execute the generated binary:
```bash
cd build
./JoKinoJo
```

## Notes
- **Protobuf**: Make sure the `.proto` files are compiled using the correct Protobuf compiler (`protoc`) that matches your library version.
- **MPV**: Ensure `libmpv` is available on your system, and the include directories and libraries are correctly linked.
- **wxWidgets**: Verify that wxWidgets is properly installed and detectable by CMake.
- **Asio**: Asio is included as a header-only library under `libraries/asio/include`.
