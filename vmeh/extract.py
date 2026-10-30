from vmee.extract import chosen_emulation, declared_parts, memory_declarations
from vmee.listing import emulations
from vmee.memory import check_window
from vmeg.blocks import find_blocks, kernel_name


def prologue(words, commands=False):
  shared = "meLibSetSharedUncached32(4);" if commands else "meLibSetSharedUncached32(1);"
  command = "\n#define meCommand (meLibSharedMemory[1])\n#define meStart (meLibSharedMemory[2])\n#define meCount (meLibSharedMemory[3])" if commands else ""
  debug = "\n#include <pspdebug.h>" if commands else ""
  return f"""#include <pspctrl.h>{debug}
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

{shared}
#define meFinish (meLibSharedMemory[0]){command}"""


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


NAVIGATION = """static const char* const vmehNames[] = {NAMES};

#define vmehCount ((int)(sizeof(vmehNames) / sizeof(vmehNames[0])))

static int vmehWords = WORDS;

static void vmehPlay(const int index) {
  pspDebugScreenClear();
  pspDebugScreenSetXY(0, 0);
  pspDebugScreenPrintf("%03d - %s", index + 1, vmehNames[index]);

  meFinish = 0;
  meCommand = index + 1;
  while (!meFinish) {
    sceKernelDelayThread(100);
  }

  vmeDebugTouch();
  FILE* const log = fopen("./log.txt", "a");
  if (log) {
    fprintf(log, "Kernel: %03d - %s\\n\\n", index + 1, vmehNames[index]);
    fclose(log);
  }
  vmeDebugDumpWindowCount(vmehWords);

  sceKernelDelayThread(500000);
}

static void vmehReadConfig(int* const start, int* const count) {
  FILE* const config = fopen("./config.txt", "r");
  if (!config) {
    return;
  }

  char line[64];
  while (fgets(line, sizeof(line), config)) {
    int value;
    if (sscanf(line, "start: %d", &value) == 1) {
      *start = value;
    } else if (sscanf(line, "count: %d", &value) == 1) {
      *count = value;
    }
  }
  fclose(config);
}

int main() {
  scePowerSetClockFrequency(333, 333, 166);
  pspDebugScreenInit();

  int start = START;
  vmehReadConfig(&start, &vmehWords);
  vmeDebugSetupBuffersCount(vmehWords);

  meLibDefaultInit();

  meStart = start;
  meCount = vmehWords;

  int index = 0;
  vmehPlay(index);

  SceCtrlData pad;
  while (1) {
    sceCtrlPeekBufferPositive(&pad, 1);
    if ((pad.Buttons & PSP_CTRL_LEFT) && index > 0) {
      vmehPlay(--index);
    } else if ((pad.Buttons & PSP_CTRL_RIGHT) && index < vmehCount - 1) {
      vmehPlay(++index);
    }
    sceKernelDelayThread(10000);
  }
}"""


def navigation_main(identifiers, start, words):
  return NAVIGATION.replace("NAMES", ", ".join(f'"{identifier}"' for identifier in identifiers)).replace("WORDS", str(words)).replace("START", str(start))


def kernel_texts(text, identifier):
  names = chosen_emulation(text, identifier)["kernels"]
  blocks = find_blocks(text)
  return [(name, text[block[1]:block[3]]) for name in names for block in blocks if block[0] == "kernel" and kernel_name(text, block) == name]


def call_block(name, actions, pairs, memory, body):
  lines = [f"  @kernel {name} {' | '.join(actions)} {{"]
  if pairs:
    lines.append("    .params = { " + ", ".join(f"{key}: {value}" for key, value in pairs) + " };")
  if memory:
    lines.append(f"    .memory = {memory};")
  lines += [f"    {line}" for line in body]
  lines.append("  }")
  return lines


