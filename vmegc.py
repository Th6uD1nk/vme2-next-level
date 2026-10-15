import argparse
import os
import re
import sys

SUFFIX = ".vmeg.c"

IDENT = re.compile(r"[A-Za-z_]\w*")
NUMBER = re.compile(r"[0-9][\w.]*")
STRING = re.compile(r'"(?:[^"\\\n]|\\[\s\S])*"|\'(?:[^\'\\\n]|\\[\s\S])*\'')
BLANK = re.compile(r"(?:\s+|//[^\n]*|/\*.*?\*/)+", re.S)


def tokens(text):
  pos = 0
  size = len(text)
  while pos < size:
    m = BLANK.match(text, pos)
    if m:
      pos = m.end()
      continue
    if text.startswith("/*", pos):
      line = text.count("\n", 0, pos) + 1
      raise ValueError(f"line {line}: unterminated comment")
    m = STRING.match(text, pos)
    if m:
      yield ("str", m.group(), m.start(), m.end())
      pos = m.end()
      continue
    if text[pos] in "\"'":
      line = text.count("\n", 0, pos) + 1
      raise ValueError(f"line {line}: unterminated literal")
    m = IDENT.match(text, pos)
    kind = "ident"
    if not m:
      m = NUMBER.match(text, pos)
      kind = "num"
    if not m:
      yield ("punct", text[pos], pos, pos + 1)
      pos += 1
      continue
    yield (kind, m.group(), m.start(), m.end())
    pos = m.end()


def default_output(path):
  name = os.path.basename(path)
  if not name.endswith(SUFFIX):
    raise SystemExit(f"vmegc: input must end with {SUFFIX} (or pass -o)")
  return name[:-len(SUFFIX)] + ".c"


def main(argv=None):
  parser = argparse.ArgumentParser(prog="vmegc")
  parser.add_argument("input")
  parser.add_argument("-o", "--output")
  args = parser.parse_args(argv)

  output = args.output or default_output(args.input)

  with open(args.input, encoding="utf-8", newline="") as f:
    text = f.read()
  with open(output, "w", encoding="utf-8", newline="") as f:
    f.write(text)
  return 0


if __name__ == "__main__":
  sys.exit(main())
