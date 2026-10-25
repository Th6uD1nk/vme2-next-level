find_program(VMEGC_PYTHON NAMES python3 python)
if(NOT VMEGC_PYTHON)
  message(FATAL_ERROR "vmegc needs python3")
endif()

get_filename_component(VMEGC_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/../vmegc.py" ABSOLUTE)

set(VMEGC_COMPAT "" CACHE STRING "keep only the opcodes compatible with this model (fat)")
set(VMEGC_OPTIONS "")
if(VMEGC_COMPAT)
  if(NOT VMEGC_COMPAT STREQUAL "fat")
    message(FATAL_ERROR "VMEGC_COMPAT must be fat or empty, not '${VMEGC_COMPAT}'")
  endif()
  set(VMEGC_OPTIONS --compat "${VMEGC_COMPAT}")
endif()

function(vmegc_options_stamp out_stamp)
  set(stamp "${CMAKE_CURRENT_BINARY_DIR}/vmegc-options.txt")
  set(current "")
  if(EXISTS "${stamp}")
    file(READ "${stamp}" current)
  endif()
  if(NOT EXISTS "${stamp}" OR NOT current STREQUAL "${VMEGC_OPTIONS}")
    file(WRITE "${stamp}" "${VMEGC_OPTIONS}")
  endif()
  set(${out_stamp} "${stamp}" PARENT_SCOPE)
endfunction()

function(vmegc_translate out_c input)
  get_filename_component(name "${input}" NAME)
  string(REGEX REPLACE "\\.vmeg\\.(cpp|c)$" "" base "${name}")
  string(REGEX REPLACE "^.*\\.vmeg\\.(cpp|c)$" "\\1" extension "${name}")
  get_filename_component(source "${input}" ABSOLUTE)
  set(c "${CMAKE_CURRENT_BINARY_DIR}/${base}.${extension}")
  vmegc_options_stamp(stamp)
  add_custom_command(
    OUTPUT "${c}"
    COMMAND "${VMEGC_PYTHON}" "${VMEGC_SCRIPT}" "${source}" -o "${c}" ${VMEGC_OPTIONS}
    DEPENDS "${source}" "${VMEGC_SCRIPT}" "${stamp}"
    COMMENT "vmegc ${name}"
    VERBATIM)
  set(${out_c} "${c}" PARENT_SCOPE)
endfunction()

function(vmegc_sources target)
  if(CMAKE_VERSION VERSION_LESS 3.11)
    message(FATAL_ERROR "vmegc_sources needs cmake 3.11 or newer")
  endif()
  cmake_parse_arguments(ARG "" "" "SOURCES" ${ARGN})
  set(inputs "")
  set(generated "")
  foreach(source ${ARG_SOURCES})
    get_filename_component(name "${source}" NAME)
    string(REGEX REPLACE "\\.vmeg\\.(cpp|c)$" "" base "${name}")
    string(REGEX REPLACE "^.*\\.vmeg\\.(cpp|c)$" "\\1" extension "${name}")
    get_filename_component(input "${source}" ABSOLUTE)
    list(APPEND inputs "${input}")
    list(APPEND generated "${CMAKE_CURRENT_BINARY_DIR}/${base}.${extension}")
  endforeach()
  vmegc_options_stamp(stamp)
  add_custom_command(
    OUTPUT ${generated}
    COMMAND "${VMEGC_PYTHON}" "${VMEGC_SCRIPT}" ${inputs} ${VMEGC_OPTIONS}
    DEPENDS ${inputs} "${VMEGC_SCRIPT}" "${stamp}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "vmegc ${target}"
    VERBATIM)
  target_sources(${target} PRIVATE ${generated})
endfunction()
