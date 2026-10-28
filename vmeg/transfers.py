from vmeg.expr import value as full_value


def transfer_number(name, what, value, env):
  folded = full_value(value, env)
  if folded[0] == "num" and folded[1] < 0:
    raise ValueError(f"Transfer {name}: {what} cannot be negative")
  return folded[1]


class TransferKind:
  fields = ()
  required = ()
  numbers = ()
  nested = {}

  def check(self, name, params, env):
    values = {"kind": self}
    for key, value in params[1]:
      if key not in self.fields:
        raise ValueError(f"Transfer {name}: unknown field '{key}' ({', '.join(self.fields)})")
      if key in values:
        raise ValueError(f"Transfer {name}: duplicate field '{key}'")
      if key in self.nested:
        values[key] = self.check_nested(name, key, value, env)
      elif value[0] == "params":
        raise ValueError(f"Transfer {name}: '{key}' takes a value, not a list of fields")
      elif key in self.numbers:
        values[key] = transfer_number(name, key, value, env)
      elif value[0] != "name":
        raise ValueError(f"Transfer {name}: '{key}' takes a name")
      else:
        values[key] = value[1]
    for key in self.required:
      if key not in values:
        raise ValueError(f"Transfer {name}: the field '{key}' is needed")
    return values

  def check_nested(self, name, key, value, env):
    if value[0] != "params":
      raise ValueError(f"Transfer {name}: '{key}' takes a list of fields")
    names = [field for register in self.nested[key] for field in register]
    inner = {}
    for field, item in value[1]:
      if field not in names:
        raise ValueError(f"Transfer {name}: unknown field '{field}' of {key} ({', '.join(names)})")
      if field in inner:
        raise ValueError(f"Transfer {name}: duplicate field '{field}' of {key}")
      if item[0] == "params":
        raise ValueError(f"Transfer {name}: '{field}' of {key} takes a value, not a list of fields")
      inner[field] = transfer_number(name, f"{key}.{field}", item, env)
    if not inner:
      raise ValueError(f"Transfer {name}: {key} needs at least one field ({', '.join(names)})")
    for register in self.nested[key]:
      missing = [field for field in register if field not in inner]
      if 0 < len(missing) < len(register):
        raise ValueError(f"Transfer {name}: the field '{missing[0]}' of {key} is needed, {' and '.join(register)} are one register")
    return inner
