import re

ENABLE = "\x00enable\x00"
DISABLE = "\x00disable\x00"
ASYNC_START = "\x00asyncstart\x00"
ASYNC_END = "\x00asyncend\x00"

WAIT = re.compile(r"\x00wait:\w+\x00")
WAIT_CALL = "meCoreDMACPrimWaitTransferFinish();"

WAITS = re.compile(r"([ \t]*\x00wait:(\w+)\x00[ \t]*\n?)((?:[ \t\r\n]|#line [^\n]*\n)*)((?=\2\())?")

GAP = re.compile(r"[ \t]*" + re.escape(DISABLE) + r"[ \t]*\n?((?:[ \t\r\n]|#line [^\n]*\n|[{}])*?)[ \t]*" + re.escape(ENABLE) + r"[ \t]*\n?")


ASYNC_GAP = re.compile(r"[ \t]*" + re.escape(ASYNC_END) + r"[ \t]*\n?((?:[ \t\r\n]|#line [^\n]*\n)*?)[ \t]*" + re.escape(ASYNC_START) + r"[ \t]*\n?")


def wait_marker(name):
  return f"\x00wait:{name}\x00"


def merge_waits(text):
  pending = False

  def merge(found):
    nonlocal pending
    if found.group(4) is not None and not pending:
      pending = True
      return found.group(3)
    pending = False
    return found.group(0)

  return WAITS.sub(merge, text)


def finish_calls(text):
  return WAIT.sub(WAIT_CALL, merge_waits(ASYNC_GAP.sub(r"\1", GAP.sub(r"\1", text)))).replace(ENABLE, "vmeLibEnable();").replace(DISABLE, "vmeLibDisable();").replace(ASYNC_START, "vmeLibStart();").replace(ASYNC_END, "vmeLibFinishAsync();")
