cmake_minimum_required(VERSION 3.25)
project(mushi LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(REXSDK_DIR thirdparty/rexglue-sdk)
include(generated/rexglue.cmake)

set(MUSHI_SOURCES
    src/main.cpp
)

if(WIN32)
    add_executable(mushi WIN32 ${MUSHI_SOURCES})
else()
    add_executable(mushi ${MUSHI_SOURCES})
endif()

set_target_properties(mushi PROPERTIES
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
    BUILD_WITH_INSTALL_RPATH ON
    OUTPUT_NAME "Mushihimesama Futari"
)

rexglue_setup_target(mushi GPU_PLUGINS xenos)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/generated/default/dll_targets.cmake")
    # see: https://github.com/rexglue/rexglue-sdk/issues/454
    set_target_properties(mushi_hirow_abnormal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_hirow_normal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_kiniro_abnormal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_kiniro_normal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_palm_abnormal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_palm_normal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_reco_abnormal PROPERTIES PREFIX "" SUFFIX "")
    set_target_properties(mushi_reco_normal PROPERTIES PREFIX "" SUFFIX "")
endif()

