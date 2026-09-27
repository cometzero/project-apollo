# Cross Trigger

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration/Cross-Trigger>

### Cross Trigger

The Shared Debug System implements a Cross Trigger Matrix (CTM) and a single Cross Trigger Interface (CTI). These together allow DMA, timers, and watchdog timers in the CRSAS Ma1 subsystem to be halted and restarted using trigger sources from any of the CPU cores and also from trigger sources external to the subsystem through the Cross Trigger Channel Interface.

The first four Cross Trigger inputs and the first six outputs are reserved for internal use to support the following:

- SLOWCLK watchdog and SLOWCLK timer halting as follows:

  - CTIEVENTOUT[0] of the CTI is used internally to halt the SLOWCLK Timer and Watchdog.
  - CTIEVENTOUT[1] of the CTI is used internally to restart the SLOWCLK Timer and Watchdog.
- Triggers to and from the ETB

  - CTIEVENTOUT[2] of the CTI is used to drive TRIGIN input of the ETB to request ETB to insert a trigger in a trace stream
  - CTIEVENTOUT[3] of the CTI is used to drive FLUSHIN input of the ETB to initiate a flush.
  - CTIEVENTIN[0] of the CTI takes the event output FLUSHCOMP of the ETB to indicate that a flush operation is completed.
  - CTIEVENTIN[1] of the CTI takes the event output ACQCOMP of the ETB to indicate that trace acquisition is completed.
  - CTIEVENTIN[2] of the CTI takes the event output FULL of the ETB to indicate that either the trace memory is full or the write pointer wrapped around.
  - CTIEVENTIN[3] of the CTI is reserved and tied 0.
- If NUMDMA > 0, triggers a halt and restart the DMA, reserved if NUMDMA=0

  - CTIEVENTOUT[4] of the CTI is used internally to halt the DMA.
  - CTIEVENTOUT[5] of the CTI is used internally to restart the DMA.

All other Cross Trigger Interface inputs and outputs of the CTI Block are made available as expansion signals through CTIEVENTIN[7:4] and CTIEVENTOUT[7:6].

When integrating a CRSAS Ma1 based subsystem with HASCSS=1, we recommend that the triggers signals are used to also halt the system timestamp counter in the following way

- Use CTIEVENTOUT[6] to halt the system timestamp counter.
- Use CTIEVENTOUT[7] to restart the system timestamp counter.

> ### Note
>
> It is the responsibility of debug software to halt and restart NPUs in the system, using their programming interface.
