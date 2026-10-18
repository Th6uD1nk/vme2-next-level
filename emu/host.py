import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY = os.path.join(ROOT, "me-custom-core")
LIBRARY_FILES = ("vme-lib.c", "vme-lib.h", "vme-fu-opcodes.h", "me-lib.h", "me-core-mapper.h")


def library_folder():
  missing = [name for name in LIBRARY_FILES if not os.path.isfile(os.path.join(LIBRARY, name))]
  if missing:
    raise ValueError(f"the library folder {LIBRARY} lacks {', '.join(missing)}, the submodule is probably empty (git submodule update --init me-custom-core)")
  return LIBRARY
