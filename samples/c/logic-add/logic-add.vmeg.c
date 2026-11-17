volatile Buffer inA[1] = { 3 };
volatile Buffer inB[1] = { 10 };
volatile Buffer outSum[1] = { 0 };

@emulate "logic-add"
.kernel logicAdd pipeline {
  Transfer ta = { memory: inA, count: 0 };
  Transfer tb = { memory: inB, count: 0 };
  Transfer dst = { memory: outSum, count: 0 };

  .load { .transfer = ta; .scope = global; .offsets { .top0 = 0; } }
  .load { .transfer = tb; .scope = global; .offsets { .top1 = 0; } }

  .flow {
    .count = 0;
    Slot carry[4];

    .slot = top0 ^ top1;
    carry[0] = (top0 & top1) << 1;

    for i in 0..2 {
      carry[i + 1] = (slot & carry[i]) << 1;
      .slot = slot ^ carry[i];
    }

    .slot = slot ^ carry[3];
  }

  .store { .transfer = dst; .scope = global; }
}
