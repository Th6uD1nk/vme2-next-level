import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vmee.agu import stream_at
from vmee.extract import array_declarations
from vmee.fu import execute
from vmee.listing import defines, emulations, format_listing
from vmee.memory import BASE_OFFSET, BUFFER_WORDS, TOP_OFFSET
from vmee.registers import CONTEXT_WORDS, agu_register, fu_register
from vmee.trace import replay
from vmee.machine import Emulator
from vmeg.vmecalls import wait_marker


def loads(*rows):
  declarations = "".join(f"  Transfer t{n} = {{ type: words, mode: basic, memory: {memory}, count: {words - 1} }};\n" for n, (scope, buffer, words, offset, memory) in enumerate(rows))
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


class ListingTest(unittest.TestCase):
  def test_only_the_emulated_kernels_are_listed_with_their_buffers(self):
    text = (
      "volatile Buffer a[4];\n"
      ".kernel other direct {\n" + loads(("global", "top1", 4, 0, "a")) + "}\n"
      "@emulate \"first\"\n"
      ".kernel k direct {\n" + loads(("global", "top0", 4, 0, "a"), ("global", "base2", 2, "OFFSET", "a")) + "}\n"
    )
    self.assertEqual(emulations(text), [{
      "id": "first", "kernel": "k", "kernels": ["k"], "steps": [("k", ("config", "exec"))], "modes": {"k": "direct"}, "form": "mark", "mode": "direct", "first": 7, "last": 12, "local": [], "declared": {"global": {"a"}, "local": set()},
      "global": [("TOP_0", 4, "", "a", 10, False), ("BASE_2", 2, "OFFSET", "a", 11, False)],
      "calls": ["kT0Load(a, VME_TOP_BUFF0_WOFF);", wait_marker("kT0Load"), "kT1Load(a, VME_BASE_BUFF2_WOFF + OFFSET);", wait_marker("kT1Load")],
      "definitions": [function("kT0Load", 3), function("kT1Load", 1)],
      "stores": {"global": [], "local": []}, "downloads": [],
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


if __name__ == "__main__":
  unittest.main()
