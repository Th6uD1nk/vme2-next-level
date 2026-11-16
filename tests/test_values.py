import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vmeg.blocks import body_tokens, find_blocks
from vmeg.kernel import generate, input_agu_count, new_state, parameter_names, replace_names, resolve_extended_offsets, resolve_idle_routing, resolve_write_routing, run_statements, source_ref, staging_depths, staging_refs, transfer_names
from vmeg.parser import Parser, parse_body
from vmeg.registry import kernel_definitions
from vmeg.transfers import TRANSFER_KINDS
from vmegc import render
from vmee.listing import defines, emulations, format_listing


def agu_count(body, prefix="", suffix=""):
  text = prefix + ".kernel k direct {\n" + body + "\n  Agu t = { count: n };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f() { }\n" + suffix
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
  text = ".kernel k direct {\n  Agu t = { count: 3 }, w = { count: 3, cyc: auto };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }\n  .pe1 { .top = t; .write = w; " + second + " }\n}\n@kernel k config | exec\nvoid f() { }\n"
  warnings = []
  generate(text, find_blocks(text)[0], warnings)
  return [message for _, message in warnings if "shares" in message]


class CycAutoTest(unittest.TestCase):
  def test_auto_is_three_cycles_plus_three_per_fu_of_the_chain_and_a_shift_follows_it(self):
    self.assertEqual(cyc_line(".spad = top0 + base0;"), cyc_mode("6"))
    self.assertEqual(cyc_line(".spad = clamp(top0 + base0, 0, 255);"), cyc_mode("9"))
    self.assertEqual(cyc_line(".spad = clamp(top0 + base0, 0, 255);", "auto - 1"), cyc_mode("8"))

  def test_a_shared_write_agu_with_auto_warns_only_when_the_pes_need_different_delays(self):
    self.assertEqual(shared_warnings(".spad = clamp(top1 + top1, 0, 9);"), ["pe1 shares the write Agu 'w' with pe0 but its operations need another delay, cyc: auto follows pe0"])
    self.assertEqual(shared_warnings(".spad = top1 - top1;"), [])


def kernel_lines(body, compat):
  text = ".kernel k direct {\n  .pe0 { " + body + " }\n}\n@kernel k config | exec\nvoid f() { }\n"
  code = generate(text, find_blocks(text)[0], [], compat)
  return [line.strip() for line in code.splitlines() if "vme_fu" in line or "fu_reg" in line]


def agu_lines(body, kind):
  text = ".kernel k direct {\n" + body + "\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }\n}\n@kernel k config | exec\nvoid f() { }\n"
  code = generate(text, find_blocks(text)[0], [], None)
  return [line.strip() for line in code.splitlines() if f"agu_{kind}(" in line]


class AguModeTest(unittest.TestCase):
  def test_the_repeat_of_a_read_agu_is_written_without_inner0_too(self):
    self.assertEqual(agu_lines("  Agu t = { count: 15, repeat: true };\n  Agu w = { count: 15, cyc: 6 };", "top"), [
      "vme_pe0(agu_top(MODE), VME_DEF_MODE);",
      "vme_pe0(agu_top(COUNT), VME_DEF_STEP, 0xf);",
      "vme_pe0(agu_top(FORMAT_0), VME_RING_TOKEN);",
    ])

  def test_an_agu_of_the_mode_2_writes_its_count_and_swaps_the_fields_of_inner0(self):
    self.assertEqual(agu_lines("  Agu(2) t = { offset: 128, count: 7, inner0: { count: 3, step: 1 }, repeat: true };\n  Agu w = { count: 15, cyc: 6 };", "top"), [
      "vme_pe0(agu_top(MODE), agu_mode(2), 0x80);",
      "vme_pe0(agu_top(COUNT), VME_DEF_STEP, 7);",
      "vme_pe0(agu_top(INNER_0), agu_step(1), 3);",
      "vme_pe0(agu_top(FORMAT_0), VME_RING_TOKEN);",
    ])
    self.assertEqual(agu_lines("  Agu t = { count: 15 };\n  Agu(2) w = { offset: 4, count: 15, step: 2, cyc: 6, bubbles: 2, sync: true };", "write"), [
      "vme_pe0(agu_write(MODE), agu_mode(2), 4, vme_cyc(6));",
      "vme_pe0(agu_write(COUNT), agu_step(2), 0xf);",
      "vme_pe0(agu_write(FORMAT_0), 2);",
      "vme_pe0(agu_write(FORMAT_1), VME_END_TOKEN);",
    ])


class CompatTest(unittest.TestCase):
  def test_the_option_fat_replaces_the_opcode_that_is_not_portable_by_its_variant(self):
    self.assertEqual(kernel_lines(".spad = top0 + base0;", None), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD));"])
    self.assertEqual(kernel_lines(".spad = top0 + base0;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD_OFA));", "vme_pe0(fu_reg(PRIMARY, A), 0);"])
    self.assertEqual(kernel_lines(".spad = top0 - base0;", None), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_SUB));"])
    self.assertEqual(kernel_lines(".spad = top0 - base0;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(0x028));"])
    self.assertEqual(kernel_lines(".spad = (top0 - base0) >> 1;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(0x028), 1);"])
    self.assertEqual(kernel_lines(".spad = clamp((top0 - base0) >> 1, 0, 127);", "fat"), [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(0x028), 1);",
      "vme_pe0(vme_fu(SECONDARY), vme_mux(NONE, STAGING_0), fu_code(OP_CLP));",
      "vme_pe0(fu_reg(SECONDARY, A), 0x7f);",
      "vme_pe0(fu_reg(SECONDARY, B), 0);",
    ])
    self.assertEqual(kernel_lines(".spad = top0 >> 3;", None), ["vme_pe0(vme_fu(PRIMARY), vme_mux(NONE, TOP_0), fu_code(0x014), 3);"])
    self.assertEqual(kernel_lines(".spad = top0 >> 3;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(NONE, TOP_0), fu_code(OP_SHR_CST_OFA));", "vme_pe0(fu_reg(PRIMARY, A), 0);", "vme_pe0(fu_reg(PRIMARY, B), 3);"])
    self.assertEqual(kernel_lines(".spad = (top0 & 4) ? 0 : 9;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0), fu_code(OP_SEL_CST_OFB));", "vme_pe0(fu_reg(PRIMARY, A), 4);", "vme_pe0(fu_reg(PRIMARY, B), 9);"])
    self.assertEqual(kernel_lines(".spad = (top0 & 4) ? 9 : 0;", "fat"), ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0), fu_code(OP_SEL_CST));", "vme_pe0(fu_reg(PRIMARY, A), 4);", "vme_pe0(fu_reg(PRIMARY, B), 9);"])


