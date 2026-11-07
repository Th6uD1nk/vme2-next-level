import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def listed_ids(source):
  run = subprocess.run([sys.executable, os.path.join(ROOT, "vmeemu.py"), "--list", source], capture_output=True, text=True)
  if run.returncode:
    raise ValueError(run.stderr.strip() or "vmeemu --list failed")
  return re.findall(r'^emulate "([^"]+)"', run.stdout, flags=re.M)


def chosen_ids(source, wanted):
  found = listed_ids(source)
  if not found:
    raise ValueError("the file has no @emulate")
  if not wanted:
    return found
  unknown = [identifier for identifier in wanted if identifier not in found]
  if unknown:
    raise ValueError("not an @emulate id of the file: " + ", ".join(unknown))
  return wanted
