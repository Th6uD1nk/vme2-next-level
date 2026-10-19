OPERATIONS = {
  "add": {
    "syntax": "a + b",
    "code": "fu_code(OP_ADD)",
    "operands": ("front", "back"),
    "units": "any",
    "note": "a on the front socket, b on the back one",
  },
  "clamp": {
    "syntax": "clamp(x, low, high)",
    "code": "fu_code(OP_CLP)",
    "operands": ("back",),
    "units": "any",
    "note": "registers A = high and B = low, x is a buffer, a Staging variable or an operation",
  },
  "mac": {
    "syntax": "mac(a, b)",
    "code": "VME_FU_OPCODE_MAC_INNER_PRODUCT_BIAS",
    "operands": ("front", "back"),
    "units": "primary",
    "note": "running inner product (sum of a * b + bias) >> k, a on the front socket and b on the back one",
  },
  "acc": {
    "syntax": "acc(x)",
    "code": "VME_FU_OPCODE_MAC_ACC_SHIFT_BIAS",
    "operands": ("back",),
    "units": "primary",
    "note": "running sum, x is a buffer or a Staging variable",
  },
}

FIELDS = (
  ("sat(op, bits)", "fu_sat(bits)", "the saturator of the FU of the operation it wraps, bits 0 to 31"),
  ("op >> n", "k = n", "the shift in the 6 low bits of the FU register, n 0 to 63, the last layer of an operation"),
  ("op << n", "k = 64 - n", "the rotary shift, n 0 to 63"),
)
