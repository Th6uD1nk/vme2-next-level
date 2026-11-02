import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmee.agu import stream_at
from vmee.extract import array_declarations, host_main, host_program
from vmee.fu import execute, opcode_entry
from vmee.host import build_program, run_program
from vmee.listing import defines, emulations, format_listing
from vmee.memory import BASE_OFFSET, BUFFER_WORDS, TOP_OFFSET
from vmee.registers import CONTEXT_WORDS, agu_register, fu_register
from vmee.run import run_emulation
from vmee.trace import replay
from vmee.machine import Emulator
from vmeg.vmecalls import wait_marker
from vmeh.extract import extract_source
from vmeemu import main as vmeemu_main


def loads(*rows):
  declarations = "".join(f"  Transfer t{n} = {{ memory: {memory}, count: {words - 1} }};\n" for n, (scope, buffer, words, offset, memory) in enumerate(rows))
  statements = "".join(f"  .load {{ .transfer = t{n}; .scope = {scope}; .offsets {{ .{buffer} = {offset}; }} }}\n" for n, (scope, buffer, words, offset, memory) in enumerate(rows))
  return declarations + statements


def dma(memory, count, destination):
  return [f"vme_dma(MEMORY, ADDR, useg_mem((u32){memory}));", f"vme_dma(ITERATION, DIMS, {count});", f"vme_dma(SPAD, OFFSET, {destination});", "vme_dma(CTRL, VALUE, 0x40);", "meCoreDMACPrimWaitTransferFinish();"]


def function(name, count):
  return f"static inline void {name}(volatile u32* memory, u32 spadOffset) {{\n" + "".join(f"  {line}\n" for line in dma("memory", count, "spadOffset")[:-1]) + "}"


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

  def iterate_to_scratchpad(self):
    self.calls.append("iterate to scratchpad")

  def iterate_to_memory(self):
    self.calls.append("iterate to memory")


class ControlTest(unittest.TestCase):
  def test_each_control_value_fires_its_own_action_only(self):
    actions = {
      0x05: "context", 0x0c: "context", 0x1d: "context", 0x18: "trigger", 0x21: "clear",
      0x40: "ring to scratchpad", 0x48: "ring to memory", 0x52: "mem to 16", 0x5a: "mem from 16",
      0x50: "iterate to scratchpad", 0x58: "iterate to memory",
    }
    nothing = [0x00, 0x02, 0x03, 0x04, 0x08, 0x20, 0x28, 0x42, 0x45, 0x4d, 0x54, 0x5d]
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


class MacTest(unittest.TestCase):
  def stream(self, opcode, k, b, backs, fronts):
    fu = {"opcode": opcode, "sat": 0, "round": 0, "k": k}
    state = {}
    out = []
    previous = None
    for back, front in zip(backs, fronts):
      previous = execute(fu, back, front, 0, b, previous, state)
      out.append(previous)
    return out

  def test_inner_product_is_a_running_sum_and_bias_is_added_to_each_output(self):
    self.assertEqual(self.stream(0x240, 0, 0, [1, 1, 1, 1], [1, 1, 1, 1]), [1, 2, 3, 4])
    self.assertEqual(self.stream(0x240, 0, 1, [1, 1, 1, 1], [1, 1, 1, 1]), [2, 3, 4, 5])
    self.assertEqual(self.stream(0x240, 1, 0, [1, 2, 3], [2, 2, 2]), [1, 3, 6])

  def test_acc_shift_starts_with_bias_then_adds_the_previous_result(self):
    self.assertEqual(self.stream(0x250, 1, 20, [4, 6, 8, 10], [0, 0, 0, 0]), [12, 15, 19, 24])


class RingTest(unittest.TestCase):
  def test_ring_cycles_over_inner_count_whatever_the_agu_count(self):
    emulator = Emulator()
    emulator.active[:] = [0] * 106
    emulator.scratchpad.transfer(TOP_OFFSET, [0x100 + i for i in range(8)])
    emulator.active[28] = 0x4440
    emulator.active[agu_register(0, "top", "mode")] = 0x84000000
    emulator.active[agu_register(0, "top", "count")] = 0x10000 | 15
    emulator.active[agu_register(0, "top", "inner0")] = (3 << 16) | 1
    emulator.active[agu_register(0, "top", "format0")] = 0x20000
    self.assertEqual([stream_at(emulator, "top", 0, cycle, {}) for cycle in range(10)], [0x100, 0x101, 0x102, 0x103] * 2 + [0x100, 0x101])


