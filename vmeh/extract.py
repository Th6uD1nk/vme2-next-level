from vmee.extract import chosen_emulation, declared_parts, memory_declarations
from vmee.listing import emulations
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


def single_identifier(sources):
  found = [emulation["id"] for _, text in sources for emulation in emulations(text)]
  if not found:
    raise ValueError("there is no @emulate in these files")
  if len(found) > 1:
    raise ValueError(f"there are {len(found)} @emulate in these files ({', '.join(found)}), give --extract ID")
  return found[0]


def kernel_text(text, identifier):
  names = chosen_emulation(text, identifier)["kernels"]
  blocks = find_blocks(text)
  return "\n\n".join(text[block[1]:block[3]] for name in names for block in blocks if block[0] == "kernel" and kernel_name(text, block) == name)


def call_block(name, actions, pairs, memory, body):
  lines = [f"  @kernel {name} {' | '.join(actions)} {{"]
  if pairs:
    lines.append("    .params = { " + ", ".join(f"{key}: {value}" for key, value in pairs) + " };")
  if memory:
    lines.append(f"    .memory = {memory};")
  lines += [f"    {line}" for line in body]
  lines.append("  }")
  return lines


def process_function(text, identifier, locals_, start):
  emulation = chosen_emulation(text, identifier)
  lines = ["void meLibOnProcess(void) {"]
  for declaration in locals_:
    lines += [f"  {declaration['text']}", ""]
  last = len(emulation["steps"]) - 1
  for index, ((name, actions), pairs, memory) in enumerate(zip(emulation["steps"], emulation["pairs"], emulation["memories"])):
    body = [f"vmeDebugFillWith(VME_BASE_BUFFERS{fill_offset(start)});"] if index == last else []
    lines += call_block(name, actions, pairs, memory, body)
  lines += ["", "  meFinish = 1;", "", "  while (1) {", "  }", "}"]
  return "\n".join(lines)


def fill_offset(start):
  return f" + {start} * 4" if start else ""


def emulation_parts(text, identifier, others):
  arrays, macros = declared_parts(text, identifier, others)
  memories = memory_declarations(text, identifier)
  declared = arrays + memories
  return {
    "macros": macros,
    "globals": [declaration["text"] for declaration in declared if declaration["where"] == "global"],
    "locals": [declaration for declaration in declared if declaration["where"] == "local"],
    "kernels": kernel_text(text, identifier),
  }


def extract_source(text, identifier, others=(), start=0, words=32):
  check_window(start, words)
  parts = emulation_parts(text, identifier, others)
  sections = [prologue(words)]
  if parts["macros"]:
    sections.append("\n".join(parts["macros"]))
  if parts["globals"]:
    sections.append("\n\n".join(parts["globals"]))
  sections.append(parts["kernels"])
  sections.append(process_function(text, identifier, parts["locals"], start))
  sections.append(MAIN)
  return "\n\n".join(sections) + "\n"
