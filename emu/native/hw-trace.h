#ifndef EMU_HW_TRACE_H
#define EMU_HW_TRACE_H

#define HW_REGISTERS_H

#include <cstdint>
#include <cstdio>
#include <map>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;

inline FILE*& hwTraceFile() {
  static FILE* file = stdout;
  return file;
}

inline std::map<u32, u32>& hwTraceLast() {
  static std::map<u32, u32> last;
  return last;
}

inline void hwTraceOpen(const char* path) {
  hwTraceFile() = fopen(path, "w");
}

inline void hwTraceClose() {
  if (hwTraceFile() != stdout) {
    fclose(hwTraceFile());
    hwTraceFile() = stdout;
  }
}

inline void hwTraceMemory(u32 address, const u32* words, int count) {
  fprintf(hwTraceFile(), "M 0x%x", address);
  for (int i = 0; i < count; i++) {
    fprintf(hwTraceFile(), " 0x%x", words[i]);
  }
  fprintf(hwTraceFile(), "\n");
}

struct HwRef {
  u32 address;

  bool isRegister() const {
    return address >= 0x44000000 && address < 0x44100000;
  }

  operator u32() const {
    if (!isRegister()) {
      return *(volatile u32*)(uintptr_t)address;
    }
    std::map<u32, u32>::const_iterator found = hwTraceLast().find(address);
    return found == hwTraceLast().end() ? 0 : found->second;
  }

  HwRef& operator=(u32 value) {
    if (!isRegister()) {
      *(volatile u32*)(uintptr_t)address = value;
      return *this;
    }
    fprintf(hwTraceFile(), "W 0x%x 0x%x\n", address, value);
    hwTraceLast()[address] = value;
    return *this;
  }

  HwRef& operator=(const HwRef& other) {
    return *this = (u32)other;
  }

  HwRef& operator|=(u32 value) {
    return *this = (u32)*this | value;
  }

  HwRef& operator&=(u32 value) {
    return *this = (u32)*this & value;
  }
};

#define hw(addr) (HwRef{(u32)(addr)})

#endif
