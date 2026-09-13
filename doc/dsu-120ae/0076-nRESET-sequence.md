# nRESET sequence

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Power-policy-unit-operation/nRESET-sequence>

### nRESET sequence

Asserting nRESET causes all the cluster and core logic to be Cold reset, using the Power Policy Units (PPUs). Each PPU has its own set of reset output and input signals, which are internal to the cluster, and connect to the core and cluster logic. Each PPU is responsible for resetting its associated core or cluster logic during nRESET.

The following sequence of events occurs when nRESET is asserted:

1. nRESET is asserted, placing the PPUs under reset. The PPU internal reset outputs are LOW, so the cluster and cores are also reset.
2. nRESET is deasserted:
   - The PPUs are now active and can start logical operation.
   - The cluster and cores are held in reset by the PPUs:
     - If a power domain is required to be in MEM\_RET, the PPU does the Power Control State Machine (PCSM) handshake to enter MEM\_RET. There is no device P-Channel handshake as the logic is OFF and under reset. See figure Transitions from OFF to MEM\_RET with a P-Channel PPU in [Arm® Power Policy Unit Architecture Specification](https://developer.arm.com/documentation/den0051/latest).
     - Otherwise, the power domain is OFF and is held in reset.
3. Software programs the PPUs to enter the desired power mode. Typically this is ON.
4. The system continues.
