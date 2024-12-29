# JoKinoJo

## Overview
**JoKinoJo** is a media player that synchronises media playback with your friends. This is the server.

## Prerequisites

1. **CMake** version 3.27 or newer.
2. **C++ Compiler** supporting C++20.
3. Libraries:
   - [Protobuf](https://github.com/protocolbuffers/protobuf)
   - [Asio](https://think-async.com/Asio/)
   - [abseil-cpp](https://github.com/abseil/abseil-cpp)(protobuf requires this)
   - In windows, this project uses vcpkg, in linux, it doesn't.


## Build Instructions

## Notes
- If you are already comfortable with cmake and vcpkg, you can use your own ways. 
- If you already have vcpkg in your system, you can use that one if you want, you just need to change the cmake variables CMAKE_TOOLCHAIN_FILE, CMAKE_PREFIX_PATH and Protobuf_LIBRARIES according to your vcpkg paths.
- You can also use the prebuilt version I provided.(only for Windows, It is already easy to build for Linux)

### Step 1: Clone the Repository

### Step 2: Configure the Build Environment

#### Windows:
1. To the libraries folder of this project, clone the vcpkg.(I will add it as git submodule)  
2. Run the bootstrap-vcpkg.bat file in the vcpkg folder.  
3. Install these libraries with vcpkg( vcpkg.exe install library_name ):
   - [protobuf](https://github.com/protocolbuffers/protobuf)  
   - [abseil](https://github.com/abseil/abseil-cpp)  

#### Linux:
1. install these libraries using your package manager:
   - [Protobuf](https://github.com/protocolbuffers/protobuf)
   - [abseil-cpp](https://github.com/abseil/abseil-cpp)(protobuf requires this)

### Step 3: Build the Application
1. Create a build directory and cd into it.  
2. Build the project with cmake:  
```bash
cmake ..
```

```bash
cmake --build . --config release
```

### Step 4: Only needed for Windows

1. Copy the dll files I included(from the release_dlls folder) to the build folder  

### Step 5: Run the Application
1. Execute the generated binary:
```bash
./JoKinoJo
```
Or just double click it.
