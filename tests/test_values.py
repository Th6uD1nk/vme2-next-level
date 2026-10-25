import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.blocks import find_blocks
from vmeg.kernel import generate, parameter_names, replace_names, transfer_names
from vmegc import render
from emu.listing import defines, emulations, format_listing


def agu_count(body, prefix="", suffix=""):
  text = prefix + ".kernel k direct {\n" + body + "\n  Agu t = { count: n };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .top0 + top0; }\n}\n@kernel k config | exec\nvoid f() { }\n" + suffix
  out = render(text, find_blocks(text), "t.vmeg.c")
  line = next(line for line in out.splitlines() if "agu_top(COUNT)" in line)
  return line.strip()


def count_line(value):
  return f"vme_pe0(agu_top(COUNT), VME_DEF_STEP, {value});"


def cyc_line(operation, cyc="auto"):
  text = ".kernel k direct {\n  Agu t = { count: 3 }, b = { count: 3 };\n  Agu w = { count: 3, cyc: " + cyc + " };\n  .pe0 { .top = t; .base = b; .write = w; " + operation + " }\n}\n@kernel k config | exec\nvoid f() { }\n"
  out = render(text, find_blocks(text), "t.vmeg.c")
  return next(line for line in out.splitlines() if "vme_cyc" in line).strip()


def cyc_mode(value):
  return f"vme_pe0(agu_write(MODE), VME_DEF_MODE, vme_cyc({value}));"


def shared_warnings(second):
  text = ".kernel k direct {\n  Agu t = { count: 3 }, w = { count: 3, cyc: auto };\n  .pe0 { .top = t; .write = w; .top0 + top0; }\n  .pe1 { .top = t; .write = w; " + second + " }\n}\n@kernel k config | exec\nvoid f() { }\n"
  warnings = []
  generate(text, find_blocks(text)[0], warnings)
  return [message for _, message in warnings if "shares" in message]


class CycAutoTest(unittest.TestCase):
  def test_auto_is_three_cycles_plus_three_per_fu_of_the_chain_and_a_shift_follows_it(self):
    self.assertEqual(cyc_line(".top0 + base0;"), cyc_mode("6"))
    self.assertEqual(cyc_line(".clamp(top0 + base0, 0, 255);"), cyc_mode("9"))
    self.assertEqual(cyc_line(".clamp(top0 + base0, 0, 255);", "auto - 1"), cyc_mode("8"))

  def test_a_shared_write_agu_with_auto_warns_only_when_the_pes_need_different_delays(self):
    self.assertEqual(shared_warnings(".clamp(top1 + top1, 0, 9);"), ["pe1 shares the write Agu 'w' with pe0 but its operations need another delay, cyc: auto follows pe0"])
    self.assertEqual(shared_warnings(".top1 - top1;"), [])


def kernel_lines(body, compat):
  text = ".kernel k direct {\n  .pe0 { " + body + " }\n}\n@kernel k config | exec\nvoid f() { }\n"
  code = generate(text, find_blocks(text)[0], [], compat)
  return [line.strip() for line in code.splitlines() if "vme_fu" in line or "fu_reg" in line]


class CompatTest(unittest.TestCase):
  def test_the_option_fat_replaces_the_opcode_that_is_not_portable_by_its_variant(self):
    self.assertEqual(kernel_lines(".top0 + base0;", None), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD));"])
    self.assertEqual(kernel_lines(".top0 + base0;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD_OFA));", "vme_pe0(fu_reg(PRIMARY, A), 0);"])
    self.assertEqual(kernel_lines(".top0 - base0;", "fat"), kernel_lines(".top0 - base0;", None))


