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


def buffers(identifier):
  run = subprocess.run([sys.executable, os.path.join(ROOT, "vmeemu.py"), "--run", identifier, SOURCE], capture_output=True, text=True)
  if run.returncode:
    return None, run.stderr.strip()
  blocks = [block for block in run.stdout.split("\n\n") if block.startswith("Buffer: BASE")]
  return [[int(w, 16) for w in re.findall(r"0x[0-9a-f]{8}", block)][:16] for block in blocks], None


def check(kernel):
  identifier, expected = kernel
  found, error = buffers(identifier)
  if error:
    return f"{identifier}: {error}"
  if len(found) < 4:
    return f"{identifier}: {len(found)} buffers BASE found, expected 4"
  for pe, words in enumerate(found[:4]):
    for index, (got, want) in enumerate(zip(words, expected)):
      if got != word(want):
        return f"{identifier}: BASE_{pe} word {index}: got 0x{got:08x}, expected 0x{word(want):08x}"
  return None


def main(names):
  chosen = [kernel for kernel in KERNELS if not names or kernel[0] in names]
  with ThreadPoolExecutor(os.cpu_count()) as pool:
    problems = list(pool.map(check, chosen))
  for (identifier, _), problem in zip(chosen, problems):
    print(problem or f"{identifier}: ok")
  return 1 if any(problems) else 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
