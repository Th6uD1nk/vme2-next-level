import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY = os.path.join(ROOT, "me-core-mapper")
NATIVE = os.path.join(ROOT, "vmee", "native")
SUBSTITUTES = (("emu-me-lib.h", "me-lib.h"), ("emu-me-core-mapper.h", "me-core-mapper.h"))
RUN_TIMEOUT = 60
COMPILER_FLAGS = ("-m32", "-no-pie", "-std=c++11", "-fpermissive", "-w", "-x", "c++")
LIBRARY_FILES = ("vme-lib.c", "vme-lib.h", "vme-fu-opcodes.h", "me-lib.h", "me-core-mapper.h")


def library_folder():
  missing = [name for name in LIBRARY_FILES if not os.path.isfile(os.path.join(LIBRARY, name))]
  if missing:
    raise ValueError(f"the library folder {LIBRARY} lacks {', '.join(missing)}, the submodule is probably empty (git submodule update --init me-core-mapper)")
  return LIBRARY


def cache_key(library):
  h = hashlib.sha256()
  h.update("\0".join(COMPILER_FLAGS).encode())
  for base in (library, NATIVE):
    for root, dirs, files in os.walk(base):
      dirs[:] = sorted(d for d in dirs if d != ".git")
      for name in sorted(files):
        path = os.path.join(root, name)
        h.update(os.path.relpath(path, ROOT).encode() + b"\0")
        with open(path, "rb") as f:
          h.update(f.read())
  return h.hexdigest()


def cached_objects(library):
  bucket = os.path.join(tempfile.gettempdir(), "vmee-obj-cache", cache_key(library))
  objects = (os.path.join(bucket, "emu-me-core-mapper.o"), os.path.join(bucket, "vme-lib.o"))
  if all(os.path.isfile(path) for path in objects):
    return objects
  os.makedirs(bucket, exist_ok=True)
  with tempfile.TemporaryDirectory(dir=bucket) as staging:
    os.symlink(library, os.path.join(staging, "me-core-mapper"))
    for original, name in SUBSTITUTES:
      shutil.copy(os.path.join(NATIVE, original), os.path.join(staging, name))
    shutil.copy(os.path.join(library, "vme-lib.c"), staging)
    sources = (os.path.join(NATIVE, "emu-me-core-mapper.cpp"), os.path.join(staging, "vme-lib.c"))
    for src, dst in zip(sources, objects):
      tmp = os.path.join(staging, os.path.basename(dst))
      done = subprocess.run(["g++", *COMPILER_FLAGS, "-I" + staging, "-I" + NATIVE, "-c", src, "-o", tmp], capture_output=True, text=True)
      if done.returncode:
        raise ValueError(f"the host library does not build:\n{done.stderr.rstrip()}")
      os.replace(tmp, dst)
  return objects


def build_program(source, folder):
  library = library_folder()
  if shutil.which("g++") is None:
    raise ValueError("g++ is needed to build the host program and was not found")
  os.symlink(library, os.path.join(folder, "me-core-mapper"))
  for original, name in SUBSTITUTES:
    shutil.copy(os.path.join(NATIVE, original), os.path.join(folder, name))
  program = os.path.join(folder, "program.cpp")
  with open(program, "w", encoding="utf-8") as f:
    f.write(source)
  executable = os.path.join(folder, "program")
  command = ["g++", *COMPILER_FLAGS, "-I" + folder, "-I" + NATIVE, program, "-x", "none", *cached_objects(library), "-o", executable]
  done = subprocess.run(command, capture_output=True, text=True)
  if done.returncode:
    raise ValueError(f"the host program does not build:\n{done.stderr.rstrip()}")
  return executable


def run_program(executable, arguments=()):
  try:
    done = subprocess.run([executable, *arguments], capture_output=True, text=True, timeout=RUN_TIMEOUT)
  except subprocess.TimeoutExpired:
    raise ValueError(f"the host program did not finish in {RUN_TIMEOUT} seconds") from None
  if done.returncode:
    raise ValueError(f"the host program failed with the exit code {done.returncode}:\n{done.stderr.rstrip()}")
  return done.stdout
