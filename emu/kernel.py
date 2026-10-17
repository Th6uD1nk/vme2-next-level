from vmeg.blocks import find_blocks, kernel_name
from vmeg.parser import kernel_statements


def load_kernel(text, name=None):
  blocks = find_blocks(text)
  kernels = {kernel_name(text, block): block for block in blocks if block[0] == "kernel"}
  if name is None:
    if len(kernels) != 1:
      known = ", ".join(kernels) if kernels else "there is no kernel in this file"
      raise ValueError(f"give the name of the kernel ({known})")
    name = next(iter(kernels))
  if name not in kernels:
    known = ", ".join(kernels) if kernels else "there is no kernel in this file"
    raise ValueError(f"unknown kernel '{name}' ({known})")
  return kernel_statements(text, kernels[name], {})
