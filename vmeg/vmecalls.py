import re

ENABLE = "\x00enable\x00"
DISABLE = "\x00disable\x00"

WAIT = re.compile(r"\x00wait:\w+\x00")
WAIT_CALL = "meCoreDMACPrimWaitTransferFinish();"

SAME_WAIT = re.compile(r"[ \t]*\x00wait:(\w+)\x00[ \t]*\n?((?:[ \t\r\n]|#line [^\n]*\n)*?)(?=[ \t]*\1\()")

GAP = re.compile(r"[ \t]*" + re.escape(DISABLE) + r"[ \t]*\n?((?:[ \t\r\n]|#line [^\n]*\n|[{}])*?)[ \t]*" + re.escape(ENABLE) + r"[ \t]*\n?")


def wait_marker(name):
  return f"\x00wait:{name}\x00"


def finish_calls(text):
  return WAIT.sub(WAIT_CALL, SAME_WAIT.sub(r"\2", GAP.sub(r"\1", text))).replace(ENABLE, "vmeLibEnable();").replace(DISABLE, "vmeLibDisable();")