class Mode2Test(unittest.TestCase):
  def play(self, count, inner0, format0, cycles):
    emulator = Emulator()
    emulator.active[:] = [0] * 106
    emulator.scratchpad.transfer(TOP_OFFSET, [0x100 + i for i in range(32)])
    emulator.active[28] = 0x4440
    emulator.active[agu_register(0, "top", "mode")] = 0x82000000
    emulator.active[agu_register(0, "top", "count")] = count
    emulator.active[agu_register(0, "top", "inner0")] = inner0
    emulator.active[agu_register(0, "top", "format0")] = format0
    return [stream_at(emulator, "top", 0, cycle, {}) for cycle in range(cycles)], emulator.warnings

  def test_a_ring_is_read_until_the_range_and_the_ring_end_together_then_the_last_word_is_held(self):
    self.assertEqual(self.play(0x10000 | 7, (2 << 16) | 6, 0x20000, 10), ([0x100, 0x102, 0x104, 0x106] * 2 + [0x106] * 2, []))
    self.assertEqual(self.play(0x10000 | 5, (1 << 16) | 3, 0x20000, 14), ([0x100, 0x101, 0x102, 0x103] * 3 + [0x103] * 2, []))

  def test_without_the_ring_token_the_reads_are_linear_and_without_inner0_the_first_word_is_read(self):
    self.assertEqual(self.play(0x10000 | 3, (1 << 16) | 3, 0, 6), ([0x100, 0x101, 0x102, 0x103, 0x103, 0x103], []))
    self.assertEqual(self.play(0x10000 | 3, 0, 0x20000, 3), ([0x100] * 3, []))

  def test_the_parent_step_divides_the_count(self):
    self.assertEqual(self.play(0x20000 | 14, (1 << 16) | 3, 0x20000, 10), ([0x100, 0x101, 0x102, 0x103] * 2 + [0x103] * 2, []))

  def test_what_the_psp_does_not_like_or_what_is_not_measured_is_played_with_a_warning(self):
    cases = (
      (0x10000 | 7, (2 << 16) | 3, 0x20000, "inner0 count 3 with the step 2"),
      (0x20000 | 7, (1 << 16) | 3, 0x20000, "count 7 with the step 2"),
      (0x10000 | 7, (2 << 16) | 6, 0, "no ring with a step other than 1"),
      (0x10000 | 7, (1 << 16) | 3, 0x20000 | 0x10000000, "reverses the order in the mode 2"),
      (0, (1 << 16) | 3, 0x20000, "step 0"),
    )
    for count, inner0, format0, expected in cases:
      words, warnings = self.play(count, inner0, format0, 4)
      self.assertEqual(len(words), 4)
      self.assertTrue(any(expected in warning for warning in warnings), (expected, warnings))
    words, _ = self.play(0x10000 | 7, (2 << 16) | 3, 0x20000, 6)
    self.assertEqual(words, [0x100, 0x102, 0x100, 0x102, 0x100, 0x102])


class SyncTest(unittest.TestCase):
  def run_kernel(self, sync):
    emulator = Emulator()
    registers = emulator.registers
    registers[:] = [0] * 106
    registers[28], registers[29], registers[30] = 0x4400, 0x4440, 0x3210
    registers[fu_register(0, "primary")] = (2 << 27) | (0x010 << 12)
    registers[fu_register(1, "primary")] = (4 << 27) | (8 << 22) | (0x010 << 12)
    for pe, agu, mode, count in ((0, "top", 0x84000000, 7), (0, "base", 0x84000000, 11), (0, "write", 0x84000000, 14), (1, "write", 0x84060000, 11)):
      registers[agu_register(pe, agu, "mode")] = mode
      registers[agu_register(pe, agu, "count")] = 0x10000 | count
    registers[agu_register(0, "write", "format0")] = 1
    registers[agu_register(0, "write", "format1")] = 0x200000 if sync else 0
    emulator.scratchpad.transfer(TOP_OFFSET, [1, 2, 3, 4, 5, 6, 7, 8])
    emulator.scratchpad.transfer(TOP_OFFSET + BUFFER_WORDS, [100] * 8)
    emulator.trigger()
    return [emulator.scratchpad.read(BASE_OFFSET + BUFFER_WORDS + i) for i in range(12)]

  def test_written_words_are_seen_by_a_later_fu_only_with_the_end_token(self):
    self.assertEqual(self.run_kernel(True), [0] * 7 + [101, 102, 103, 104, 105])
    self.assertEqual(self.run_kernel(False), [0] * 12)


