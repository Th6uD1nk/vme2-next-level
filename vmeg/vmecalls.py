import re

ENABLE = "\x00enable\x00"
DISABLE = "\x00disable\x00"

GAP = re.compile(r"[ \t]*" + re.escape(DISABLE) + r"[ \t]*\n?((?:[ \t\r\n]|#line [^\n]*\n|[{}])*?)[ \t]*" + re.escape(ENABLE) + r"[ \t]*\n?")


def finish_calls(text):
  return GAP.sub(r"\1", text).replace(ENABLE, "vmeLibEnable();").replace(DISABLE, "vmeLibDisable();")
