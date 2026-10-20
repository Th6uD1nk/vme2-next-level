import re

ENABLE = "\x00enable\x00"
DISABLE = "\x00disable\x00"

GAP = re.compile(re.escape(DISABLE) + r"((?:[ \t\r\n]|#line [^\n]*\n|[{}])*)" + re.escape(ENABLE))


def finish_calls(text):
  return GAP.sub(r"\1", text).replace(ENABLE, "vmeLibEnable();").replace(DISABLE, "vmeLibDisable();")
