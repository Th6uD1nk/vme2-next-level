from vmee.extract import chosen_emulation, declared_parts
from vmee.memory import check_window
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
  names = chosen_emulation(text, identifier)["kernels"]
  blocks = find_blocks(text)
  return "\n\n".join(text[block[1]:block[3]] for name in names for block in blocks if block[0] == "kernel" and kernel_name(text, block) == name)


def process_function(text, identifier, locals_, start):
  kernel = chosen_emulation(text, identifier)["kernel"]
  lines = ["void meLibOnProcess(void) {"]
  for declaration in locals_:
    lines += [f"  {declaration['text']}", ""]
  lines += [f"  @kernel {kernel} config | exec {{", f"    vmeDebugFillWith(VME_BASE_BUFFERS{fill_offset(start)});", "  }", "", "  meFinish = 1;", "", "  while (1) {", "  }", "}"]
  return "\n".join(lines)


def fill_offset(start):
  return f" + {start} * 4" if start else ""


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
