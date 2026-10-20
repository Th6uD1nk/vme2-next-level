ENABLE = "\x00enable\x00"
DISABLE = "\x00disable\x00"


def finish_calls(text):
  return text.replace(ENABLE, "vmeLibEnable();").replace(DISABLE, "vmeLibDisable();")