class RoundTest(unittest.TestCase):
  def test_round_sets_the_bit_6_of_the_operation_it_wraps_before_or_after_the_shift_and_only_once(self):
    plain = ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD), 1);"]
    marked = ["vme_pe0(vme_fu(PRIMARY), vme_mux(TOP_0, BASE_0), fu_code(OP_ADD), 1, (1 << 6));"]
    self.assertEqual(kernel_lines(".spad = top0 + base0 >> 1;", None), plain)
    self.assertEqual(kernel_lines(".spad = round(top0 + base0) >> 1;", None), marked)
    self.assertEqual(kernel_lines(".spad = round(top0 + base0 >> 1);", None), marked)
    with self.assertRaises(ValueError):
      kernel_lines(".spad = round(round(top0 + base0));", None)
    self.assertEqual(kernel_lines(".spad = round(5);", None), [
      "vme_pe0(vme_fu(PRIMARY), vme_mux(NONE, STAGING_0), fu_code(OP_CST), (1 << 6));",
      "vme_pe0(fu_reg(PRIMARY, B), 5);",
    ])


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
      "    Transfer(Words) t = { memory: arr, count: last, gap: 0 };\n"
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


def dma_lines(transfer, prefix="", kind=""):
  text = prefix + "volatile Buffer arr[64];\n.kernel k direct {\n  Transfer" + kind + " t = " + transfer + ";\n  .load { .transfer = t; .scope = global; }\n}\n@kernel k config | exec\nvoid f() { }\n"
  out = render(text, find_blocks(text), "t.vmeg.c")
  return [line.strip() for line in out.splitlines() if line.strip().startswith("vme_dma(ITERATION") or line.strip().startswith("vme_dma(GROUP")]


class TransferValuesTest(unittest.TestCase):
  def test_a_macro_that_is_not_in_the_file_is_copied_in_the_fields_of_a_transfer(self):
    transfer = "{ memory: arr, count: HEADER_N - 1, gap: 0, step: HEADER_STEP, group: { size: 3, outer: HEADER_OUT, inner: 1 } }"
    self.assertEqual(dma_lines(transfer, kind="(Words)"), [
      "vme_dma(ITERATION, DIMS, (headerN - 1), 0);",
      "vme_dma(ITERATION, STEP, headerStep);",
      "vme_dma(GROUP, SIZE, 3);",
      "vme_dma(GROUP, STEPS, headerOut, 1);",
    ])

  def test_an_extended_transfer_writes_both_values_of_the_dims_with_a_gap_of_0_when_it_is_left_out(self):
    self.assertEqual(dma_lines("{ memory: arr, count: 7 }", kind="(Words)"), ["vme_dma(ITERATION, DIMS, 7, 0);"])
    self.assertEqual(dma_lines("{ memory: arr, count: 7, gap: 3 }", kind="(Words)"), ["vme_dma(ITERATION, DIMS, 7, 3);"])

  def test_a_known_part_is_replaced_by_its_number_in_the_copy_and_a_known_value_is_a_number(self):
    prefix = "#define KNOWN 64\n"
    self.assertEqual(dma_lines("{ memory: arr, count: KNOWN + HEADER }", prefix), ["vme_dma(ITERATION, DIMS, (64 + header));"])
    self.assertEqual(dma_lines("{ memory: arr, count: KNOWN - 1 }", prefix), ["vme_dma(ITERATION, DIMS, 63);"])

  def test_a_negative_number_is_still_refused(self):
    with self.assertRaises(ValueError) as caught:
      dma_lines("{ memory: arr, count: 0 - 1 }")
    self.assertIn("cannot be negative", str(caught.exception))


class TransferListingTest(unittest.TestCase):
  def test_the_listing_shows_the_words_of_a_transfer_with_an_unknown_macro_as_a_text(self):
    text = (
      "#define KNOWN 64\nvolatile Buffer a[64];\nvolatile Buffer b[64];\n@emulate \"e\"\n.kernel k direct {\n"
      "  Transfer t = { memory: a, count: HEADER_COUNT };\n"
      "  Transfer u = { memory: b, count: KNOWN - 1 };\n"
      "  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n"
      "  .load { .transfer = u; .scope = global; .offsets { .top1 = 0; } }\n}\n"
    )
    lines = format_listing(emulations(text), defines(text)).splitlines()
    self.assertEqual(lines[2:4], ["    TOP_0   (HEADER_COUNT + 1) words  from a", "    TOP_1   64 words  from b"])


if __name__ == "__main__":
  unittest.main()


class WordsOfATransferTest(unittest.TestCase):
  def test_the_words_written_are_the_count_plus_one_and_the_repetitions_of_a_step_of_0_are_multiplied(self):
    basic, extended = TRANSFER_KINDS["basic"], TRANSFER_KINDS["Words"]
    self.assertEqual(basic.words({"count": 15}), 16)
    self.assertEqual(extended.words({"count": 15, "gap": 3, "step": 4}), 16)
    self.assertEqual(extended.words({"count": 1, "gap": 23, "step": 0}), 48)
    self.assertEqual(extended.words({"count": 1, "step": 0}), 2)
    self.assertEqual(extended.words({"count": "HEADER", "gap": 3, "step": 0}), "((HEADER + 1) * 4)")


