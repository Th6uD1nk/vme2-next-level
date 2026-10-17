import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmeemu import BASE_OFFSET, BUFFER_WORDS, CONTEXT_WORDS, TOP_OFFSET, Emulator, replay


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


SAMPLE_KERNEL_TRACE = (
    "W 0x440ff008 0x3\n"
    "W 0x440f8070 0x0\n"
    "W 0x440f8078 0x0\n"
    "W 0x440f8074 0x4440\n"
    "W 0x440f8000 0x2010380\n"
    "W 0x440f8010 0x407c000\n"
    "W 0x440f8040 0x7fffff\n"
    "W 0x440f8044 0x0\n"
    "W 0x440f8004 0x12010380\n"
    "W 0x440f8014 0x447c000\n"
    "W 0x440f8048 0x7fffff\n"
    "W 0x440f804c 0x0\n"
    "W 0x440f8008 0x22010380\n"
    "W 0x440f8018 0x487c000\n"
    "W 0x440f8050 0x7fffff\n"
    "W 0x440f8054 0x0\n"
    "W 0x440f800c 0x32010380\n"
    "W 0x440f801c 0x4c7c000\n"
    "W 0x440f8058 0x7fffff\n"
    "W 0x440f805c 0x0\n"
    "W 0x440f8084 0x84000000\n"
    "W 0x440f8088 0x1000f\n"
    "W 0x440f809c 0x84000020\n"
    "W 0x440f80a0 0x1000f\n"
    "W 0x440f80b4 0x84090000\n"
    "W 0x440f80b8 0x1000f\n"
    "W 0x440f806c 0xf0000000\n"
    "W 0x440ff008 0x18\n"
    "W 0x440ff000 0x88\n"
)

SAMPLE_REGISTERS = {
  0: 0x02010380, 1: 0x12010380, 2: 0x22010380, 3: 0x32010380,
  4: 0x0407c000, 5: 0x0447c000, 6: 0x0487c000, 7: 0x04c7c000,
  0x10: 0x7fffff, 0x12: 0x7fffff, 0x14: 0x7fffff, 0x16: 0x7fffff,
  0x1b: 0xf0000000, 0x1d: 0x4440, 0x21: 0x84000000, 0x22: 0x0001000f,
  0x27: 0x84000020, 0x28: 0x0001000f, 0x2d: 0x84090000, 0x2e: 0x0001000f,
}


class SampleTest(unittest.TestCase):
  def test_kernel_trace_gives_the_registers_of_the_sample(self):
    emulator = Emulator()
    replay(emulator, SAMPLE_KERNEL_TRACE)
    expected = [SAMPLE_REGISTERS.get(index, 0) for index in range(len(emulator.registers))]
    self.assertEqual(emulator.registers, expected)
    self.assertEqual(emulator.active, expected)

  def test_sample_results_in_the_base_buffers(self):
    tops = [[0x10 * (n + 1) + i for i in range(16)] for n in range(4)]
    base0 = [0x01, 0x10, 0x01, 0x800001, 0x01, 0x20, 0x01, 0x800001, 0x01, 0x30, 0x01, 0x800001, 0x01, 0x40, 0x01, 0x800001]
    emulator = Emulator()
    for n in range(4):
      emulator.scratchpad.transfer(TOP_OFFSET + n * BUFFER_WORDS, tops[n])
    emulator.scratchpad.transfer(BASE_OFFSET + 32, base0)
    replay(emulator, SAMPLE_KERNEL_TRACE)
    signed = [word - 0x1000000 if word & 0x800000 else word for word in base0]
    for pe in range(4):
      expected = [max(0, min(0x7fffff, max(-64, min(63, tops[pe][i] + signed[i])))) for i in range(16)]
      got = [emulator.scratchpad.read(BASE_OFFSET + pe * BUFFER_WORDS + i) for i in range(16)]
      self.assertEqual(got, expected, f"base{pe}")


if __name__ == "__main__":
  unittest.main()
