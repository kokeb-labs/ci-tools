# Self-test project for ru-cmake-matrix.yml: a library with tests, an install package and a consumer
# (consumer/), configured for an MCU and RTOS named by FIXTURE_MCU and FIXTURE_RTOS. Builds on the host, for Arm
# cores and with the ESP-IDF toolchain file; tests run on the host only.
cmake_minimum_required(VERSION 3.21)
project(ring VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(FIXTURE_MCU "HOST" CACHE STRING "MCU family the configuration is for")
set(FIXTURE_RTOS "NONE" CACHE STRING "RTOS the configuration is for")
set(_mcus HOST ESP32 STM32F4)
set(_rtoses NONE FREERTOS)
if(NOT FIXTURE_MCU IN_LIST _mcus OR NOT FIXTURE_RTOS IN_LIST _rtoses)
  message(FATAL_ERROR "unknown configuration ${FIXTURE_MCU}/${FIXTURE_RTOS}")
endif()
option(RING_STRICT "Warnings are errors" OFF)
option(RING_BUILD_TESTS "Build the tests" ON)

add_library(ring src/ring.cpp)
add_library(ring::ring ALIAS ring)
target_include_directories(ring PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                                       $<INSTALL_INTERFACE:include>)
target_compile_definitions(ring PRIVATE RING_MCU_${FIXTURE_MCU}=1 RING_RTOS_${FIXTURE_RTOS}=1)
if(RING_STRICT)
  target_compile_options(ring PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

if(RING_BUILD_TESTS AND CMAKE_CROSSCOMPILING)
  set(RING_BUILD_TESTS OFF)
endif()
if(RING_BUILD_TESTS)
  enable_testing()
  add_executable(ring_test test/ring_test.cpp)
  target_link_libraries(ring_test PRIVATE ring)
  add_test(NAME ring COMMAND ring_test)
endif()

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
install(TARGETS ring EXPORT ringTargets ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT ringTargets NAMESPACE ring:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/ring)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/ringConfig.cmake"
     "include(\"\${CMAKE_CURRENT_LIST_DIR}/ringTargets.cmake\")\n")
write_basic_package_version_file("${CMAKE_CURRENT_BINARY_DIR}/ringConfigVersion.cmake" COMPATIBILITY SameMajorVersion)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/ringConfig.cmake" "${CMAKE_CURRENT_BINARY_DIR}/ringConfigVersion.cmake"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/ring)