class IterationTest(unittest.TestCase):
  def test_groups_on_the_way_in_and_gap_on_the_way_out(self):
    emulator = Emulator()
    emulator.put_memory(0x1000, list(range(1, 9)))
    for offset, value in ((0x10, 0x1000), (0x14, 0x70000), (0x18, 0x8000), (0x20, 4), (0x24, 3), (0x28, 0x100001), (0x08, 0x50)):
      emulator.write(0x440ff000 + offset, value)
    words = [emulator.scratchpad.read(0x8000 + i) for i in range(32)]
    self.assertEqual(words[:4] + words[16:20], list(range(1, 9)))
    self.assertEqual(sum(1 for word in words if word), 8)
    for offset, value in ((0x10, 0x2000), (0x14, 0x1000f), (0x18, 0x8000), (0x24, 0), (0x28, 0), (0x08, 0x58)):
      emulator.write(0x440ff000 + offset, value)
    self.assertEqual(emulator.get_memory(0x2000, 2), [1, 5])

  def test_the_memory_is_stepped_by_the_iteration_step_and_a_step_that_is_not_a_word_multiple_is_refused(self):
    emulator = Emulator()
    emulator.put_memory(0x1000, list(range(10, 18)))
    for offset, value in ((0x10, 0x1000), (0x14, 0x30000), (0x18, 0x8000), (0x20, 8), (0x24, 0), (0x28, 0), (0x08, 0x50)):
      emulator.write(0x440ff000 + offset, value)
    self.assertEqual([emulator.scratchpad.read(0x8000 + i) for i in range(4)], [10, 12, 14, 16])
    for offset, value in ((0x10, 0x2000), (0x14, 0x30000), (0x18, 0x8000), (0x08, 0x58)):
      emulator.write(0x440ff000 + offset, value)
    self.assertEqual(emulator.get_memory(0x2000, 4, 8), [10, 12, 14, 16])
    emulator.write(0x440ff000 + 0x20, 6)
    with self.assertRaises(ValueError):
      emulator.write(0x440ff000 + 0x08, 0x50)

  def test_a_step_of_0_repeats_the_transfer_in_one_stream_through_the_groups(self):
    emulator = Emulator()
    emulator.put_memory(0x1000, list(range(100, 108)))
    for offset, value in ((0x10, 0x1000), (0x14, (1 << 16) | 7), (0x18, 0x8000), (0x20, 0), (0x24, 3), (0x28, (2 << 16) | 1), (0x08, 0x50)):
      emulator.write(0x440ff000 + offset, value)
    self.assertEqual([emulator.scratchpad.read(0x8000 + i) for i in range(10)], [100, 101, 104, 105, 100, 101, 104, 105, 106, 107])

  def test_a_step_of_0_is_refused_with_a_store_and_with_a_stream_that_is_not_whole_groups(self):
    emulator = Emulator()
    emulator.put_memory(0x1000, list(range(100, 108)))
    for offset, value in ((0x10, 0x1000), (0x14, (1 << 16) | 4), (0x18, 0x8000), (0x20, 0), (0x24, 2), (0x28, (1 << 16) | 1)):
      emulator.write(0x440ff000 + offset, value)
    with self.assertRaises(ValueError):
      emulator.write(0x440ff000 + 0x08, 0x50)
    emulator.write(0x440ff000 + 0x24, 0)
    with self.assertRaises(ValueError):
      emulator.write(0x440ff000 + 0x08, 0x58)

  def test_the_four_stage_transfers_of_the_fft_give_the_legs_of_its_readme(self):
    legs = {
      8: ([0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14, 15]),
      4: ([0, 1, 2, 3, 8, 9, 10, 11], [4, 5, 6, 7, 12, 13, 14, 15]),
      2: ([0, 1, 4, 5, 8, 9, 12, 13], [2, 3, 6, 7, 10, 11, 14, 15]),
      1: ([0, 2, 4, 6, 8, 10, 12, 14], [1, 3, 5, 7, 9, 11, 13, 15]),
    }
    for stride, (upper, lower) in legs.items():
      emulator = Emulator()
      emulator.put_memory(0x1000, [100 + i for i in range(16)] + [0] * 16)
      for offset, value in ((0x10, 0x1000), (0x14, (1 << 16) | (15 + stride)), (0x18, 0x8000), (0x20, 0), (0x24, 2 * stride - 1), (0x28, (stride << 16) | 1), (0x08, 0x50)):
        emulator.write(0x440ff000 + offset, value)
      zone = [emulator.scratchpad.read(0x8000 + i) for i in range(16 + stride)]
      self.assertEqual(zone[:8], [100 + i for i in upper])
      self.assertEqual(zone[8 + stride:16 + stride], [100 + i for i in lower])


