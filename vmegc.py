import sys


def main(argv):
  with open(argv[1], encoding="utf-8", newline="") as f:
    text = f.read()
  with open(argv[2], "w", encoding="utf-8", newline="") as f:
    f.write(text)
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv))
