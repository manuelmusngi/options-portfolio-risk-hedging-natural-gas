cmake_minimum_required(VERSION 3.20)
project(OptionHedgingSystem LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

file(GLOB_RECURSE LIB_SOURCES src/*.cpp)

add_library(hedging_lib ${LIB_SOURCES})
target_include_directories(hedging_lib PUBLIC include)

add_executable(hedging main.cpp)
target_link_libraries(hedging PRIVATE hedging_lib)

enable_testing()
add_subdirectory(tests)