def fu_of(opcode):
  return {"front": "TOP_0", "back": "BASE_0", "opcode": opcode, "sat": 0, "round": 0, "k": 0}


def cut24(value):
  value &= 0xffffff
  return value - (1 << 24) if value >= 1 << 23 else value


class SubtractionOnThePspTest(unittest.TestCase):
  def test_the_subtractions_give_the_words_read_on_the_psp(self):
    top, base = (741455, -741455), (741454, 741455)
    for opcode, registers, wanted in (
      (0x034, {"a": 7}, (8, -1482903)),
      (0x048, {"b": 7}, (735663, -747247)),
      (0x048, {"b": -7}, (6498639, 5015601)),
      (0x050, {"b": 2}, (-556092, 926818)),
    ):
      with self.subTest(opcode=hex(opcode), registers=registers):
        found = tuple(cut24(execute(fu_of(opcode), base[i], top[i], registers.get("a", 0), registers.get("b", 0))) for i in range(2))
        self.assertEqual(found, wanted)


def rounded_fu(opcode, k, round_):
  return {"front": "TOP_0", "back": "BASE_0", "opcode": opcode, "sat": 0, "round": round_, "k": k}


class RoundOnThePspTest(unittest.TestCase):
  def test_the_bit_rounds_the_shift_of_an_addition_a_subtraction_and_a_product_as_the_psp_does(self):
    for opcode, k, back, front, off, on in (
      (0x010, 1, 0, 1, 0, 1),
      (0x010, 1, 0, -1, -1, 0),
      (0x010, 2, 0, -2, -1, 0),
      (0x010, 8, 0, 128, 0, 1),
      (0x010, 8, 0, -128, -1, 0),
      (0x018, 1, 741454, 741455, 0, 1),
      (0x200, 4, 1, 8, 0, 1),
      (0x220, 20, -7, 0x80000, -4, -3),
      (0x010, 0, 0, 5, 5, 5),
      (0x018, 0, 0, 5, 5, 5),
    ):
      with self.subTest(opcode=hex(opcode), k=k, back=back, front=front):
        self.assertEqual(execute(rounded_fu(opcode, k, 0), back, front), off)
        self.assertEqual(execute(rounded_fu(opcode, k, 1), back, front), on)

  def test_the_bit_changes_nothing_on_the_three_subtractions_and_is_refused_where_it_is_not_known(self):
    for opcode, a, b in ((0x034, 7, 0), (0x048, 0, 7), (0x050, 0, 2)):
      with self.subTest(opcode=hex(opcode)):
        self.assertEqual(execute(rounded_fu(opcode, 1, 1), 741454, 741455, a, b), execute(rounded_fu(opcode, 1, 0), 741454, 741455, a, b))
    for opcode in (0x0c0, 0x024, 0x07c, 0x240):
      with self.subTest(opcode=hex(opcode)):
        with self.assertRaisesRegex(ValueError, "rounding bit of the opcode"):
          opcode_entry(rounded_fu(opcode, 1, 1))
        opcode_entry(rounded_fu(opcode, 1, 0))


