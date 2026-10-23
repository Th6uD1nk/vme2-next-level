from emu.extract import chosen_emulation, declared_parts
from vmeg.blocks import find_blocks, kernel_name


PROLOGUE = """#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>
#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <debug.h>

PSP_MODULE_INFO("vmeh", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT(32);"""


def kernel_text(text, identifier):
  name = chosen_emulation(text, identifier)["kernel"]
  for block in find_blocks(text):
    if block[0] == "kernel" and kernel_name(text, block) == name:
      return text[block[1]:block[3]]


def extract_source(text, identifier, others=()):
  arrays, macros = declared_parts(text, identifier, others)
  sections = [PROLOGUE]
  if macros:
    sections.append("\n".join(macros))
  globals_ = [declaration["text"] for declaration in arrays if declaration["where"] == "global"]
  if globals_:
    sections.append("\n\n".join(globals_))
  sections.append(kernel_text(text, identifier))
  return "\n\n".join(sections) + "\n"
