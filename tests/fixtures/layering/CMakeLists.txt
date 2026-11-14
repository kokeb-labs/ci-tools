# Self-test project of ru-layering.yml: three parts linked downwards, the RTOS backend PRIVATE, built on the host
# without the RTOS (FX_RTOS=OFF), so the poison build proves the platform-free parts include no RTOS header.
cmake_minimum_required(VERSION 3.21)
project(layering_fixture LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
option(FX_RTOS "Build the RTOS backend (needs FreeRTOS headers)" OFF)
option(FX_BUILD_TESTS "Build the tests" OFF)

add_library(fx_core lib/core/src/core.cpp)
target_include_directories(fx_core PUBLIC lib/core/inc)
if(FX_RTOS)
  add_library(fx_backend lib/core/backends/rtos_boundary.cpp)
  target_link_libraries(fx_backend PRIVATE fx_core)
endif()
add_library(fx_app lib/app/src/app.cpp)
target_include_directories(fx_app PUBLIC lib/app/inc)
target_link_libraries(fx_app PUBLIC fx_core)

if(FX_BUILD_TESTS)
  add_executable(fx_test tests/fx_test.cpp)
  target_include_directories(fx_test PRIVATE tests)
  target_link_libraries(fx_test PRIVATE fx_app)
endif()