class ListingTest(unittest.TestCase):
  def test_only_the_emulated_kernels_are_listed_with_their_buffers(self):
    text = (
      "volatile Buffer a[4];\n"
      ".kernel other direct {\n" + loads(("global", "top1", 4, 0, "a")) + "}\n"
      "@emulate \"first\"\n"
      ".kernel k direct {\n" + loads(("global", "top0", 4, 0, "a"), ("global", "base2", 2, "OFFSET", "a")) + "}\n"
    )
    self.assertEqual(emulations(text), [{
      "id": "first", "kernel": "k", "kernels": ["k"], "steps": [("k", ("config", "exec"))], "pairs": [[]], "memories": [None], "after": [[]], "bodies": [[]], "modes": {"k": "direct"}, "form": "mark", "mode": "direct", "first": 7, "last": 12, "local": [], "declared": {"global": {"a"}, "local": set()},
      "global": [("TOP_0", 4, "", "a", 10, False), ("BASE_2", 2, "OFFSET", "a", 11, False)],
      "definitions": [function("kT0Load", 3), function("kT1Load", 1)],
      "stores": {"global": [], "local": []},
    }])


  def test_defines_with_continuation_comment_and_arguments(self):
    text = "#define A 1\n#define B (x + 1) // note\n#define F(x) ((x) * 2)\n#define L a + \\\n  b /* c */\n#define E\n#include <x.h>\nint y = 1; // #define NOT 3\n"
    self.assertEqual(defines(text), [("A", "1"), ("B", "(x + 1)"), ("F(x)", "((x) * 2)"), ("L", "a + b"), ("E", "")])


  def test_overlap_is_marked_on_the_second_link_of_the_same_kernel_only(self):
    text = (
      "#define OFF 8\n"
      "@emulate \"one\"\n.kernel k direct {\n" + loads(("global", "top0", 16, 0, "a"), ("global", "top0", 16, "OFF", "b"), ("global", "top1", 4, 40, "c"), ("global", "top1", 4, "UNKNOWN", "d")) + "}\n"
      "@emulate \"two\"\n.kernel m direct {\n" + loads(("global", "top0", 16, 0, "a")) + "}\n"
      "Buffer a[4], b[4], c[4], d[4];\n"
    )
    lines = format_listing(emulations(text), defines(text), full=True).splitlines()
    marked = [line for line in lines if "overlaps" in line]
    self.assertEqual(marked, ["  TOP_0   global  at 8  16 words  from b  <-- overlaps TOP_0 at 0 (words 8-15)"])


  def test_a_number_of_words_that_is_a_text_is_shown_and_noted_only_when_it_can_be_computed(self):
    emulation = {
      "id": "e", "kernel": "k", "first": 1, "last": 2, "declared": {"global": {"a"}, "local": set()},
      "global": [
        ("TOP_0", "(HEADER + 1)", "", "a", 3, False),
        ("TOP_0", 16, "", "a", 4, False),
        ("TOP_1", "(63 + 1)", "4", "a", 5, False),
        ("TOP_1", 16, "8", "a", 6, False),
        ("TOP_2", "(2048 + 1)", "", "a", 7, False),
      ],
      "local": [], "stores": {"global": [], "local": []},
    }
    lines = format_listing([emulation], []).splitlines()
    self.assertEqual(lines[2:7], [
      "    TOP_0   (HEADER + 1) words  from a",
      "    TOP_0   16 words  from a",
      "    TOP_1   (63 + 1) words  at 4  from a",
      "    TOP_1   16 words  at 8  from a  <-- overlaps TOP_1 at 4 (words 8-23)",
      "    TOP_2   (2048 + 1) words  from a  <-- goes past the end of the buffer (0x800 words)",
    ])

  def test_an_array_without_buffer_declaration_is_marked_and_extern_counts(self):
    text = "extern Buffer a[4];\n@emulate \"one\"\n.kernel k direct {\n" + loads(("global", "top0", 4, 0, "a"), ("global", "top1", 4, 0, "nothere")) + "}\n"
    lines = format_listing(emulations(text), [], full=True).splitlines()
    self.assertEqual(lines[1:3], ["  TOP_0   global  at 0  4 words  from a", "  TOP_1   global  at 0  4 words  from nothere  <-- 'nothere' is not declared with Buffer"])


  def test_an_offset_name_without_define_is_marked(self):
    text = "#define KNOWN 8\n@emulate \"one\"\n.kernel k direct {\n" + loads(("global", "top0", 4, "KNOWN", "a"), ("global", "top1", 4, "(KNOWN + MISSING)", "a"), ("global", "top2", 4, "0x28", "a")) + "}\nBuffer a[4];\n"
    lines = format_listing(emulations(text), defines(text), full=True).splitlines()
    self.assertEqual([line for line in lines if "<--" in line], ["  TOP_1   global  at (8 + MISSING)  4 words  from a  <-- 'MISSING' has no #define in this file"])


