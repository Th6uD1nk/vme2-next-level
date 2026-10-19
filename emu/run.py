import tempfile

from emu.extract import chosen_emulation, host_program
from emu.listing import emulations
from emu.host import build_program, run_program
from emu.machine import Emulator
from emu.trace import replay


def choose_source(sources, identifier):
  having = [(path, text) for path, text in sources if any(emulation["id"] == identifier for emulation in emulations(text))]
  if len(having) == 1:
    return having[0]
  if len(having) > 1:
    raise ValueError(f"the @emulate \"{identifier}\" is in {' and '.join(path for path, _ in having)}")
  if len(sources) == 1:
    chosen_emulation(sources[0][1], identifier)
  known = ", ".join(emulation["id"] for _, text in sources for emulation in emulations(text))
  raise ValueError(f"no @emulate with the id '{identifier}' ({known if known else 'there is no @emulate in these files'})")


def run_emulation(text, identifier, trace_path=None, others=()):
  with tempfile.TemporaryDirectory() as folder:
    trace = run_program(build_program(host_program(text, identifier, others), folder))
  if trace_path is not None:
    with open(trace_path, "w", encoding="utf-8") as f:
      f.write(trace)
  emulator = Emulator()
  replay(emulator, trace)
  return emulator
