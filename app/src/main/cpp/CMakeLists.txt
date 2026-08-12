cmake_minimum_required(VERSION 3.22.1)
project(genesis_engine)

add_library(genesis_engine SHARED
    native_genesis_engine.cpp
)

find_library(android-lib android)
find_library(log-lib log)
find_library(vulkan-lib vulkan)

target_compile_features(genesis_engine PRIVATE cxx_std_20)
target_compile_options(genesis_engine PRIVATE -Wall -Wextra -Werror)
target_link_libraries(genesis_engine PRIVATE ${android-lib} ${log-lib} ${vulkan-lib})
