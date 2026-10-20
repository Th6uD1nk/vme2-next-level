import re

from vmeg.scanner import tokens

DIRECTIVE = re.compile(r"#\s*([A-Za-z_]\w*)\s*(.*)", re.S)
DEFINE = re.compile(r"([A-Za-z_]\w*)(\([^)]*\))?(.*)", re.S)
COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


def macro_events(text):
  events = []
  for kind, value, start, _ in tokens(text):
    if kind != "pp":
      continue
    m = DIRECTIVE.match(value)
    if m is None or m.group(1) != "define":
      continue
    parts = DEFINE.match(m.group(2).strip())
    if parts is not None:
      body = " ".join(COMMENTS.sub(" ", parts.group(3).replace("\\\n", " ")).split())
      events.append({"kind": "define", "name": parts.group(1), "params": parts.group(2), "body": body, "start": start})
  return events
