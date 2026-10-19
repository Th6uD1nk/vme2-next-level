find_program(VMEGC_PYTHON NAMES python3 python)
if(NOT VMEGC_PYTHON)
  message(FATAL_ERROR "vmegc needs python3")
endif()

get_filename_component(VMEGC_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/../vmegc.py" ABSOLUTE)

function(vmegc_translate out_c input)
  get_filename_component(name "${input}" NAME)
  string(REGEX REPLACE "\\.vmeg\\.(cpp|c)$" "" base "${name}")
  string(REGEX REPLACE "^.*\\.vmeg\\.(cpp|c)$" "\\1" extension "${name}")
  get_filename_component(source "${input}" ABSOLUTE)
  set(c "${CMAKE_CURRENT_BINARY_DIR}/${base}.${extension}")
  add_custom_command(
    OUTPUT "${c}"
    COMMAND "${VMEGC_PYTHON}" "${VMEGC_SCRIPT}" "${source}" -o "${c}"
    DEPENDS "${source}" "${VMEGC_SCRIPT}"
    COMMENT "vmegc ${name}"
    VERBATIM)
  set(${out_c} "${c}" PARENT_SCOPE)
endfunction()

function(vmegc_sources target)
  if(CMAKE_VERSION VERSION_LESS 3.11)
    message(FATAL_ERROR "vmegc_sources needs cmake 3.11 or newer")
  endif()
  cmake_parse_arguments(ARG "" "" "SOURCES" ${ARGN})
  set(generated "")
  foreach(source ${ARG_SOURCES})
    vmegc_translate(c "${source}")
    list(APPEND generated "${c}")
  endforeach()
  target_sources(${target} PRIVATE ${generated})
endfunction()