class KnownMacrosInAKernelTest(unittest.TestCase):
  def test_a_chain_of_int_built_from_a_macro_of_the_file_is_a_number(self):
    self.assertEqual(agu_count("  Int a = STEP * 2, n = a + 1;", "#define STEP 4\n"), count_line("9"))

  def test_a_macro_in_a_macro_of_the_file_is_a_number(self):
    self.assertEqual(agu_count("  Int n = COUNT_OF - 1;", "#define BASE 16\n#define COUNT_OF (BASE * 4)\n"), count_line("0x3f"))

  def test_an_int_takes_the_name_of_a_macro_without_an_error(self):
    self.assertEqual(agu_count("  Int n = 7;", "#define n 5\n"), count_line("7"))

  def test_a_transfer_of_a_kernel_block_counts_with_a_macro_of_the_file(self):
    text = (
      "#define BATCH 64\nvolatile Buffer arr[64];\n.kernel k direct {\n}\n"
      "void f() {\n  @kernel k config | exec {\n    Int last = BATCH - 1;\n"
      "    Transfer t = { type: words, mode: extended, memory: arr, dims: { count: last, gap: 0 } };\n"
      "    .load { .transfer = t; .scope = global; }\n  }\n}\n"
    )
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("vme_dma(ITERATION, DIMS, 63, 0);", out)


class UnknownMacrosInAKernelTest(unittest.TestCase):
  def test_a_macro_that_is_not_in_the_file_copies_the_whole_chain(self):
    self.assertEqual(agu_count("  Int a = HEADER_N * 2, n = a + 1;"), count_line("((HEADER_N * 2) + 1)"))

  def test_a_known_part_is_replaced_by_its_number_in_a_copy(self):
    self.assertEqual(agu_count("  Int n = N + HEADER;", "#define N 3\n"), count_line("(3 + HEADER)"))

  def test_the_unknown_spreads_along_a_chain(self):
    self.assertEqual(agu_count("  Int a = HEADER, b = a * 2, n = b - a;"), count_line("((HEADER * 2) - HEADER)"))

  def test_a_macro_defined_twice_is_copied(self):
    self.assertEqual(agu_count("  Int n = M + 1;", "#define M 1\n#define M 2\n"), count_line("(M + 1)"))

  def test_a_macro_in_a_condition_is_copied(self):
    self.assertEqual(agu_count("  Int n = M + 1;", "#ifdef Z\n#define M 1\n#endif\n"), count_line("(M + 1)"))

  def test_a_macro_defined_after_the_kernel_is_copied(self):
    self.assertEqual(agu_count("  Int n = M + 1;", "", "#define M 1\n"), count_line("(M + 1)"))


def dma_lines(transfer, prefix=""):
  text = prefix + "volatile Buffer arr[64];\n.kernel k direct {\n  Transfer t = " + transfer + ";\n  .load { .transfer = t; .scope = global; }\n}\n@kernel k config | exec\nvoid f() { }\n"
  out = render(text, find_blocks(text), "t.vmeg.c")
  return [line.strip() for line in out.splitlines() if line.strip().startswith("vme_dma(ITERATION") or line.strip().startswith("vme_dma(GROUP")]


class TransferValuesTest(unittest.TestCase):
  def test_a_macro_that_is_not_in_the_file_is_copied_in_the_fields_of_a_transfer(self):
    transfer = "{ type: words, mode: extended, memory: arr, dims: { count: HEADER_N - 1, gap: 0 }, step: HEADER_STEP, group: { size: 3, outer: HEADER_OUT, inner: 1 } }"
    self.assertEqual(dma_lines(transfer), [
      "vme_dma(ITERATION, DIMS, (headerN - 1), 0);",
      "vme_dma(ITERATION, STEP, headerStep);",
      "vme_dma(GROUP, SIZE, 3);",
      "vme_dma(GROUP, STEPS, headerOut, 1);",
    ])

  def test_a_known_part_is_replaced_by_its_number_in_the_copy_and_a_known_value_is_a_number(self):
    prefix = "#define KNOWN 64\n"
    self.assertEqual(dma_lines("{ type: words, mode: basic, memory: arr, count: KNOWN + HEADER }", prefix), ["vme_dma(ITERATION, DIMS, (64 + header));"])
    self.assertEqual(dma_lines("{ type: words, mode: basic, memory: arr, count: KNOWN - 1 }", prefix), ["vme_dma(ITERATION, DIMS, 63);"])

  def test_a_negative_number_is_still_refused(self):
    with self.assertRaises(ValueError) as caught:
      dma_lines("{ type: words, mode: basic, memory: arr, count: 0 - 1 }")
    self.assertIn("cannot be negative", str(caught.exception))


