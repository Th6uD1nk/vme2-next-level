from concurrent.futures import ThreadPoolExecutor
import os
import re
import subprocess
import sys

from vmegt.ids import ROOT


def parse_buffers(text, words):
  found = {}
  for block in text.split("\n\n"):
    match = re.match(r"\s*Buffer: BASE ([0-3])\n", block)
    if match:
      found[int(match.group(1))] = [int(w, 16) for w in re.findall(r"0x[0-9a-f]{8}", block)][:words]
  return found


def parse_log(text):
  found = {}
  for match in re.finditer(r"^=== kernel ([^\n]+) ===\n(.*?)(?=^=== |\Z)", text, flags=re.M | re.S):
    found[match.group(1)] = match.group(2).strip()
  return found


def compare_buffers(psp_text, emu_text, words):
  found = parse_buffers(psp_text, words)
  reference = parse_buffers(emu_text, words)
  if len(found) < 4 or len(reference) < 4:
    return f"4 buffers BASE are needed ({len(found)} in the PSP log, {len(reference)} in the emulator)"
  for pe in range(4):
    if len(found[pe]) != len(reference[pe]):
      return f"BASE_{pe} has {len(found[pe])} words in the PSP log, {len(reference[pe])} in the emulator"
    for index, (got, want) in enumerate(zip(found[pe], reference[pe])):
      if got != want:
        return f"mismatch: BASE_{pe} word {index}: PSP 0x{got:08x}, emulator 0x{want:08x}"
  return "ok"


def emulate(source, identifier, start, words, uses):
  command = [sys.executable, os.path.join(ROOT, "vmeemu.py"), "--run", identifier, source, "--buffers-start", str(start), "--buffers-words", str(words)]
  for item in uses:
    command.extend(["--use", item])
  run = subprocess.run(command, capture_output=True, text=True)
  return None if run.returncode else run.stdout, run.stderr.strip()


def check_one(source, identifier, section, start, words, uses):
  if section is None:
    return "not in log"
  if section == "no log" or section.startswith("build failed"):
    return section.splitlines()[0]
  emu_text, error = emulate(source, identifier, start, words, uses)
  if emu_text is None:
    return f"emulator failed: {error}"
  return compare_buffers(section, emu_text, words)


def check_all(source, ids, sections, jobs, start, words, uses):
  with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
    results = list(pool.map(lambda i: check_one(source, i, sections.get(i), start, words, uses), ids))
  return dict(zip(ids, results))
