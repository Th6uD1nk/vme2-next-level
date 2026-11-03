import re

USE = re.compile(r"([A-Za-z_]\w*)=([A-Za-z_]\w*)")


def parse_uses(parser, values):
  uses = []
  for value in values:
    found = USE.fullmatch(value)
    if found is None:
      parser.error(f"--use takes NAME=NAME, for example --use input=other (got '{value}')")
    if any(found.group(1) == replaced for replaced, _ in uses):
      parser.error(f"--use: the array {found.group(1)} is replaced twice")
    uses.append(found.groups())
  return uses