class TransferListingTest(unittest.TestCase):
  def test_the_listing_shows_the_words_of_a_transfer_with_an_unknown_macro_as_a_text(self):
    text = (
      "#define KNOWN 64\nvolatile Buffer a[64];\nvolatile Buffer b[64];\n@emulate \"e\"\n.kernel k direct {\n"
      "  Transfer t = { type: words, mode: basic, memory: a, count: HEADER_COUNT };\n"
      "  Transfer u = { type: words, mode: basic, memory: b, count: KNOWN - 1 };\n"
      "  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n"
      "  .load { .transfer = u; .scope = global; .offsets { .top1 = 0; } }\n}\n"
    )
    lines = format_listing(emulations(text), defines(text)).splitlines()
    self.assertEqual(lines[2:4], ["    TOP_0   (HEADER_COUNT + 1) words  from a", "    TOP_1   64 words  from b"])


if __name__ == "__main__":
  unittest.main()


class NamesOfATransferTest(unittest.TestCase):
  def test_the_names_are_found_once_in_the_order_of_the_fields(self):
    transfer = {"mode": "extended", "dims": {"count": "((HEADER_N * 2) - n)", "gap": "n"}, "step": "HEADER_STEP", "group": {"size": 3}}
    self.assertEqual(transfer_names(transfer), ["HEADER_STEP", "HEADER_N", "n"])

  def test_a_number_a_member_and_a_value_that_is_not_a_text_have_no_name(self):
    self.assertEqual(transfer_names({"mode": "basic", "count": "0x1F + obj.size + p->len"}), ["obj", "p"])
    self.assertEqual(transfer_names({"mode": "basic", "count": 15}), [])

  def test_the_parameters_are_camel_case_and_never_collide(self):
    self.assertEqual(parameter_names(["HEADER_N", "n", "memory", "HEADER", "headerN", "N_"]), {"HEADER_N": "headerN", "n": "n", "memory": "memory2", "HEADER": "header", "headerN": "headerN2", "N_": "n2"})

  def test_the_names_of_a_text_are_replaced_and_the_rest_is_kept(self):
    names = parameter_names(["HEADER_N", "n"])
    self.assertEqual(replace_names("((HEADER_N * 2) - n) + a->n + 0x1F + obj.n", names), "((headerN * 2) - n) + a->n + 0x1F + obj.n")
    self.assertEqual(replace_names(15, names), 15)


class FunctionOfATransferTest(unittest.TestCase):
  def test_the_prototype_takes_the_names_of_the_fields_and_the_call_gives_them(self):
    text = "volatile Buffer arr[64];\n.kernel k direct {\n  Transfer t = { type: words, mode: basic, memory: arr, count: HEADER_M + 1 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n@kernel k config | exec\nvoid f() { }\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("static inline void kTLoad(volatile u32* memory, u32 spadOffset, u32 headerM) {", out)
    self.assertIn("vme_dma(ITERATION, DIMS, (headerM + 1));", out)
    self.assertIn("kTLoad(arr, VME_TOP_BUFF0_WOFF, HEADER_M);", out)
    self.assertNotIn("HEADER_M +", out)

  def test_a_load_and_a_store_of_the_blocks_are_functions_before_the_function_that_holds_them(self):
    text = (
      "volatile Buffer arr[64];\n.kernel k direct {\n}\n"
      "void f(int n) {\n"
      "  @kernel k config {\n    Transfer t = { type: words, mode: basic, memory: arr, count: n };\n    .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n  }\n"
      "  @kernel k exec {\n    Transfer t = { type: words, mode: basic, memory: arr, count: 3 };\n    .store { .transfer = t; .scope = global; .offsets { .base1 = 8; } }\n  }\n}\n"
    )
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("static inline void fTLoad(volatile u32* memory, u32 spadOffset, u32 n) {", out)
    self.assertIn("static inline void f2TStore(volatile u32* memory, u32 spadOffset) {", out)
    self.assertLess(out.index("static inline void f2TStore"), out.index("void f(int n) {"))
    self.assertLess(out.index("void f(int n) {"), out.index("fTLoad(arr, VME_TOP_BUFF0_WOFF, n);"))
    self.assertLess(out.index("fTLoad(arr, VME_TOP_BUFF0_WOFF, n);"), out.index("f2TStore(arr, VME_BASE_BUFF1_WOFF + 8);"))
    self.assertEqual(out.count("vme_dma(MEMORY"), 2)
