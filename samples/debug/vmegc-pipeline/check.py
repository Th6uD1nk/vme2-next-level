import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(HERE, "pipeline.vmeg.cpp")


def main(arguments):
  command = [
    sys.executable, os.path.join(ROOT, "vmegt.py"),
    "--check", "--buffers-words", "16",
    SOURCE, *arguments,
  ]
  return subprocess.run(command).returncode


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
