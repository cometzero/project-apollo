# EVENT Interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/CPU/EVENT-Interfaces>

### EVENT Interfaces

Each CPU has event interfaces, RXEV and TXEV. In CRSAS Ma1, all TXEVs are logically or together and used to drive all processors’ RXEV.

> ### Note
>
> In this system, events do not wake a processor from its EWIC based low power state, or wake the system from Hibernation{0/1} state.

CRSAS Ma1 does not support the use of WFE for the CPU to enter DeepSleep state.
