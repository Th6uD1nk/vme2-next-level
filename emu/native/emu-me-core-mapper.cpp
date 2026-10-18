#include "hw-trace.h"
#include <map>
#include <string.h>

static u32 virtualAddress(const void* pointer, u32 count) {
  static std::map<const void*, u32> known;
  static u32 next = 0x08800000;
  std::map<const void*, u32>::iterator found = known.find(pointer);
  if (found != known.end()) {
    return found->second;
  }
  u32 address = next;
  next += (count * 4 + 63) & ~63u;
  known[pointer] = address;
  return address;
}

static void transfer(u32 address, u32 offset, u32 count, u32 control) {
  hw(0x440ff010) = (address & 0x1fffffff) | 0x40000000;
  hw(0x440ff014) = count - 1;
  hw(0x440ff018) = offset;
  hw(0x440ff008) = control;
}

extern "C" {
void meCoreDMACPrimMemoryToRingBuffer(void* src, u32 offset, u32 count) {
  u32 address = virtualAddress(src, count);
  hwTraceMemory(address & 0x1fffffff, (const u32*)src, count);
  transfer(address, offset, count, 0x40);
}

void meCoreDMACPrimRingBufferToMemory(void* dst, u32 offset, u32 count) {
  transfer(virtualAddress(dst, count), offset, count, 0x48);
}

void meCoreBusClockEnableDMACPrimMux(void) {}
void meCoreBusClockDisableDMACPrimMux(void) {}
void meCoreBusClockEnableVMECtrl(void) {}
void meCoreBusClockDisableVMECtrl(void) {}

int meCoreDcacheWritebackRange(void* address, u32 size) {
  return 0;
}

void meCoreDMACPrimWaitTransferFinish(void) {
  hw(0x440ff000) = (0x200 >> 8) | 0x80;
}

void meCoreDMACPrimWaitVMEFinish(void) {
  hw(0x440ff000) = (0x800 >> 8) | 0x80;
}

void meCoreDMACPrimMuxSetCtrl_0x018(void) {
  hw(0x440ff008) = 0x18;
}

void meCoreMemset(void* dst, int value, u32 size) {
  u32 address = (u32)(uintptr_t)dst;
  if (address >= 0x440f8000 && address < 0x44100000) {
    for (u32 i = 0; i < size; i += 4) {
      hw(address + i) = (u32)value;
    }
    return;
  }
  memset(dst, value, size);
}
}
