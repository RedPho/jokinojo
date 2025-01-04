# JoKinoJo
**JoKinoJo** is a media player that synchronises media playback with your friends.  

## Server

### Prerequisites
1. [Python3](https://www.python.org/)
2. [Protobuf](https://github.com/protocolbuffers/protobuf)

### Setup and Run Instructions

1. To start the server, at first, cd into the python directory of this project.  
2. Compile the protobuf file.  
```bash
protoc --python_out=. network.proto
```
3. Create and activate the python virtual environment.  
4. Install protobuf python library with pip.  
5. Start the server.  

```bash
python3 -m venv venv
source venv/bin/activate
pip install protobuf
python server.py
```


## Desktop

To build the desktop app, at first, cd into the desktop directory of this project.

### Prerequisites

1. **CMake** version 3.27 or newer.
2. **C++ Compiler** supporting C++20.
3. Libraries:
   - [Protobuf](https://github.com/protocolbuffers/protobuf)
   - [wxWidgets](https://www.wxwidgets.org/)
   - [MPV](https://mpv.io/)
   - [Asio](https://think-async.com/Asio/)
   - [abseil-cpp](https://github.com/abseil/abseil-cpp)(protobuf requires this)
   - [pkg-config](https://gitlab.freedesktop.org/pkg-config/pkg-config)
   - In windows, this project uses vcpkg, in linux, it doesn't.


### Build Instructions

### Notes
- If you are already comfortable with cmake and vcpkg, you can use your own ways. 
- If you already have vcpkg in your system, you can use that one if you want, you just need to change the cmake variables CMAKE_TOOLCHAIN_FILE, CMAKE_PREFIX_PATH and Protobuf_LIBRARIES according to your vcpkg paths.
- You can also use the [prebuilt version](https://drive.google.com/drive/folders/1HQvRmpQ54Rlii4XynUh39SXDRIkOszrp?usp=sharing) I provided.(only for Windows, It is already easy to build for Linux) 

#### Step 1: Configure the Build Environment

##### Windows:
1. To the libraries folder of this project, clone the vcpkg.(I will add it as git submodule)  
2. Run the bootstrap-vcpkg.bat file in the vcpkg folder.  
3. Install these libraries with vcpkg( vcpkg.exe install library_name ):
   - [protobuf](https://github.com/protocolbuffers/protobuf)  
   - [wxwidgets](https://www.wxwidgets.org/)  
   - [abseil](https://github.com/abseil/abseil-cpp)(protobuf requires this)  

vcpkg doesn't have libmpv so I included the binarires in the project. You don't need to install it.  

##### Linux and MacOS:
1. install these libraries using your package manager:
   - [Protobuf](https://github.com/protocolbuffers/protobuf)
   - [wxWidgets](https://www.wxwidgets.org/)
   - [MPV](https://mpv.io/)
   - [abseil-cpp or abseil](https://github.com/abseil/abseil-cpp)(protobuf requires this)
   - [pkg-config](https://gitlab.freedesktop.org/pkg-config/pkg-config)

Examples:  
```bash
sudo pacman -S protobuf wxwidgets abseil-cpp pkg-config mpv
```
```bash
brew install protobuf  wxwidgets abseil pkg-config mpv
```

#### Step 2: Build the Application
1. Create a build directory and cd into it.  
2. Build the project with cmake:  
```bash
cmake ..
```

```bash
cmake --build . --config release
```

#### Step 3: Dll files. This step is only needed for Windows

1. Copy [the dll files](https://drive.google.com/drive/folders/1HQvRmpQ54Rlii4XynUh39SXDRIkOszrp?usp=sharing) to the build folder  

#### Step 4: Run the Application
1. Execute the generated binary:
```bash
./JoKinoJo
```
Or just double click it.
