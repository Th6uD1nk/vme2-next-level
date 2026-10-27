import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(HERE, "opcode-checker.vmeg.cpp")

KERNELS = [
  ("add", [0, 2, 1, 31, 511, 32768, 0, -8388608, 0, 0, 0, 8388607, 8388607, 8388607, 123, -77]),
  ("add_ofa", [5, 7, 6, 36, 516, -8355842, 5, -8388603, 5, 5, 5, 8388607, -8388604, -8388604, 128, -100]),
  ("add_cst", [3, 4, 5, 0, -1, 258, -8388606, -8388608, 8388607, -8388605, -8388603, 5592408, 2796205, 103, -97, 2]),
  ("sub", [0, 0, -1, 10, 255, -8388608, 0, 8388607, -8388607, 0, 2796203, -2796203, 8388607, 123, -123, 2]),
  ("subacst", [7, 14, 0, 14, 157, -8388607, -8388601, -8388594, -8388602, 7, -8388602, 7, 7, -7, 4102, -4088]),
  ("subshr", [0, -1, 8, 10, 11, 1, 1, -320, -2097151, 2097152, 4194304, 6990507, 7689558, -7689558, 0, 1]),
  ("and", [0, -1, 5592405, 0, 0, -986896, 8388607, -8388608, 1, -2, 13312, 51968, 65280, 0, 255, 0]),
  ("or", [0, -1, 8388607, -1, 1048575, -986896, 8388607, -8388607, 3, -1, -52138, -1192961, 65535, -1, -1, -1]),
  ("xor", [0, 0, 0, -1, 0, -1, 0, -1, -2, -1, -1193047, -1193047, 0, -1, -1, 5592405]),
  ("nand", [-1, 0, -5592406, -1, -1, -1, -8388608, 8388607, -2, -8388607, -13313, -51969, -65281, -1, -256, -1]),
  ("nor", [-1, 0, -8388608, 0, -1048576, 986895, -8388608, 8388606, -4, 0, 52137, 1192960, -65536, 0, 0, 0]),
  ("not", [-1, 0, -2, 1, -5592406, 5592405, -986896, 986895, -8388608, 8388607, -8388607, 8388606, -256, 255, -1193047, 1193046]),
  ("and_cst", [0, 255, 255, 0, 255, 86, 255, 0, 0, 255, 85, 170, 128, 127, 128, 127]),
  ("or_cst", [128, -1, 128, 255, 255, 384, 384, 5592533, -5592406, -1, -128, -128, 8388607, -8388480, 129, -2]),
  ("xor_cst", [85, -86, 0, 255, 170, 5592320, -5592321, 8388522, -8388523, 84, -85, 341, 256, -1, 1192963, -1192964]),
  ("nand_cst", [-1, -256, -256, -1, -256, -129, -128, -256, -1, -1, -256, -86, -171, -16, -241, -2]),
  ("nor_cst", [-16, 0, -16, -32, -256, -256, -272, -32, -8388608, 8388592, 0, 16, -5592416, 5592400, -1193056, 1193040]),
  ("xnor_cst", [-86, 85, -1, -256, -171, -342, -257, -5592321, 5592320, -8388523, 8388522, -85, 84, 0, -1192964, 1192963]),
  ("clamp", [-100, -100, -100, -99, -1, 0, 1, 99, 100, 100, 100, 100, -100, 100, -100, 50]),
  ("mul", [0, 1, 1, -4, 9, 10000, -10000, 0, 0, -2, -8388608, 1, -5592406, -2, 65025, -65536]),
  ("mul_shr", [16, 0, -16, -1, 625, -625, 0, -1, 1048576, 0, -1048576, -8388608, 5592405, -5592406, -8192, 0]),
  ("mac", [1, 3, 6, 10, 9, 7, 4, 0, 300, -300, 600, -600, -600, -600, -600, -602]),
  ("acc", [1, 3, 6, 10, 9, 7, 4, 0, 100, 0, 4096, 0, 8388592, -8388592, 32, 2080]),
]


def word(value):
  return value & 0xffffffff


def parse(text):
  found = {}
  for block in text.split("\n\n"):
    match = re.match(r"Buffer: BASE ([0-3])\n", block)
    if match:
      found[int(match.group(1))] = [int(w, 16) for w in re.findall(r"0x[0-9a-f]{8}", block)][:16]
  return found


def emulate(identifier):
  run = subprocess.run([sys.executable, os.path.join(ROOT, "vmeemu.py"), "--run", identifier, SOURCE], capture_output=True, text=True)
  return None if run.returncode else run.stdout, run.stderr.strip()


def check(kernel, log=None):
  identifier, expected = kernel
  text, error = emulate(identifier)
  if text is None:
    return f"{identifier}: {error}"
  emulated = parse(text)
  if log is None:
    found, reference, names = emulated, {pe: [word(v) for v in expected] for pe in range(4)}, ("got", "expected")
  else:
    found, reference, names = parse(log), emulated, ("PSP", "emulator")
  if len(found) < 4 or len(reference) < 4:
    return f"{identifier}: 4 buffers BASE are needed ({len(found)} in the log, {len(reference)} in the reference)"
  for pe in range(4):
    for index, (got, want) in enumerate(zip(found[pe], reference[pe])):
      if got != want:
        return f"{identifier}: BASE_{pe} word {index}: {names[0]} 0x{got:08x}, {names[1]} 0x{want:08x}"
  return None


def main(arguments):
  log = None
  if arguments[:1] == ["--log"]:
    with open(arguments[1], encoding="utf-8") as f:
      log = f.read()
    arguments = arguments[2:]
    if len(arguments) != 1:
      print("--log goes with one kernel id")
      return 2
  chosen = [kernel for kernel in KERNELS if not arguments or kernel[0] in arguments]
  with ThreadPoolExecutor(os.cpu_count()) as pool:
    problems = list(pool.map(lambda kernel: check(kernel, log), chosen))
  for (identifier, _), problem in zip(chosen, problems):
    print(problem or f"{identifier}: ok")
  return 1 if any(problems) else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