class OffsetsOfATransferTest(unittest.TestCase):
  def test_a_negative_offset_is_subtracted_from_its_buffer_a_computed_one_too_and_an_unknown_one_is_left_to_the_c(self):
    text = (
      "#define A 6\nvolatile Buffer arr[16];\n.kernel k direct {\n"
      "  Transfer t = { memory: arr, count: 15 };\n"
      "  .load { .transfer = t; .scope = global; .offsets { .top1 = -8; .top0 = 4; .base2 = 5 - A; .top2 = 3 - UNKNOWN; } }\n"
      "}\n@kernel k config | exec\nvoid f() { }\n"
    )
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("kTLoad(arr, VME_TOP_BUFF1_WOFF - 8);", out)
    self.assertIn("kTLoad(arr, VME_TOP_BUFF0_WOFF + 4);", out)
    self.assertIn("kTLoad(arr, VME_BASE_BUFF2_WOFF - 1);", out)
    self.assertIn("kTLoad(arr, VME_TOP_BUFF2_WOFF + (3 - UNKNOWN));", out)

  def test_extended_slots_4_to_7_add_0x400_in_render_registry_and_listing(self):
    text = (
      "volatile Buffer arr[16], dst[16];\n"
      "@emulate \"ext_xfer\"\n"
      ".kernel k extended {\n"
      "  Transfer t = { memory: arr, count: 3 };\n"
      "  .load { .transfer = t; .scope = global; .offsets { .top4 = 0; .base7 = 8; .top5 = -4; } }\n"
      "}\n"
      "void f() {\n"
      "  @emulate \"ext_blk\" {\n"
      "    @kernel k config | exec {\n"
      "      Transfer s = { memory: dst, count: 3 };\n"
      "      .store { .transfer = s; .scope = global; .offsets { .base6 = 4; } }\n"
      "    }\n"
      "  }\n"
      "}\n"
    )
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("kTLoad(arr, VME_TOP_BUFF0_WOFF + 0x400);", out)
    self.assertIn("kTLoad(arr, VME_BASE_BUFF3_WOFF + 0x408);", out)
    self.assertIn("kTLoad(arr, VME_TOP_BUFF1_WOFF + 0x3fc);", out)
    self.assertIn("fSStore(dst, VME_BASE_BUFF2_WOFF + 0x404);", out)
    defs = kernel_definitions("t.vmeg.c", text)
    self.assertEqual(defs[0]["mode"], "extended")
    self.assertIn("VME_TOP_BUFF0_WOFF + 0x400", defs[0]["loads"][0]["calls"][0])
    emus = emulations(text)
    self.assertEqual(emus[0]["mode"], "extended")
    self.assertEqual([entry[:2] for entry in emus[0]["global"]], [("TOP_4", 4), ("BASE_7", 4), ("TOP_5", 4)])
    self.assertEqual([entry[:2] for entry in emus[1]["stores"]["global"]], [("BASE_6", 4)])


class NamesOfATransferTest(unittest.TestCase):
  def test_the_names_are_found_once_in_the_order_of_the_fields(self):
    transfer = {"kind": TRANSFER_KINDS["Words"], "count": "((HEADER_N * 2) - n)", "gap": "n", "step": "HEADER_STEP", "group": {"size": 3}}
    self.assertEqual(transfer_names(transfer), ["HEADER_N", "n", "HEADER_STEP"])

  def test_a_number_a_member_and_a_value_that_is_not_a_text_have_no_name(self):
    self.assertEqual(transfer_names({"kind": TRANSFER_KINDS["basic"], "count": "0x1F + obj.size + p->len"}), ["obj", "p"])
    self.assertEqual(transfer_names({"kind": TRANSFER_KINDS["basic"], "count": 15}), [])

  def test_the_parameters_are_camel_case_and_never_collide(self):
    self.assertEqual(parameter_names(["HEADER_N", "n", "memory", "HEADER", "headerN", "N_"]), {"HEADER_N": "headerN", "n": "n", "memory": "memory2", "HEADER": "header", "headerN": "headerN2", "N_": "n2"})

  def test_the_names_of_a_text_are_replaced_and_the_rest_is_kept(self):
    names = parameter_names(["HEADER_N", "n"])
    self.assertEqual(replace_names("((HEADER_N * 2) - n) + a->n + 0x1F + obj.n", names), "((headerN * 2) - n) + a->n + 0x1F + obj.n")
    self.assertEqual(replace_names(15, names), 15)


class FunctionOfATransferTest(unittest.TestCase):
  def test_the_prototype_takes_the_names_of_the_fields_and_the_call_gives_them(self):
    text = "volatile Buffer arr[64];\n.kernel k direct {\n  Transfer t = { memory: arr, count: HEADER_M + 1 };\n  .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n}\n@kernel k config | exec\nvoid f() { }\n"
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("static inline void kTLoad(volatile u32* memory, u32 spadOffset, u32 headerM) {", out)
    self.assertIn("vme_dma(ITERATION, DIMS, (headerM + 1));", out)
    self.assertIn("kTLoad(arr, VME_TOP_BUFF0_WOFF, HEADER_M);", out)
    self.assertNotIn("HEADER_M +", out)

  def test_a_load_and_a_store_of_the_blocks_are_functions_before_the_function_that_holds_them(self):
    text = (
      "volatile Buffer arr[64];\n.kernel k direct {\n}\n"
      "void f(int n) {\n"
      "  @kernel k config {\n    Transfer t = { memory: arr, count: n };\n    .load { .transfer = t; .scope = global; .offsets { .top0 = 0; } }\n  }\n"
      "  @kernel k exec {\n    Transfer t = { memory: arr, count: 3 };\n    .store { .transfer = t; .scope = global; .offsets { .base1 = 8; } }\n  }\n}\n"
    )
    out = render(text, find_blocks(text), "t.vmeg.c")
    self.assertIn("static inline void fTLoad(volatile u32* memory, u32 spadOffset, u32 n) {", out)
    self.assertIn("static inline void f2TStore(volatile u32* memory, u32 spadOffset) {", out)
    self.assertLess(out.index("static inline void f2TStore"), out.index("void f(int n) {"))
    self.assertLess(out.index("void f(int n) {"), out.index("fTLoad(arr, VME_TOP_BUFF0_WOFF, n);"))
    self.assertLess(out.index("fTLoad(arr, VME_TOP_BUFF0_WOFF, n);"), out.index("f2TStore(arr, VME_BASE_BUFF1_WOFF + 8);"))
    self.assertEqual(out.count("vme_dma(MEMORY"), 2)


def staging_lines(body, head=""):
  text = head + ".kernel k direct {\n" + body + "\n}\n@kernel k config | exec\nvoid f() { }\n"
  out = render(text, find_blocks(text), "t.vmeg.c")
  return [line.strip() for line in out.splitlines() if "vme_fu" in line or "fu_reg" in line]


STAGING_LOOP = "  for n in 0..2 {\n    pe[n] { s[n] = top[n] + 1; .spad = s[n] + 2; }\n  }"
STAGING_MANUAL = "  .pe0 { s0 = top0 + 1; .spad = s0 + 2; }\n  .pe1 { s1 = top1 + 1; .spad = s1 + 2; }\n  .pe2 { s2 = top2 + 1; .spad = s2 + 2; }"


