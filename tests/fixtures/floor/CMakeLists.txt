# Self-test project for ru-floor-compilers.yml: C++20 as the oldest supported compilers (GCC 10, Clang 13) accept it.
cmake_minimum_required(VERSION 3.16)
project(floor_fixture LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
enable_testing()

add_executable(floor_test test/floor_test.cpp)
add_test(NAME floor COMMAND floor_test)
