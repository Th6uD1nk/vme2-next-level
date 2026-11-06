import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from generate import load

DEFAULT = "0x000-0x0ff"


def word(value):
  value &= 0xffffff
  return (value - 0x1000000 if value & 0x800000 else value) & 0xffffffff


def parse(text):
  found = {}
  for block in text.split("\n\n"):
    match = re.match(r"Buffer: BASE ([0-3])\n", block)
    if match:
      found[int(match.group(1))] = [int(w, 16) for w in re.findall(r"0x[0-9a-f]{8}", block)][:16]
  return found


def emulate(source, identifier):
  run = subprocess.run([sys.executable, os.path.join(ROOT, "vmeemu.py"), "--run", identifier, source], capture_output=True, text=True)
  return None if run.returncode else run.stdout, run.stderr.strip()


def check(module, source, entry):
  identifier = entry["id"]
  text, error = emulate(source, identifier)
  if text is None:
    return f"{identifier}: {error}"
  found = parse(text)
  expected = [word(entry["expected"](f, b)) for f, b in zip(module.IN0, module.IN1)]
  if len(found) < 4:
    return f"{identifier}: 4 buffers BASE are needed ({len(found)} in the output)"
  for pe in range(4):
    for index, (got, want) in enumerate(zip(found[pe], expected)):
      if got != want:
        return f"{identifier}: BASE_{pe} word {index}: got 0x{got:08x}, expected 0x{want:08x}"
  return None


def main(arguments):
  module = load(DEFAULT)
  source = os.path.join(HERE, f"opcodes-{DEFAULT}.vmeg.cpp")
  chosen = [entry for entry in module.SPECS if not arguments or entry["id"] in arguments]
  with ThreadPoolExecutor(os.cpu_count()) as pool:
    problems = list(pool.map(lambda entry: check(module, source, entry), chosen))
  for entry, problem in zip(chosen, problems):
    print(problem or f"{entry['id']}: ok")
  return 1 if any(problems) else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