class StagingArrayTest(unittest.TestCase):
  def test_an_array_in_a_loop_gives_the_code_of_the_scalars_written_one_by_one(self):
    expected = staging_lines("  Staging s0, s1, s2;\n" + STAGING_MANUAL)
    self.assertEqual(staging_lines("  Staging s[3];\n" + STAGING_LOOP), expected)
    self.assertEqual(staging_lines(STAGING_LOOP, "@declare { Staging s[3]; }\n"), expected)

  def test_a_pe_reads_the_element_set_by_another_pe(self):
    lines = staging_lines("  Staging s[2];\n  .pe0 { s[0] = top0 + 1; }\n  .pe1 { .spad = s[0] + top1; }")
    self.assertIn("vme_pe1(vme_fu(PRIMARY), vme_mux(STAGING_0, TOP_1), fu_code(OP_ADD));", lines)

  def test_the_misuse_of_an_array_is_refused_with_the_line(self):
    cases = [
      ("Staging s[2];\n  .pe0 { s[2] = top0 + 1; }", "line 3: s[2]: index out of range (0 to 1)"),
      ("Staging s[2];\n  .pe0 { s = top0 + 1; }", "line 3: 's' is an array, write s[...]"),
      ("Staging s;\n  .pe0 { s[0] = top0 + 1; }", "line 3: 's' is not an array"),
      ("Staging s[0];", "line 2: s[...]: array size must be a number of 1 or more"),
      ("Staging s[2];\n  .pe0 { .spad = s[1] + 1; }", "line 3: the Staging variable 's[1]' is read before it is set"),
      ("Staging s[2];\n  .pe0 { s[0] = top0 + 1; }\n  .pe1 { s[0] = top1 + 1; }", "line 4: the Staging variable 's[0]' is already set at line 3"),
      ("Staging s[2];\n  Staging s;", "line 3: the Staging variable 's' is declared twice"),
    ]
    for body, message in cases:
      with self.subTest(body=body):
        with self.assertRaises(ValueError) as ctx:
          staging_lines("  " + body)
        self.assertTrue(str(ctx.exception).endswith(message), str(ctx.exception))


def int_lines(body, head=""):
  text = head + ".kernel k direct {\n" + body + "\n}\n@kernel k config | exec\nvoid f() { }\n"
  out = render(text, find_blocks(text), "t.vmeg.c")
  return [line.strip() for line in out.splitlines() if "agu_top(" in line or "fu_reg(" in line or "vme_fu(" in line]


class IntArrayTest(unittest.TestCase):
  def test_an_array_with_initializers_configures_an_agu(self):
    lines = int_lines("  Int a[2] = { 5, 10 };\n  Agu t = { count: a[0], step: a[1] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0xa), 5);", lines)

  def test_an_array_can_be_declared_in_declare_block(self):
    lines = int_lines("  Agu t = { count: a[0], step: a[1] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }", "@declare { Int a[2] = { 5, 10 }; }\n")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0xa), 5);", lines)

  def test_elements_can_be_assigned_and_used_in_expressions(self):
    lines = int_lines("  Int a[2];\n  a[0] = 5;\n  a[1] = a[0] + 5;\n  Agu t = { count: a[0], step: a[1] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0xa), 5);", lines)

  def test_elements_can_be_populated_in_a_loop(self):
    lines = int_lines("  Int a[2];\n  for n in 0..1 { a[n] = (n + 1) * 4; }\n  Agu t = { count: a[0], step: a[1] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(8), 4);", lines)

  def test_elements_can_be_read_in_pe_operations(self):
    lines = int_lines("  Int a[2] = { 10, 20 };\n  .pe0 { .spad = top0 + a[0]; }\n  .pe1 { .spad = top1 + a[1]; }")
    self.assertIn("vme_pe0(fu_reg(PRIMARY, B), 0xa);", lines)
    self.assertIn("vme_pe1(fu_reg(PRIMARY, B), 0x14);", lines)

  def test_the_misuse_of_an_array_is_refused_with_the_line(self):
    cases = [
      ("Int a[0];", "line 2: a[...]: array size must be a number of 1 or more"),
      ("Int a[2] = { 1, 2, 3 };", "line 2: a[...]: too many initializers (3 for size 2)"),
      ("Int a[2];\n  a[2] = 1;", "line 3: a[2]: index out of range (0 to 1)"),
      ("Int a[2];\n  a[-1] = 1;", "line 3: a[-1]: index out of range (0 to 1)"),
      ("Int a = 1;\n  a[0] = 1;", "line 3: 'a' is not an array"),
      ("Int a[2];\n  Int a = 1;", "line 3: 'a' is defined twice"),
      ("Int a[2];\n  Int a[2];", "line 3: 'a' is defined twice"),
      ("Int auto[2];", "line 2: auto is reserved for the cyc of a write AGU"),
      ("Staging s[2];\n  Int s[2];", "line 3: 's' is already declared as a Staging variable"),
      ("Agu t = { count: 3 };\n  Int t[2];", "line 3: 't' is already declared as an Agu variable"),
      ("Transfer in = { memory: buf, count: 4 };\n  Int in[2];", "line 3: 'in' is already declared as a Transfer variable"),
      ("Staging s[2];\n  s[0] = 1;", "line 3: 's' is a Staging variable, only an Int variable can receive an assignment"),
      ("b[0] = 1;", "line 2: unknown array 'b'"),
    ]
    for body, message in cases:
      with self.subTest(body=body):
        with self.assertRaises(ValueError) as ctx:
          int_lines("  " + body)
        self.assertTrue(str(ctx.exception).endswith(message), str(ctx.exception))


def agu_array_lines(body, head=""):
  text = head + ".kernel k direct {\n" + body + "\n}\n@kernel k config | exec\nvoid f() { }\n"
  out = render(text, find_blocks(text), "t.vmeg.c")
  return [line.strip() for line in out.splitlines() if "agu_top(" in line or "agu_write(" in line or "vme_icn(AGU_" in line]


AGU_ARRAY_LOOP = "  Agu t[2] = { { count: 10 }, { count: 20 } };\n  Agu w = { count: 3 };\n  for n in 0..1 {\n    pe[n] { .top = t[n]; .write = w; .spad = top[n] + top[n]; }\n  }"
AGU_ARRAY_MANUAL = "  Agu t0 = { count: 10 }, t1 = { count: 20 };\n  Agu w = { count: 3 };\n  .pe0 { .top = t0; .write = w; .spad = top0 + top0; }\n  .pe1 { .top = t1; .write = w; .spad = top1 + top1; }"


