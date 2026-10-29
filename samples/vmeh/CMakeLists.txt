cmake_minimum_required(VERSION 3.11)
set(CMAKE_TOOLCHAIN_FILE "$ENV{PSPDEV}/psp/share/pspdev.cmake" CACHE PATH "toolchain file")
project(vme-hardware C CXX ASM)

include(../../cmake/vmegc.cmake)

set(VMEH_SOURCE "" CACHE STRING "vmeg file with an @emulate, relative to the root of the project")
set(VMEH_ID "" CACHE STRING "id of the @emulate to extract")
set(VMEH_BUFFERS_START 0 CACHE STRING "first word of the window of the buffers")
set(VMEH_BUFFERS_WORDS 32 CACHE STRING "number of words of the window of the buffers")

if(NOT VMEH_SOURCE OR NOT VMEH_ID)
  message(FATAL_ERROR "give the vmeg file and the id of its @emulate, for example: cmake -DVMEH_SOURCE=path/to/file.vmeg.cpp -DVMEH_ID=id ..")
endif()

get_filename_component(VMEH_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
get_filename_component(VMEH_INPUT "${VMEH_ROOT}/${VMEH_SOURCE}" ABSOLUTE)
set(VMEH_OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/hw-${VMEH_ID}.vmeg.cpp")

execute_process(
  COMMAND "${VMEGC_PYTHON}" "${VMEH_ROOT}/vmeh.py"
    --extract "${VMEH_ID}" "${VMEH_INPUT}" -o "${VMEH_OUTPUT}"
    --buffers-start "${VMEH_BUFFERS_START}" --buffers-words "${VMEH_BUFFERS_WORDS}"
  RESULT_VARIABLE VMEH_RESULT
  ERROR_VARIABLE VMEH_ERROR)

if(VMEH_RESULT)
  message(FATAL_ERROR "vmeh: ${VMEH_ERROR}")
endif()

set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${VMEH_INPUT}")

add_executable(vme)
vmegc_sources(vme SOURCES "${VMEH_OUTPUT}")

target_include_directories(vme PRIVATE ../../vmeh)

target_compile_options(vme PRIVATE -Os -G0 -Wall -fno-pic)

target_compile_options(vme PRIVATE
  $<$<COMPILE_LANGUAGE:CXX>:-std=c++11>
  $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
  $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
)

target_link_libraries(vme
  nl-me-core nl-me-core-lib nl-vme-lib
  psppower pspge pspdisplay pspctrl pspdebug
)

create_pbp_file(TARGET vme TITLE "VME Hardware" BUILD_PRX)
