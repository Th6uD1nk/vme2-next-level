from emu.extract import chosen_emulation, declared_parts
from emu.memory import BUFFER_WORDS
from vmeg.blocks import find_blocks, kernel_name


def prologue(words):
  return f"""#include <pspctrl.h>
#include <pspdisplay.h>
#include <pspkernel.h>
#include <psppower.h>
#include <me-core-mapper/me-core.h>
#include <me-core-mapper/vme-fu-opcodes.h>
#include <vme-debug.h>

PSP_MODULE_INFO("vmeh", 0, 1, 1);
PSP_HEAP_SIZE_KB(-1024);
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_VFPU | PSP_THREAD_ATTR_USER);

ME_LIB_SETUP_SIMPLE_SUSPEND_HANDLER();
VME_DEBUG_SET_BUFFER_WORD_COUNT({words});

meLibSetSharedUncached32(1);
#define meFinish (meLibSharedMemory[0])"""


MAIN = """int main() {
  scePowerSetClockFrequency(333, 333, 166);
  vmeDebugSetupBuffers();

  meLibDefaultInit();

  while (!meFinish) {
    sceKernelDelayThread(100);
  }

  vmeDebugTouch();
  vmeDebugDumpWindow();
  vmeDebugFreeBuffers();

  sceKernelExitGame();
  return 0;
}"""


def kernel_text(text, identifier):
  name = chosen_emulation(text, identifier)["kernel"]
  for block in find_blocks(text):
    if block[0] == "kernel" and kernel_name(text, block) == name:
      return text[block[1]:block[3]]


def process_function(text, identifier, locals_, start):
  kernel = chosen_emulation(text, identifier)["kernel"]
  lines = ["void meLibOnProcess(void) {"]
  for declaration in locals_:
    lines += [f"  {declaration['text']}", ""]
  lines += [f"  @kernel {kernel} config | exec {{", f"    vmeDebugFillWith(VME_BASE_BUFFERS{fill_offset(start)});", "  }", "", "  meFinish = 1;", "", "  while (1) {", "  }", "}"]
  return "\n".join(lines)


def fill_offset(start):
  return f" + {start} * 4" if start else ""


def check_window(start, words):
  if start < 0:
    raise ValueError("the first word of the buffers cannot be negative")
  if words <= 0:
    raise ValueError("the number of words of the buffers must be 1 or more")
  if start + words > BUFFER_WORDS:
    raise ValueError(f"the window of the buffers goes past the end of a buffer ({BUFFER_WORDS} words)")


def extract_source(text, identifier, others=(), start=0, words=32):
  check_window(start, words)
  arrays, macros = declared_parts(text, identifier, others)
  sections = [prologue(words)]
  if macros:
    sections.append("\n".join(macros))
  globals_ = [declaration["text"] for declaration in arrays if declaration["where"] == "global"]
  if globals_:
    sections.append("\n\n".join(globals_))
  sections.append(kernel_text(text, identifier))
  sections.append(process_function(text, identifier, [declaration for declaration in arrays if declaration["where"] == "local"], start))
  sections.append(MAIN)
  return "\n\n".join(sections) + "\n"
