from vmeg.host import declarator_names

BOUNDARIES = (";", "}", "{")


def statement_span(toks, i):
  first = i
  while first > 0 and not (toks[first - 1][0] == "pp" or toks[first - 1][0] == "punct" and toks[first - 1][1] in BOUNDARIES):
    first -= 1
  nest = 0
  for last in range(i, len(toks)):
    kind, value, _, _ = toks[last]
    if kind == "punct" and value in "([{":
      nest += 1
    elif kind == "punct" and value in ")]}":
      nest -= 1
    elif kind == "punct" and value == ";" and nest == 0:
      return first, last
  return first, len(toks) - 1


def declarations(text, toks, depth_wanted):
  found = []
  depth = 0
  for i, (kind, value, _, _) in enumerate(toks):
    if kind == "punct" and value == "{":
      depth += 1
    elif kind == "punct" and value == "}":
      depth -= 1
    elif kind == "ident" and value == "Buffer" and depth == depth_wanted:
      first, last = statement_span(toks, i)
      statement = toks[first:last + 1]
      found.append({
        "names": declarator_names(toks, i),
        "text": text[statement[0][2]:statement[-1][3]],
        "line": text.count("\n", 0, statement[0][2]) + 1,
        "extern": any(kind == "ident" and value == "extern" for kind, value, _, _ in statement),
      })
  return found
