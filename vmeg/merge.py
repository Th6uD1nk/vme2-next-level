import os

from vmeg.names import globals_header
from vmeg.parser import upload_text


def read_summary(text, name):
  rows = text.split("\n")
  if rows and rows[-1] == "":
    rows.pop()
  if not rows or rows[0].split("\t") != ["vmeg-info", "1"]:
    raise ValueError(f"{name}:1: not a vmeg-info file of version 1")
  info = {"source": name, "globals": [], "on_process": []}
  for number, row in enumerate(rows[1:], 2):
    fields = row.split("\t")
    if fields[0] == "source" and len(fields) == 2:
      info["source"] = fields[1]
    elif fields[0] == "global" and len(fields) == 6 and fields[2].isdigit() and fields[5].isdigit():
      info["globals"].append((fields[1], int(fields[2]), fields[3], fields[4], int(fields[5])))
    elif fields[0] == "on-process" and len(fields) == 2 and fields[1].isdigit():
      info["on_process"].append(int(fields[1]))
    else:
      raise ValueError(f"{name}:{number}: unknown or malformed line")
  return info


def merge_globals(infos):
  seen = {}
  merged = []
  for info in infos:
    for target, count, offset, source, line in info["globals"]:
      key = (target, offset or "0")
      first = seen.get(key)
      if first is None:
        seen[key] = (count, source, info["source"], line)
        merged.append((target, count, offset, source))
      elif first[:2] != (count, source):
        name = target.replace("_", "").lower()
        raise ValueError(f"{info['source']}:{line}: {name} is already loaded at the same offset by {first[2]}:{first[3]} with a different source or size")
  return merged


def check_on_process(infos):
  defined = []
  first_global = None
  for info in infos:
    defined += [(info["source"], line) for line in info["on_process"]]
    if first_global is None and info["globals"]:
      first_global = (info["source"], info["globals"][0][4])
  if len(defined) > 1:
    places = " and ".join(f"{source}:{line}" for source, line in defined)
    raise ValueError(f"meLibOnProcess is defined more than once: {places}")
  if not defined and first_global is not None:
    raise ValueError(f"{first_global[0]}:{first_global[1]}: global buffers need a function meLibOnProcess in one of the files, none defines it")


def merged_file(merged):
  rows = [f"extern volatile u32 {source}[];" for source in dict.fromkeys(source for _, _, _, source in merged)]
  rows.append("static void vmegUploadGlobals(void) {")
  rows += [f"  {upload_text(*entry)}" for entry in merged]
  rows.append("}")
  return "\n".join(rows) + "\n"


def merge_command(paths):
  infos = []
  for path in paths:
    with open(path, encoding="utf-8", newline="") as f:
      infos.append(read_summary(f.read(), path))
  merged = merge_globals(infos)
  check_on_process(infos)
  for path, info in zip(paths, infos):
    if info["on_process"]:
      target = os.path.join(os.path.dirname(path), globals_header(info["source"]))
      with open(target, "w", encoding="utf-8", newline="") as f:
        f.write(merged_file(merged))
