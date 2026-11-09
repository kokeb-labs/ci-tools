# A tiny driver for ru-misra's self-test: seeded MISRA findings, a deviated one, and suppressions that must fail.
cmake_minimum_required(VERSION 3.16)
project(misra_fixture LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_library(misra_fixture INTERFACE)
target_include_directories(misra_fixture INTERFACE inc)
# The org warning set the compiler-decided guidelines rely on.
add_library(misra_fixture_checks STATIC src/fixture.cpp)
target_link_libraries(misra_fixture_checks PRIVATE misra_fixture)
target_compile_options(misra_fixture_checks PRIVATE -Wall -Wextra -Wpedantic -Wshadow -Wundef -Werror
                                                   -fno-exceptions -fno-rtti)