class ExtractTest(unittest.TestCase):
  def test_arrays_of_the_links_with_two_in_one_statement_extern_and_local(self):
    text = (
      "extern Buffer ex[16];\n"
      "volatile Buffer a[2] = { 1, 2 }, b[3];\n"
      "@emulate \"one\"\n.kernel k direct {\n"
      + loads(("global", "top0", 2, 0, "a"), ("global", "top1", 3, 0, "b"), ("global", "top2", 16, 0, "ex"), ("local", "top3", 4, 0, "x")) +
      "}\n"
      "@kernel k config | exec\nvoid f() {\n  Buffer x[4] = { 5, 6, 7, 8 };\n}\n"
    )
    found = array_declarations(text, "one")
    self.assertEqual([(d["where"], d["names"], d["extern"], d["text"]) for d in found], [
      ("global", ["a", "b"], False, "volatile Buffer a[2] = { 1, 2 }, b[3];"),
      ("global", ["ex"], True, "extern Buffer ex[16];"),
      ("local", ["x"], False, "Buffer x[4] = { 5, 6, 7, 8 };"),
    ])
    with self.assertRaises(ValueError):
      array_declarations(text, "missing")

  def test_arrays_of_the_links_come_from_the_other_files(self):
    text = "extern Buffer ex[2];\n@emulate \"one\"\n.kernel k direct {\n" + loads(("global", "top0", 2, 0, "ex"), ("global", "top1", 2, 0, "absent"), ("local", "top2", 4, 0, "x")) + "}\n"
    arrays = "volatile Buffer ex[2] = { 1, 2 };\nvolatile Buffer absent[2] = { 3, 4 };\n"
    function = "@kernel k config | exec\nvoid f() {\n  Buffer x[4] = { 5, 6, 7, 8 };\n}\n"
    found = array_declarations(text, "one", [arrays, function])
    self.assertEqual([(d["where"], d["names"], d["extern"], d["text"]) for d in found], [
      ("global", ["ex"], False, "volatile Buffer ex[2] = { 1, 2 };"),
      ("global", ["absent"], False, "volatile Buffer absent[2] = { 3, 4 };"),
      ("local", ["x"], False, "Buffer x[4] = { 5, 6, 7, 8 };"),
    ])
    self.assertEqual([d["origin"] for d in found], [arrays, arrays, function])


BLOCK = (
  "volatile Buffer src[16];\n"
  "volatile Memory stage[2];\n"
  ".kernel m memory {\n  .params { int n; }\n" + loads(("global", "top0", 16, 0, "src")) + "}\n"
  ".kernel d direct {\n}\n"
  "void meLibOnProcess(void) {\n"
  "  @emulate \"blk\" {\n"
  "    @kernel m build {\n      .params = { n: 5 };\n      .memory = stage[1];\n    }\n"
  "    @kernel d config | exec {\n    }\n"
  "    @kernel m config {\n      .memory = stage[1];\n    }\n"
  "  }\n"
  "}\n"
)


BODY = (
  "volatile Buffer a[16];\n"
  "volatile Buffer b[16];\n"
  ".kernel k direct {\n"
  "  Transfer in = { memory: a, count: 15 };\n"
  "  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n"
  "}\n"
  "void meLibOnProcess(void) {\n"
  "  @emulate \"body\" {\n"
  "    @kernel k config {\n"
  "      Transfer out = { memory: b, count: 15 };\n"
  "      .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }\n"
  "    }\n"
  "    @kernel k exec {\n"
  "    }\n"
  "  }\n"
  "}\n"
)


def main_calls(text, identifier):
  structure = ("if (", "}", "vmegLoadArrays(", "vmegBindPointers(", "hwTraceMuted()", "vmeLibEnable();", "vmeLibWipe();", "vmeLibDisable();")
  lines = [line.strip() for line in host_main(text, identifier).splitlines()]
  return [line for line in lines[lines.index("vmegFixArrays();") + 1:] if not line.startswith(structure) and line != "return 0;"]


CHAIN = (
  "volatile Buffer input[4] = { 1, 2, 3, 4 };\n"
  "volatile Buffer middle[4];\n"
  ".kernel first direct {\n"
  "  Int count = 4 - 1;\n"
  "  Transfer in = { memory: input, count };\n"
  "  Transfer out = { memory: middle, count };\n"
  "  .load { .transfer = in; .scope = global; .offsets { .top0 = 0; } }\n"
  "  Agu top = { count };\n"
  "  Agu write = { count, cyc: auto };\n"
  "  .pe0 { .top = top; .write = write; .spad = top0 + top0; }\n"
  "  .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }\n"
  "}\n"
  ".kernel second direct {\n"
  "  Int count = 4 - 1;\n"
  "  Transfer back = { memory: middle, count };\n"
  "  .load { .transfer = back; .scope = global; .offsets { .top0 = 0; } }\n"
  "  Agu top = { count };\n"
  "  Agu write = { count, cyc: auto };\n"
  "  .pe0 { .top = top; .write = write; .spad = top0 + top0; }\n"
  "}\n"
  "void meLibOnProcess(void) {\n"
  "  @emulate \"chain\" {\n"
  "    @kernel first config | exec {\n    }\n"
  "    @kernel second config | exec {\n    }\n"
  "  }\n"
  "}\n"
)


