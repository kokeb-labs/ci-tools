# Self-test project for ru-mutation.yml: a small library whose tests kill every mutant but one, which the
# equivalents file records (docs/equivalent-mutants.yml).
cmake_minimum_required(VERSION 3.21)
project(mutation_fixture LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
enable_testing()
add_library(limits src/limits.cpp)
target_include_directories(limits PUBLIC include)
add_executable(limits_test test/limits_test.cpp)
target_link_libraries(limits_test PRIVATE limits)
add_test(NAME limits COMMAND limits_test)
