import os
import tempfile

from vmee.extract import chosen_emulation, host_program
from vmee.listing import emulations
from vmee.host import build_program, run_program
from vmee.machine import Emulator
from vmee.trace import replay


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


def array_table(trace):
  table = {}
  for line in trace.splitlines():
    parts = line.split()
    if parts[:2] == ["#", "array"]:
      table[parts[2]] = (int(parts[3], 16), int(parts[4]))
  return table


def arrays_text(emulator, table):
  lines = []
  for name, (address, count) in table.items():
    first = emulator.memory_address(address)
    words = [emulator.memory.get(first + 4 * index) for index in range(count)]
    if any(word is not None for word in words):
      lines.append(name + " " + " ".join("-" if word is None else "%x" % word for word in words))
  return "".join(line + "\n" for line in lines)


def run_emulation(text, identifier, trace_path=None, others=(), compat=None, uses=()):
  steps = len(chosen_emulation(text, identifier)["steps"])
  emulator = Emulator()
  traces = []
  with tempfile.TemporaryDirectory() as folder:
    executable = build_program(host_program(text, identifier, others, compat, uses), folder)
    path = os.path.join(folder, "arrays.txt")
    arguments = ()
    for step in range(steps):
      trace = run_program(executable, (str(step), *arguments))
      traces.append(trace)
      replay(emulator, trace)
      with open(path, "w", encoding="utf-8") as f:
        f.write(arrays_text(emulator, array_table(trace)))
      arguments = (path,)
  if trace_path is not None:
    with open(trace_path, "w", encoding="utf-8") as f:
      f.write("".join(traces))
  return emulator
