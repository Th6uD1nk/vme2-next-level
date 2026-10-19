cmake_minimum_required(VERSION 3.11)
set(CMAKE_TOOLCHAIN_FILE "$ENV{PSPDEV}/psp/share/pspdev.cmake" CACHE PATH "toolchain file")
project(vme-saturate-clamp C ASM)

include(../../cmake/vmegc.cmake)

vmegc_translate(GENERATED_C ${CMAKE_CURRENT_SOURCE_DIR}/saturate-clamp.vmeg.c)

add_library(saturate-clamp OBJECT ${GENERATED_C})
target_compile_options(saturate-clamp PRIVATE -Os -G0 -Wall -fno-pic)