class EmulationBlockTest(unittest.TestCase):
  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_the_arrays_of_the_host_program_have_fixed_addresses_written_in_the_trace(self):
    for _ in range(2):
      with tempfile.TemporaryDirectory() as folder:
        trace = run_program(build_program(host_program(BODY, "body"), folder))
      self.assertEqual([line for line in trace.splitlines() if line.startswith("# array")], ["# array a 0x8800000 16", "# array b 0x8800040 16"])

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_the_steps_of_the_host_program_run_one_after_the_other_as_the_whole_program_does(self):
    def events(trace):
      return [line for line in trace.splitlines() if not line.startswith("# array")]
    with tempfile.TemporaryDirectory() as folder:
      executable = build_program(host_program(BODY, "body"), folder)
      whole = events(run_program(executable))
      first = events(run_program(executable, ("0",)))
      second = events(run_program(executable, ("1",)))
    self.assertEqual(first + second, whole)
    self.assertIn("W 0x440ff000 0x80", first)
    self.assertNotIn("W 0x440ff000 0x80", second)

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_the_arrays_given_in_a_file_are_the_content_that_the_calls_read(self):
    with tempfile.TemporaryDirectory() as folder:
      executable = build_program(host_program(BODY, "body"), folder)
      path = os.path.join(folder, "arrays.txt")
      with open(path, "w") as f:
        f.write("a " + " ".join("%x" % (0x100 + i) for i in range(16)) + "\n")
      given = run_program(executable, ("0", path)).splitlines()
      declared = run_program(executable, ("0",)).splitlines()
    self.assertIn("M 0x8800000 " + " ".join("0x%x" % (0x100 + i) for i in range(16)), given)
    self.assertIn("M 0x8800000 " + " ".join("0x0" for _ in range(16)), declared)

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_a_step_finds_the_contexts_built_by_the_earlier_steps(self):
    def events(trace):
      return [line for line in trace.splitlines() if not line.startswith("# array")]
    with tempfile.TemporaryDirectory() as folder:
      executable = build_program(host_program(BLOCK, "blk"), folder)
      steps = [events(run_program(executable, (str(index),))) for index in range(3)]
      whole = events(run_program(executable))
    self.assertEqual(steps[0] + steps[1] + steps[2], whole)
    context = [line for line in steps[2] if line.startswith("M 0xa")][0].split()[2:]
    self.assertTrue(any(int(word, 16) for word in context))

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_a_store_of_a_call_is_what_the_load_of_the_next_call_reads(self):
    emulator = run_emulation(CHAIN, "chain")
    self.assertEqual([emulator.scratchpad.read(BASE_OFFSET + i) for i in range(4)], [4, 8, 12, 16])

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_a_block_of_one_call_gives_what_the_whole_program_gives(self):
    single = CHAIN.replace("    @kernel second config | exec {\n    }\n", "")
    emulator = run_emulation(single, "chain")
    self.assertEqual([emulator.scratchpad.read(BASE_OFFSET + i) for i in range(4)], [2, 4, 6, 8])
    self.assertEqual([emulator.memory[0x08800040 + 4 * i] for i in range(4)], [2, 4, 6, 8])

  def test_each_call_does_its_own_load_and_the_statements_of_the_body_come_after_its_calls(self):
    wait = "meCoreDMACPrimWaitTransferFinish();"
    self.assertEqual(main_calls(BODY, "body"), [
      "kInLoad(a, VME_TOP_BUFF0_WOFF);", wait, "vmeLibSetFlow(VME_DEFAULT);", "k();",
      "meLibOnProcessOutStore(b, VME_BASE_BUFF0_WOFF);", wait,
      "kInLoad(a, VME_TOP_BUFF0_WOFF);", wait, "vmeLibTrigger();", "meCoreDMACPrimWaitVMEFinish();",
    ])

  def test_the_emulator_plays_the_calls_of_the_block_with_their_values_and_their_memory(self):
    self.assertEqual(main_calls(BLOCK, "blk"), ["mBuild(stage[1], 5);", "vmeLibStart();", "d();", "vmeLibFinish();", "mT0Load(src, VME_TOP_BUFF0_WOFF);", "meCoreDMACPrimWaitTransferFinish();", "vmeLibLoadCustomContext(stage[1]);"])
    self.assertIn("volatile u32 __attribute__((aligned(64))) stage[2][VME_CONTEXT_WORD_COUNT];", host_program(BLOCK, "blk"))

  def test_vmeh_writes_the_statements_of_the_body_of_a_call_before_the_fill(self):
    text = BODY.replace("    @kernel k exec {\n    }\n", "    @kernel k exec {\n      Transfer back = { memory: b, count: 15 };\n      .store { .transfer = back; .scope = global; .offsets { .base1 = 0; } }\n    }\n")
    expected = (
      "  @kernel k config {\n    Transfer out = { memory: b, count: 15 };\n    .store { .transfer = out; .scope = global; .offsets { .base0 = 0; } }\n  }\n"
      "  @kernel k exec {\n    Transfer back = { memory: b, count: 15 };\n    .store { .transfer = back; .scope = global; .offsets { .base1 = 0; } }\n    vmeDebugFillWith(VME_BASE_BUFFERS);\n  }\n"
    )
    self.assertIn(expected, extract_source(text, "body"))

  def test_vmeh_writes_the_calls_of_the_block_and_the_fill_in_the_last_one(self):
    source = extract_source(BLOCK, "blk")
    expected = (
      "void meLibOnProcess(void) {\n"
      "  @kernel m build {\n    .params = { n: 5 };\n    .memory = stage[1];\n  }\n"
      "  @kernel d config | exec {\n  }\n"
      "  @kernel m config {\n    .memory = stage[1];\n    vmeDebugFillWith(VME_BASE_BUFFERS);\n  }\n"
    )
    self.assertIn(expected, source)
    self.assertIn("volatile Memory stage[2];", source)
    marked = "@emulate \"mk\"\n.kernel m memory {\n}\n"
    self.assertIn("@kernel m build | config | exec {", extract_source(marked, "mk"))



