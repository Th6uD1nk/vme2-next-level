import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY = os.path.join(ROOT, "me-custom-core")
NATIVE = os.path.join(ROOT, "emu", "native")
SUBSTITUTES = (("emu-me-lib.h", "me-lib.h"), ("emu-me-core-mapper.h", "me-core-mapper.h"))
RUN_TIMEOUT = 60
COMPILER_FLAGS = ("-m32", "-no-pie", "-std=c++11", "-fpermissive", "-w", "-x", "c++")
LIBRARY_FILES = ("vme-lib.c", "vme-lib.h", "vme-fu-opcodes.h", "me-lib.h", "me-core-mapper.h")


def library_folder():
  missing = [name for name in LIBRARY_FILES if not os.path.isfile(os.path.join(LIBRARY, name))]
  if missing:
    raise ValueError(f"the library folder {LIBRARY} lacks {', '.join(missing)}, the submodule is probably empty (git submodule update --init me-custom-core)")
  return LIBRARY


def build_program(source, folder):
  library = library_folder()
  if shutil.which("g++") is None:
    raise ValueError("g++ is needed to build the host program and was not found")
  os.symlink(library, os.path.join(folder, "me-core-mapper"))
  for original, name in SUBSTITUTES:
    shutil.copy(os.path.join(NATIVE, original), os.path.join(folder, name))
  shutil.copy(os.path.join(library, "vme-lib.c"), folder)
  program = os.path.join(folder, "program.cpp")
  with open(program, "w", encoding="utf-8") as f:
    f.write(source)
  executable = os.path.join(folder, "program")
  command = ["g++", *COMPILER_FLAGS, "-I" + folder, "-I" + NATIVE, program, os.path.join(NATIVE, "emu-me-core-mapper.cpp"), os.path.join(folder, "vme-lib.c"), "-o", executable]
  done = subprocess.run(command, capture_output=True, text=True)
  if done.returncode:
    raise ValueError(f"the host program does not build:\n{done.stderr.rstrip()}")
  return executable


def run_program(executable):
  try:
    done = subprocess.run([executable], capture_output=True, text=True, timeout=RUN_TIMEOUT)
  except subprocess.TimeoutExpired:
    raise ValueError(f"the host program did not finish in {RUN_TIMEOUT} seconds") from None
  if done.returncode:
    raise ValueError(f"the host program failed with the exit code {done.returncode}:\n{done.stderr.rstrip()}")
  return done.stdout