class AguArrayTest(unittest.TestCase):
  def test_an_array_in_a_loop_gives_the_code_of_the_scalars_written_one_by_one(self):
    self.assertEqual(agu_array_lines(AGU_ARRAY_LOOP), agu_array_lines(AGU_ARRAY_MANUAL))

  def test_an_array_can_be_declared_in_declare_block(self):
    lines = agu_array_lines("  Agu w = { count: 3 };\n  .pe0 { .top = t[0]; .write = w; .spad = top0 + top0; }\n  .pe1 { .top = t[1]; .write = w; .spad = top1 + top1; }", "@declare { Agu t[2] = { { count: 10 }, { count: 20 } }; }\n")
    self.assertIn("vme_pe0(agu_top(COUNT), VME_DEF_STEP, 0xa);", lines)
    self.assertIn("vme_pe1(agu_top(COUNT), VME_DEF_STEP, 0x14);", lines)

  def test_elements_can_be_assigned_and_used_in_pes(self):
    lines = agu_array_lines("  Agu t[2];\n  t[0] = { count: 10 };\n  t[1] = { count: 20 };\n  Agu w = { count: 3 };\n  .pe0 { .top = t[0]; .write = w; .spad = top0 + top0; }\n  .pe1 { .top = t[1]; .write = w; .spad = top1 + top1; }")
    self.assertIn("vme_pe0(agu_top(COUNT), VME_DEF_STEP, 0xa);", lines)
    self.assertIn("vme_pe1(agu_top(COUNT), VME_DEF_STEP, 0x14);", lines)

  def test_an_element_can_be_shared_between_pes(self):
    lines = agu_array_lines("  Agu t[2] = { { count: 10 }, { count: 20 } };\n  Agu w = { count: 3 };\n  .pe0 { .top = t[0]; .write = w; .spad = top0 + top0; }\n  .pe1 { .top = t[0]; .write = w; .spad = top1 + top1; }")
    self.assertIn("vme_icn(AGU_TOP, 0x55005500);", lines)

  def test_the_misuse_of_an_array_is_refused_with_the_line(self):
    cases = [
      ("Agu t[0];", "line 2: t[...]: array size must be a number of 1 or more"),
      ("Agu t[2] = { { count: 1 }, { count: 2 }, { count: 3 } };", "line 2: t[...]: too many initializers (3 for size 2)"),
      ("Agu t[2];\n  Agu w = { count: 3 };\n  .pe0 { .top = t[0]; .write = w; .spad = top0 + top0; }", "line 4: the Agu variable 't[0]' is read before it is set"),
      ("Agu t[2] = { { count: 3 } };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }", "line 4: 't' is an array, write t[...]"),
      ("Agu t = { count: 3 };\n  Agu w = { count: 3 };\n  .pe0 { .top = t[0]; .write = w; .spad = top0 + top0; }", "line 4: 't' is not an array"),
      ("Agu t[2] = { { count: 3 } };\n  Agu w = { count: 3 };\n  .pe0 { .top = t[2]; .write = w; .spad = top0 + top0; }", "line 4: t[2]: index out of range (0 to 1)"),
      ("Agu t[2] = { { count: 3 } };\n  Agu w = { count: 3 };\n  .pe0 { .top = t[-1]; .write = w; .spad = top0 + top0; }", "line 4: t[-1]: index out of range (0 to 1)"),
      ("Agu t[2];\n  t[0] = 5;", "line 3: 't' is an Agu variable, it takes parameters between braces"),
      ("Staging s[2];\n  Agu s = { count: 3 };", "line 3: 's' is already declared as a Staging variable"),
      ("Int a[2];\n  Agu a = { count: 3 };", "line 3: 'a' is already declared as an Int variable"),
      ("Int a = 1;\n  Agu a = { count: 3 };", "line 3: 'a' is already declared as an Int variable"),
      ("Agu t[2];\n  Agu t = { count: 3 };", "line 3: the Agu variable 't' is declared twice"),
      ("Agu t[2];\n  Agu t[2];", "line 3: the Agu variable 't' is declared twice"),
      ("Agu t[2] = { { count: 3 } };\n  .pe0 { .top = t[0]; .base = t[0]; }", "line 3: the Agu variable 't[0]' is already bound to .top, it cannot be bound to .base"),
    ]
    for body, message in cases:
      with self.subTest(body=body):
        with self.assertRaises(ValueError) as ctx:
          agu_array_lines("  " + body)
        self.assertTrue(str(ctx.exception).endswith(message), str(ctx.exception))


