find_program(VMEGC_PYTHON NAMES python3 python)
if(NOT VMEGC_PYTHON)
  message(FATAL_ERROR "vmegc needs python3")
endif()

get_filename_component(VMEGC_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/../vmegc.py" ABSOLUTE)

function(vmegc_translate out_c out_info input)
  get_filename_component(name "${input}" NAME)
  string(REGEX REPLACE "\\.vmeg\\.c$" "" base "${name}")
  get_filename_component(source "${input}" ABSOLUTE)
  set(c "${CMAKE_CURRENT_BINARY_DIR}/${base}.c")
  set(info "${CMAKE_CURRENT_BINARY_DIR}/${base}.vmeg-info")
  add_custom_command(
    OUTPUT "${c}" "${info}"
    COMMAND "${VMEGC_PYTHON}" "${VMEGC_SCRIPT}" "${source}" -o "${c}"
    DEPENDS "${source}" "${VMEGC_SCRIPT}"
    COMMENT "vmegc ${name}"
    VERBATIM)
  set(${out_c} "${c}" PARENT_SCOPE)
  set(${out_info} "${info}" PARENT_SCOPE)
endfunction()

function(vmegc_sources target)
  if(CMAKE_VERSION VERSION_LESS 3.11)
    message(FATAL_ERROR "vmegc_sources needs cmake 3.11 or newer")
  endif()
  cmake_parse_arguments(ARG "" "" "SOURCES;INCLUDE" ${ARGN})
  set(generated "")
  set(infos "")
  foreach(source ${ARG_SOURCES})
    vmegc_translate(c info "${source}")
    list(APPEND generated "${c}")
    list(APPEND infos "${info}")
  endforeach()
  set(globals "${CMAKE_CURRENT_BINARY_DIR}/${target}.vmeg-globals.c")
  set(include_args "")
  foreach(header ${ARG_INCLUDE})
    list(APPEND include_args --include "${header}")
  endforeach()
  add_custom_command(
    OUTPUT "${globals}"
    COMMAND "${VMEGC_PYTHON}" "${VMEGC_SCRIPT}" --merge ${infos} -o "${globals}" ${include_args}
    DEPENDS ${infos} "${VMEGC_SCRIPT}"
    COMMENT "vmegc merge ${target}"
    VERBATIM)
  target_sources(${target} PRIVATE ${generated} "${globals}")
endfunction()
