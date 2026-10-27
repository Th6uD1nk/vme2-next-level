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