def process_function(text, identifier, locals_, start, name="meLibOnProcess", looped=True):
  emulation = chosen_emulation(text, identifier)
  lines = [f"void {name}(void) {{"]
  for declaration in locals_:
    lines += [f"  {declaration['text']}", ""]
  last = len(emulation["steps"]) - 1
  for index, ((name, actions), pairs, memory, statements) in enumerate(zip(emulation["steps"], emulation["pairs"], emulation["memories"], emulation["bodies"])):
    fill = f"vmeDebugFillWith(VME_BASE_BUFFERS{fill_offset(start)});" if looped else "vmeDebugFillWithCount(VME_BASE_BUFFERS + meStart * 4, meCount);"
    body = [line for statement in statements for line in statement.splitlines()] + ([fill] if index == last else [])
    lines += call_block(name, actions, pairs, memory, body)
  lines += ["", "  meFinish = 1;", "", "  while (1) {", "  }", "}"] if looped else ["}"]
  return "\n".join(lines)


def fill_offset(start):
  return f" + {start} * 4" if start else ""


def on_process_loop(count):
  cases = "".join(f"      case {index}:\n        vmehRun{index}();\n        break;\n" for index in range(1, count + 1))
  return f"""void meLibOnProcess(void) {{
  while (1) {{
    while (!meCommand) {{
    }}

    const int command = meCommand;
    meCommand = 0;

    vmeLibEnable();
    vmeLibWipe();
    vmeLibDisable();

    switch (command) {{
{cases}    }}

    meFinish = 1;
  }}
}}"""


def emulation_parts(text, identifier, others):
  arrays, macros = declared_parts(text, identifier, others)
  memories = memory_declarations(text, identifier)
  declared = arrays + memories
  return {
    "macros": macros,
    "globals": [declaration["text"] for declaration in declared if declaration["where"] == "global"],
    "locals": [declaration for declaration in declared if declaration["where"] == "local"],
    "kernels": kernel_texts(text, identifier),
  }


def extract_source(text, identifier, others=(), start=0, words=32):
  check_window(start, words)
  parts = emulation_parts(text, identifier, others)
  sections = [prologue(words)]
  if parts["macros"]:
    sections.append("\n".join(parts["macros"]))
  if parts["globals"]:
    sections.append("\n\n".join(parts["globals"]))
  sections.append("\n\n".join(kernel for _, kernel in parts["kernels"]))
  sections.append(process_function(text, identifier, parts["locals"], start))
  sections.append(MAIN)
  return "\n\n".join(sections) + "\n"


def merged_macros(parts):
  values = {}
  for macro in (macro for part in parts for macro in part["macros"]):
    name = macro.split()[1]
    if values.setdefault(name, macro) != macro:
      raise ValueError(f"the macro {name} has two different values in the files of the @emulate")
  return list(values.values())


def extract_program(sources, start=0, words=32):
  entries = [
    (text, emulation["id"], [other for other_index, (_, other) in enumerate(sources) if other_index != index])
    for index, (_, text) in enumerate(sources) for emulation in emulations(text)
  ]
  if not entries:
    raise ValueError("there is no @emulate in these files")
  if len(entries) == 1:
    return extract_source(*entries[0], start, words)
  check_window(start, words)
  parts = [emulation_parts(*entry) for entry in entries]
  sections = [prologue(words, True)]
  macros = merged_macros(parts)
  if macros:
    sections.append("\n".join(macros))
  globals_ = list(dict.fromkeys(declaration for part in parts for declaration in part["globals"]))
  if globals_:
    sections.append("\n\n".join(globals_))
  sections.append("\n\n".join(dict(kernel for part in parts for kernel in part["kernels"]).values()))
  for index, ((text, identifier, _), part) in enumerate(zip(entries, parts), 1):
    sections.append(process_function(text, identifier, part["locals"], start, f"vmehRun{index}", False))
  sections.append(on_process_loop(len(entries)))
  sections.append(navigation_main([identifier for _, identifier, _ in entries], start, words))
  return "\n\n".join(sections) + "\n"
