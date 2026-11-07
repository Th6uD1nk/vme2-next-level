import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

from vmegt.ids import ROOT


def tool_environment(pspdev):
  env = dict(os.environ)
  env["PSPDEV"] = pspdev
  env["PATH"] = os.path.join(pspdev, "bin") + os.pathsep + env.get("PATH", "")
  return env


def build(source, identifier, work, pspdev, start, words, uses):
  folder = os.path.join(work, identifier)
  os.makedirs(folder, exist_ok=True)
  env = tool_environment(pspdev)
  arguments = [
    "cmake", "-S", os.path.join(ROOT, "samples", "vmeh"), "-B", folder,
    f"-DVMEH_SOURCE={os.path.relpath(source, ROOT)}", f"-DVMEH_ID={identifier}",
    f"-DVMEH_BUFFERS_START={start}", f"-DVMEH_BUFFERS_WORDS={words}",
    f"-DVMEH_USE={';'.join(uses)}",
  ]
  configured = subprocess.run(arguments, capture_output=True, text=True, env=env)
  if configured.returncode:
    return None, configured.stdout + configured.stderr
  made = subprocess.run(["make", "-C", folder], capture_output=True, text=True, env=env)
  program = os.path.join(folder, "vme.prx")
  if made.returncode or not os.path.exists(program):
    return None, made.stdout + made.stderr
  return program, ""


def build_all(source, ids, work, pspdev, jobs, start, words, uses):
  with ThreadPoolExecutor(max(1, jobs)) as pool:
    return list(pool.map(lambda identifier: build(source, identifier, work, pspdev, start, words, uses), ids))
