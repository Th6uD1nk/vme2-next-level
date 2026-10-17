import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeemu import CONTEXT_WORDS, Emulator, replay


class ReplayTest(unittest.TestCase):
  def test_trace_is_played_in_order(self):
    trace = "# upload\nM 0x1000 0x10 0x800001\n\nW 0x440ff010 0x40001000\nW 0x440ff014 0x1\nW 0x440ff018 0x8000\nW 0x440ff008 0x40\n"
    emulator = Emulator()
    replay(emulator, trace)
    self.assertEqual([emulator.scratchpad.read(0x8000), emulator.scratchpad.read(0x8001)], [0x10, 0xff800001])
    with self.assertRaises(ValueError) as ctx:
      replay(Emulator(), "W 0x440ff010 0x40001000\nW 0x440ff008 0x40\n")
    self.assertEqual(str(ctx.exception), "line 2: the memory image has no word at 0x1000")


class Recorder(Emulator):
  def __init__(self):
    super().__init__()
    self.calls = []

  def load_context(self, words):
    self.calls.append("context")

  def trigger(self):
    self.calls.append("trigger")

  def clear_local_buffer(self):
    self.calls.append("clear")

  def ring_to_scratchpad(self):
    self.calls.append("ring to scratchpad")

  def ring_to_memory(self):
    self.calls.append("ring to memory")

  def mem_to_16(self):
    self.calls.append("mem to 16")

  def mem_from_16(self):
    self.calls.append("mem from 16")


class ControlTest(unittest.TestCase):
  def test_each_control_value_fires_its_own_action_only(self):
    actions = {
      0x05: "context", 0x0c: "context", 0x1d: "context", 0x18: "trigger", 0x21: "clear",
      0x40: "ring to scratchpad", 0x48: "ring to memory", 0x52: "mem to 16", 0x5a: "mem from 16",
    }
    nothing = [0x00, 0x02, 0x03, 0x04, 0x08, 0x20, 0x28, 0x42, 0x45, 0x4d, 0x50, 0x54, 0x58, 0x5d]
    for value in list(actions) + nothing:
      emulator = Recorder()
      emulator.put_memory(0x1000, [0] * CONTEXT_WORDS)
      emulator.write(0x440ff010, 0x40001000)
      emulator.write(0x440ff008, value)
      self.assertEqual(emulator.calls, [actions[value]] if value in actions else [], hex(value))


if __name__ == "__main__":
  unittest.main()
