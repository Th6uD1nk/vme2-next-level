extern "C" {
void meCoreBusClockEnableDMACPrimMux(void);
void meCoreBusClockDisableDMACPrimMux(void);
void meCoreBusClockEnableVMECtrl(void);
void meCoreBusClockDisableVMECtrl(void);
void meCoreDMACPrimMemoryToRingBuffer(void* src, u32 offset, u32 count);
void meCoreDMACPrimRingBufferToMemory(void* dst, u32 offset, u32 count);
void meCoreDMACPrimWaitTransferFinish(void);
void meCoreDMACPrimWaitVMEFinish(void);
void meCoreDMACPrimMuxSetCtrl_0x018(void);
void meCoreMemset(void* dst, int value, u32 size);
int meCoreDcacheWritebackRange(void* address, u32 size);
}