class ForLoopTest(unittest.TestCase):
  def test_a_loop_with_a_positive_step_iterates_by_the_step(self):
    lines = int_lines("  Int a[7];\n  for p in 0..6 step 2 { a[p] = p * 10; }\n  Agu t = { count: a[6], step: a[2] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0x14), 0x3c);", lines)

  def test_a_loop_with_by_keyword_iterates_by_the_step(self):
    lines = int_lines("  Int a[7];\n  for p in 0..6 by 2 { a[p] = p * 10; }\n  Agu t = { count: a[6], step: a[2] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0x14), 0x3c);", lines)

  def test_a_descending_loop_without_step_iterates_downwards(self):
    lines = int_lines("  Int a[4];\n  for p in 3..0 { a[p] = p * 10; }\n  Agu t = { count: a[0], step: a[3] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0x1e), 0);", lines)

  def test_a_descending_loop_with_a_step_iterates_downwards_by_the_step(self):
    lines = int_lines("  Int a[7];\n  for p in 6..0 step 2 { a[p] = p * 10; }\n  Agu t = { count: a[0], step: a[4] };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
    self.assertIn("vme_pe0(agu_top(COUNT), agu_step(0x28), 0);", lines)

  def test_staging_elements_and_pes_can_be_unrolled_with_step(self):
    lines = staging_lines("  Staging s[4];\n  for p in 0..3 step 2 {\n    pe[p] { s[p] = top[p] + 1; .spad = s[p] + 2; }\n  }")
    self.assertIn("vme_pe0(vme_fu(PRIMARY), vme_mux(NONE, TOP_0), fu_code(OP_ADD_CST));", lines)
    self.assertIn("vme_pe2(vme_fu(PRIMARY), vme_mux(NONE, TOP_2), fu_code(OP_ADD_CST));", lines)

  def test_invalid_step_or_bounds_are_rejected(self):
    cases = [
      ("for p in 0..4 step 0 { a[p] = p; }", "line 3: for p: step must be a positive number of 1 or more"),
      ("for p in 0..4 step -1 { a[p] = p; }", "line 3: for p: step must be a positive number of 1 or more"),
      ("for p in 0..4 step x { a[p] = p; }", "line 3: for p: bounds and step must be numbers"),
    ]
    for clause, message in cases:
      with self.subTest(clause=clause):
        with self.assertRaises(ValueError) as ctx:
          int_lines("  Int a[5];\n  " + clause + "\n  Agu t = { count: 1 };\n  Agu w = { count: 3 };\n  .pe0 { .top = t; .write = w; .spad = top0 + top0; }")
        self.assertTrue(str(ctx.exception).endswith(message), str(ctx.exception))


class SpadRedirectTest(unittest.TestCase):
  def test_redirected_spad_derives_extended_write_icn_and_unused_buffers_stay_4(self):
    lines = agu_array_lines("  .pe3 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[0] = top3; }")
    self.assertIn("vme_icn(AGU_WRITE, 0xccc3cccb);", lines)
    self.assertIn("vme_pe3(agu_write(MODE), VME_DEF_MODE, vme_cyc(4));", lines)

  def test_dotted_statement_and_self_extended_spad_are_supported(self):
    lines = agu_array_lines("  .pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; }\n  .pe0.spad[0] = top0;")
    self.assertIn("vme_icn(AGU_WRITE, 0xddd0ddd8);", lines)

  def test_swapped_redirected_outputs_derive_crossbar_without_clobbering(self):
    lines = agu_array_lines("  .pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[3] = top0; }\n  .pe3 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[0] = top3; }")
    self.assertIn("vme_icn(AGU_WRITE, 0x8dd38ddb);", lines)
    self.assertIn("vme_pe0(agu_write(MODE), VME_DEF_MODE, 0x1800, vme_cyc(4));", lines)
    self.assertIn("vme_pe3(agu_write(MODE), VME_DEF_MODE, vme_cyc(4));", lines)

  def test_regs_write_routing_follows_source_order(self):
    after = agu_array_lines("  .pe3 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[0] = top3; }\n  .regs { .icn { .write = 0x1234; } }")
    self.assertIn("vme_icn(AGU_WRITE, 0x00001234);", after)
    before = agu_array_lines("  .regs { .icn { .write = 0x1111; } }\n  .pe3 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[0] = top3; }")
    self.assertIn("vme_icn(AGU_WRITE, 0x0000111b);", before)

  def test_missing_write_warns_when_redirected_spad_has_no_write(self):
    text = ".kernel k direct {\n  .pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[1] = top0; }\n  .pe3 { .top = { count: 4 }; .spad[0] = top3; }\n}\n@kernel k config | exec\nvoid f() { }\n"
    warnings = []
    generate(text, find_blocks(text)[0], warnings)
    messages = [message for _, message in warnings]
    self.assertEqual(messages, ["pe3 has an operation but no .write is bound in this kernel"])

  def test_single_named_write_agu_is_allowed_with_redirected_spad(self):
    lines = agu_array_lines("  Agu w = { count: 4, cyc: 4 };\n  .pe2 { .top = { count: 4 }; .write = w; .spad[1] = top2; }")
    self.assertIn("vme_pe2(agu_write(MODE), VME_DEF_MODE, 0x800, vme_cyc(4));", lines)
    self.assertIn("vme_icn(AGU_WRITE, 0xcca0ccac);", lines)

  def test_automatic_write_offset_combines_base_and_user_offset(self):
    cases = [
      ("  .pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[2] = top0; }", "vme_pe0(agu_write(MODE), VME_DEF_MODE, 0x1000, vme_cyc(4));", "0xd8d1d8dd"),
      ("  .pe0 { .top = { count: 4 }; .write = { count: 4, offset: 16, cyc: 4 }; .spad[1] = top0; }", "vme_pe0(agu_write(MODE), VME_DEF_MODE, 0x810, vme_cyc(4));", "0xdd81dd8d"),
      ("  .pe0 { .top = { count: 4 }; .write = { count: 4, offset: -16, cyc: 4 }; .spad[1] = top0; }", "vme_pe0(agu_write(MODE), VME_DEF_MODE, 0x7f0, vme_cyc(4));", "0xdd81dd8d"),
      ("  .pe0 { .top = { count: 4 }; .write = { count: 4, offset: OFF, cyc: 4 }; .spad[3] = top0; }", "vme_pe0(agu_write(MODE), VME_DEF_MODE, (0x1800 + OFF) & 0xffff, vme_cyc(4));", "0x8dd18ddd"),
      ("  .pe0 { .top = { count: 4 }; .spad[2] = top0; .write = { count: 4, cyc: auto }; }", "vme_pe0(agu_write(MODE), VME_DEF_MODE, 0x1000, vme_cyc(6));", "0xd8d1d8dd"),
      ("  Agu(2) w = { count: 4, offset: 8 };\n  .pe0 { .top = { count: 4 }; .write = w; .spad[1] = top0; }", "vme_pe0(agu_write(MODE), agu_mode(2), 0x808);", "0xdd81dd8d"),
    ]
    for body, expected_mode, expected_icn in cases:
      with self.subTest(body=body):
        lines = agu_array_lines(body)
        self.assertIn(expected_mode, lines)
        self.assertIn(f"vme_icn(AGU_WRITE, {expected_icn});", lines)

  def test_for_loop_unrolls_redirected_spad_and_write_offsets(self):
    lines = agu_array_lines("  for i in 0..1 {\n    pe[i] { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[(i + 1) % 4] = top[i]; }\n  }")
    self.assertIn("vme_pe0(agu_write(MODE), VME_DEF_MODE, 0x800, vme_cyc(4));", lines)
    self.assertIn("vme_pe1(agu_write(MODE), VME_DEF_MODE, 0x1000, vme_cyc(4));", lines)
    self.assertIn("vme_icn(AGU_WRITE, 0xe982e98e);", lines)
    self.assertIn("vme_icn(AGU_TOP, 0x66106610);", lines)

  def test_unused_nibbles_isolate_pe0_above_1024_while_keeping_4_when_idle(self):
    pe0_long = agu_array_lines("  .pe0 { .top = { count: 1500 }; .write = { count: 1500, cyc: 4 }; .spad[2] = top0; }")
    self.assertIn("vme_icn(AGU_TOP, 0x55505550);", pe0_long)
    self.assertIn("vme_icn(AGU_BASE, 0x44444444);", pe0_long)
    self.assertIn("vme_icn(AGU_WRITE, 0xd8d1d8dd);", pe0_long)
    pe1_long = agu_array_lines("  .pe1 { .top = { count: 1500 }; .write = { count: 1500, cyc: 4 }; .spad[2] = top1; }")
    self.assertIn("vme_icn(AGU_TOP, 0x44144414);", pe1_long)
    self.assertIn("vme_icn(AGU_BASE, 0x44444444);", pe1_long)
    self.assertIn("vme_icn(AGU_WRITE, 0xc9c0c9cc);", pe1_long)
    pe3_base = agu_array_lines("  .pe3 { .base = { count: 1500 }; .write = { count: 1500, cyc: 4 }; .spad = base3; }")
    self.assertIn("vme_icn(AGU_TOP, 0x44444444);", pe3_base)
    self.assertIn("vme_icn(AGU_BASE, 0x34443444);", pe3_base)
    self.assertIn("vme_icn(AGU_WRITE, 0x34443444);", pe3_base)

  def test_idle_selection_handles_multiple_active_pes_and_preserves_warnings(self):
    three_pes = agu_array_lines("  .pe0 { .top = { count: 4 }; .base = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[3] = top0 + base0; }\n  .pe1 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[1] = top1; }\n  .pe2 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[2] = top2; }")
    self.assertIn("vme_icn(AGU_TOP, 0x72107210);", three_pes)
    self.assertIn("vme_icn(AGU_BASE, 0x55505550);", three_pes)
    self.assertIn("vme_icn(AGU_WRITE, 0x8a938a9f);", three_pes)
    pe0_pe2 = agu_array_lines("  .pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[2] = top0; }\n  .pe2 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[0] = top2; }")
    self.assertIn("vme_icn(AGU_TOP, 0x52505250);", pe0_pe2)
    self.assertIn("vme_icn(AGU_WRITE, 0xd8d2d8da);", pe0_pe2)
    text = ".kernel k direct {\n  .pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad = top0 + top1; }\n}\n@kernel k config | exec\nvoid f() { }\n"
    warnings = []
    generate(text, find_blocks(text)[0], warnings)
    self.assertEqual([message for _, message in warnings], ["top1 is read but no .top is bound in pe1 of this kernel"])

  def test_invalid_spad_redirections_are_rejected(self):
    cases = [
      (".pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[4] = top0; }", "line 2: spad[4]: buffer out of range (spad[0] to spad[3])"),
      (".pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[-1] = top0; }", "line 2: spad[-1]: buffer out of range (spad[0] to spad[3])"),
      (".pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[X] = top0; }", "line 2: spad destination index must be a number"),
      (".pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[2] = top0; }\n  .pe2 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad = top2; }", "line 3: base2 is written by both pe0 and pe2"),
      (".pe0 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[1] = top0; }\n  .pe3 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad[1] = top3; }", "line 3: base1 is written by both pe0 and pe3"),
      (".pe0 { .top = { count: 4 }; .spad[2] = top0; }\n  .pe2 { .top = { count: 4 }; .write = { count: 4, cyc: 4 }; .spad = top2; }", "line 3: base2 is written by both pe0 and pe2"),
      ("Agu w = { count: 4, cyc: 4 };\n  .pe0 { .top = { count: 4 }; .write = w; .spad = top0; }\n  .pe1 { .top = { count: 4 }; .write = w; .spad[2] = top1; }", "line 4: pe1 cannot share the write Agu 'w' with .spad[2]"),
      ("Agu w = { count: 4, cyc: 4 };\n  .pe0 { .top = { count: 4 }; .write = w; .spad[2] = top0; }\n  .pe1 { .top = { count: 4 }; .write = w; .spad = top1; }", "line 3: pe0 cannot share the write Agu 'w' with .spad[2]"),
      (".pe0 { .top = { count: 4 }; .write = { count: 4, offset: 32000, cyc: 4 }; .spad[1] = top0; }", "line 2: pe0.write: the offset 34048 is outside -32768 to 32767"),
    ]
    for body, message in cases:
      with self.subTest(body=body):
        with self.assertRaises(ValueError) as ctx:
          agu_array_lines("  " + body)
        self.assertTrue(str(ctx.exception).endswith(message), str(ctx.exception))


class ExtendedStagingTest(unittest.TestCase):
  def test_cross_pass_forward_routes_through_base_and_backward_raises(self):
    state = new_state(extended=True)
    state["stagings"] = {
      "p1_fu0": {"pe": 0, "unit": 0, "depth": 1, "line": 2},
      "p1_fu1": {"pe": 2, "unit": 1, "depth": 2, "line": 3},
      "p2_fu0": {"pe": 5, "unit": 0, "depth": 1, "line": 4},
      "p2_fu1": {"pe": 7, "unit": 1, "depth": 3, "line": 5},
    }
    pass2_refs = staging_refs(state, pe=4)
    self.assertEqual(source_ref(("name", "p1_fu0"), pass2_refs, 7), "BASE_0")
    self.assertEqual(source_ref(("name", "p1_fu1"), pass2_refs, 7), "BASE_2")
    self.assertEqual(source_ref(("name", "p2_fu0"), pass2_refs, 7), "STAGING_1")
    self.assertEqual(source_ref(("name", "p2_fu1"), pass2_refs, 7), "STAGING_7")
    self.assertTrue(state["stagings"]["p1_fu0"]["exported"])
    self.assertTrue(state["stagings"]["p1_fu1"]["exported"])
    self.assertNotIn("exported", state["stagings"]["p2_fu0"])
    pass1_refs = staging_refs(state, pe=1)
    self.assertEqual(source_ref(("name", "p1_fu0"), pass1_refs, 7), "STAGING_0")
    with self.assertRaisesRegex(ValueError, "set in pe5 and cannot be read in pe1"):
      source_ref(("name", "p2_fu0"), pass1_refs, 7)

  def test_staging_depths_are_isolated_per_pass(self):
    state = new_state(extended=True)
    state["stagings"] = {
      "a": {"pe": 0, "unit": 0, "depth": 2, "line": 2},
      "b": {"pe": 4, "unit": 0, "depth": 5, "line": 3},
      "c": {"pe": 6, "unit": 1, "depth": 4, "line": 4},
    }
    self.assertEqual(staging_depths(state, 0), {"STAGING_0": 2})
    self.assertEqual(staging_depths(state, 1), {"STAGING_0": 5, "STAGING_6": 4})

  def run_extended(self, body):
    text = f".kernel k extended {{\n{body}\n}}\n"
    toks, limit = body_tokens(text, find_blocks(text)[0])
    return run_statements(parse_body(Parser(text, toks, limit, True)), extended=True)

  def test_passes_isolate_pe_hardware_state_and_agu_sharing(self):
    _, state = self.run_extended(
      "  Agu a = { count: 4 };\n"
      "  Staging s;\n"
      "  .pe0 { .top = a; s = top0; .write = { count: 4, cyc: auto }; .spad = s; }\n"
      "  .pe5 { .top = a; .spad = top5 + s; }\n"
    )
    self.assertEqual(state["passes"][0]["agu_specs"][(0, "top")][:2], (("params", [("count", ("num", 4))]), 4))
    self.assertEqual(state["passes"][1]["agu_specs"][(1, "top")][:2], (("params", [("count", ("num", 4))]), 4))
    self.assertIn(0, state["passes"][0]["outputs"])
    self.assertNotIn(1, state["passes"][0]["outputs"])
    self.assertIn(1, state["passes"][1]["outputs"])
    self.assertTrue(any(line.startswith("vme_pe1(agu_top(") for line in state["passes"][1]["lines"]))
    self.assertFalse(any("vme_pe5" in line for line in state["passes"][1]["lines"]))
    self.assertEqual(state["stagings"]["s"]["pe"], 0)
    self.assertTrue(state["stagings"]["s"]["exported"])
    with self.assertRaisesRegex(ValueError, "pe5 has two outputs on the same write"):
      self.run_extended("  .pe5 { .top = { count: 2 }; .spad = top5; .spad = top5; }")

  def test_leading_regs_and_icn_follow_target_pass_lookahead(self):
    _, state = self.run_extended(
      "  .regs { .icn { .swen = 0b0101; } }\n"
      "  icn xpcr = 1;\n"
      "  for i in 4..4 {\n"
      "    pe[i] { .top = { count: 2 }; .spad = top4; }\n"
      "  }\n"
    )
    self.assertTrue(state["passes"][1]["swen_raw"])
    self.assertEqual(state["passes"][1]["secondary"], {1, 3})
    self.assertIn("xpcr", state["passes"][1]["icn"])
    self.assertFalse(state["passes"][0]["swen_raw"])
    self.assertEqual(state["passes"][0]["icn"], set())

  def test_resolve_idle_routing_gates_inactive_halves_and_honors_bank_halves(self):
    _, state = self.run_extended(
      "  Agu w = { count: 4, cyc: 4 };\n"
      "  .pe0 { .top = { count: 4 }; .write = w; .spad = top0; }\n"
      "  .pe4 { .top = { count: 4 }; .base = { count: 4 }; .write = w; .spad = top4 + base0; }\n"
      "  .pe5 { .write = w; .spad = base5; }\n"
    )
    icn = lambda p: {s: sum(n << 4 * i for i, n in enumerate(v)) for s, v in p["routing"].items()}
    resolve_idle_routing(state["passes"][0])
    self.assertEqual(icn(state["passes"][0]), {"top": 0x55545550, "base": 0x44444444, "write": 0x55545550})
    resolve_extended_offsets(state["passes"][1])
    resolve_write_routing(state["passes"][1])
    resolve_idle_routing(state["passes"][1])
    self.assertEqual(icn(state["passes"][1]), {"top": 0x55505554, "base": 0x55545550, "write": 0x55005544})

  def test_resolve_extended_offsets_adds_0x400_and_infers_low_half_reads(self):
    _, state = self.run_extended(
      "  .pe4 { .top = { count: 4, offset: 8 }; .base = { count: 4 }; .write = { count: 4, offset: OFF, cyc: auto }; .spad = top4 + base0; }\n",
    )
    p2 = state["passes"][1]
    resolve_extended_offsets(p2)
    self.assertIn("vme_pe0(agu_top(MODE), VME_DEF_MODE, 0x408);", p2["lines"])
    self.assertIn("vme_pe0(agu_base(MODE), VME_DEF_MODE);", p2["lines"])
    self.assertIn("vme_pe0(agu_write(MODE), VME_DEF_MODE, (0x400 + OFF) & 0xffff, vme_cyc(@auto@));", p2["lines"])
    self.assertEqual(p2["bank_halves"], {("base", 0): (0,)})
    _, mixed = self.run_extended("  .pe4 { .top = { count: 4 }; .spad = top0 + top4; }\n")
    with self.assertRaisesRegex(ValueError, "pe4.top cannot read both top0 and top4"):
      resolve_extended_offsets(mixed["passes"][1])

  def test_input_agu_count_picks_max_numeric_and_chains_stagings(self):
    _, state = self.run_extended(
      "  Agu a = { count: 9 };\n"
      "  Staging x, y, z;\n"
      "  .pe1 { .top = a; x = top1; }\n"
      "  .pe0 { .top = { count: 4 }; y = top0 + x; }\n"
      "  .pe2 { .top = { count: 3 }; .base = { count: 7 }; z = sat(top2 + base2, 8); }\n"
    )
    vy, vz = state["stagings"]["y"], state["stagings"]["z"]
    self.assertEqual(input_agu_count(state["passes"][0], vy["pe"] & 3, vy["unit"], "y", vy["line"]), ("num", 9))
    self.assertEqual(input_agu_count(state["passes"][0], vz["pe"] & 3, vz["unit"], "z", vz["line"]), ("num", 7))

  def test_input_agu_count_handles_symbolic_and_missing_agus(self):
    _, same = self.run_extended(
      "  Agu t = { count: N };\n"
      "  Staging s;\n"
      "  .pe0 { .top = t; .base = { count: N }; s = top0 + base0; }\n"
    )
    vs = same["stagings"]["s"]
    self.assertEqual(input_agu_count(same["passes"][0], vs["pe"] & 3, vs["unit"], "s", vs["line"]), ("name", "N"))
    _, mixed = self.run_extended("  Staging s;\n  .pe0 { .top = { count: N }; .base = { count: 4 }; s = top0 + base0; }\n")
    vm = mixed["stagings"]["s"]
    with self.assertRaisesRegex(ValueError, "combines non-constant counts"):
      input_agu_count(mixed["passes"][0], vm["pe"] & 3, vm["unit"], "s", vm["line"])
    _, empty = self.run_extended("  Staging s;\n  .pe0 { s = top1; }\n")
    ve = empty["stagings"]["s"]
    with self.assertRaisesRegex(ValueError, "has no input AGU"):
      input_agu_count(empty["passes"][0], ve["pe"] & 3, ve["unit"], "s", ve["line"])

