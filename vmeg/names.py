import os

SUFFIXES = ((".vmeg.cpp", ".cpp"), (".vmeg.c", ".c"))


def globals_header(path):
  name = os.path.basename(path)
  for source, _ in SUFFIXES:
    if name.endswith(source):
      return name[:-len(source)] + ".gen.h"
  return os.path.splitext(name)[0] + ".gen.h"
