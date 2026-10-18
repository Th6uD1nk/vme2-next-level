import tempfile

from emu.extract import host_program
from emu.host import build_program, run_program
from emu.machine import Emulator
from emu.trace import replay


def run_emulation(text, identifier, trace_path=None):
  with tempfile.TemporaryDirectory() as folder:
    trace = run_program(build_program(host_program(text, identifier), folder))
  if trace_path is not None:
    with open(trace_path, "w", encoding="utf-8") as f:
      f.write(trace)
  emulator = Emulator()
  replay(emulator, trace)
  return emulator