USE_FILE = CHAIN.replace("volatile Buffer middle[4];\n", "volatile Buffer middle[4];\nvolatile Buffer other[4] = { 10, 20, 30, 40 };\nvolatile Buffer spare[4];\nvolatile Buffer small[2];\n")


class UseTest(unittest.TestCase):
  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_a_load_reads_the_array_given_in_place_of_the_one_it_names(self):
    emulator = run_emulation(USE_FILE, "chain", uses=[("input", "other")])
    self.assertEqual([emulator.scratchpad.read(BASE_OFFSET + i) for i in range(4)], [40, 80, 120, 160])

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_a_store_goes_to_the_array_given_in_place_and_the_next_load_reads_it_there(self):
    emulator = run_emulation(USE_FILE, "chain", uses=[("middle", "spare")])
    self.assertEqual([emulator.scratchpad.read(BASE_OFFSET + i) for i in range(4)], [4, 8, 12, 16])
    self.assertEqual([emulator.memory[0x08800080 + 4 * i] for i in range(4)], [2, 4, 6, 8])
    self.assertNotIn(0x08800040, emulator.memory)

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_an_array_that_is_not_used_does_not_exist_or_has_another_size_is_refused(self):
    with self.assertRaisesRegex(ValueError, "--use other=spare: the array other is not read or written"):
      run_emulation(USE_FILE, "chain", uses=[("other", "spare")])
    with self.assertRaisesRegex(ValueError, "--use input=nope: the array nope is defined in no file"):
      run_emulation(USE_FILE, "chain", uses=[("input", "nope")])
    with self.assertRaisesRegex(ValueError, "--use input=small: the two arrays must have the same size"):
      run_emulation(USE_FILE, "chain", uses=[("input", "small")])

  @unittest.skipUnless(shutil.which("g++"), "g++ is needed to build the host program")
  def test_the_option_of_the_command_gives_the_arrays_and_refuses_what_is_not_a_pair(self):
    with tempfile.TemporaryDirectory() as folder:
      path = os.path.join(folder, "chain.vmeg.cpp")
      with open(path, "w", encoding="utf-8") as f:
        f.write(USE_FILE)
      out = io.StringIO()
      with contextlib.redirect_stdout(out):
        self.assertEqual(vmeemu_main(["--run", "chain", path, "--use", "input=other", "--buffers-words", "4"]), 0)
      self.assertEqual(out.getvalue().splitlines()[1], "0x00000028, 0x00000050, 0x00000078, 0x000000a0,")
      for arguments in (["--run", "chain", path, "--use", "input"], ["--run", "chain", path, "--use", "input=other", "--use", "input=spare"], ["--list", path, "--use", "input=other"]):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
          vmeemu_main(arguments)


if __name__ == "__main__":
  unittest.main()
