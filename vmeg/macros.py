import re

from vmeg.scanner import tokens

DIRECTIVE = re.compile(r"#\s*([A-Za-z_]\w*)\s*(.*)", re.S)
DEFINE = re.compile(r"([A-Za-z_]\w*)(\([^)]*\))?(.*)", re.S)
COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
OPENING = ("if", "ifdef", "ifndef")


def macro_events(text):
  events = []
  depth = 0
  for kind, value, start, _ in tokens(text):
    if kind != "pp":
      continue
    m = DIRECTIVE.match(value)
    if m is None:
      continue
    name, rest = m.group(1), m.group(2)
    if name in OPENING:
      depth += 1
    elif name == "endif":
      depth = max(depth - 1, 0)
    elif name == "define":
      parts = DEFINE.match(rest.strip())
      if parts is not None:
        body = " ".join(COMMENTS.sub(" ", parts.group(3).replace("\\\n", " ")).split())
        events.append({"kind": "define", "name": parts.group(1), "params": parts.group(2), "body": body, "start": start, "conditional": depth > 0})
    elif name == "undef":
      target = rest.split()
      if target:
        events.append({"kind": "undef", "name": target[0], "params": None, "body": "", "start": start, "conditional": depth > 0})
  return events
