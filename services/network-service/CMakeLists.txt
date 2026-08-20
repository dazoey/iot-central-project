# Network Protocol Service (C++) - Build Configuration

cmake_minimum_required(VERSION 3.14)
project(NetworkProtocolService VERSION 1.0.0 LANGUAGES CXX)

# Detect macOS SDK Sysroot & C++ STL Headers automatically
if(APPLE)
    execute_process(
        COMMAND xcrun --show-sdk-path
        OUTPUT_VARIABLE CMAKE_OSX_SYSROOT
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    include_directories("${CMAKE_OSX_SYSROOT}/usr/include/c++/v1")
endif()

# Set C++ Standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(include)

# Source files
file(GLOB SOURCES "src/*.cpp")

# Output executable
add_executable(network_service ${SOURCES})

# Target properties
message(STATUS "Configuring Network Protocol Service (C++) with macOS Sysroot: ${CMAKE_OSX_SYSROOT}")
