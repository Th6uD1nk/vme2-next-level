import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeemu import Emulator, replay


class ReplayTest(unittest.TestCase):
  def test_trace_is_played_in_order(self):
    trace = "# upload\nM 0x1000 0x10 0x800001\n\nW 0x440ff010 0x40001000\nW 0x440ff014 0x1\nW 0x440ff018 0x8000\nW 0x440ff008 0x40\n"
    emulator = Emulator()
    replay(emulator, trace)
    self.assertEqual([emulator.scratchpad.read(0x8000), emulator.scratchpad.read(0x8001)], [0x10, 0xff800001])
    with self.assertRaises(ValueError) as ctx:
      replay(Emulator(), "W 0x440ff010 0x40001000\nW 0x440ff008 0x40\n")
    self.assertEqual(str(ctx.exception), "line 2: the memory image has no word at 0x1000")


if __name__ == "__main__":
  unittest.main()
