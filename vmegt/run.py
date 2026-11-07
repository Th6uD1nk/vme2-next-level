import os
import re
import shutil
import subprocess
import time


def find_pspsh(pspdev, pspsh=None):
  if pspsh:
    return pspsh
  candidate = os.path.join(pspdev, "bin", "pspsh")
  return candidate if os.path.exists(candidate) else shutil.which("pspsh")


def shell(pspsh, port, work, command, limit):
  try:
    subprocess.run([pspsh, "-p", str(port), "-n", "-e", command], capture_output=True, text=True, timeout=limit, cwd=work)
  except subprocess.TimeoutExpired:
    return False
  return True


def reset(pspsh, port, work, reset_wait):
  shell(pspsh, port, work, "reset", 20)
  time.sleep(reset_wait)


def read_log(path, timeout):
  deadline = time.time() + timeout
  size = -1
  while time.time() < deadline:
    if os.path.exists(path) and os.path.getsize(path) > 0:
      now = os.path.getsize(path)
      if now == size:
        with open(path, encoding="utf-8", errors="replace") as f:
          return f.read()
      size = now
    time.sleep(1)
  return None


def run_kernel(pspsh, port, host, work, program, identifier, reset_wait, timeout, retries):
  name = f"gk_{re.sub(r'[^A-Za-z0-9_]', '_', identifier)}.prx"
  shutil.copyfile(program, os.path.join(host, name))
  log_path = os.path.join(host, "log.txt")
  for _ in range(retries + 1):
    if os.path.exists(log_path):
      os.remove(log_path)
    shell(pspsh, port, work, f"./{name}", 60)
    text = read_log(log_path, timeout)
    reset(pspsh, port, work, reset_wait)
    if text is not None:
      return text
  return None
