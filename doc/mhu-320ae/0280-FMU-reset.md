# FMU reset

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/FMU-reset>

### FMU reset

When the FMU reports multiple uncorrectable errors, the error recovery procedure might require the MHU to be reset. To facilitate this situation, the FMU has a separate reset input signal, fmu\_reset\_n.

This reset differs from the MHU functional reset, reset\_n signal. It allows the FMU to retain error records across MHU functional reset.

The FMU is reset together with the block where it is placed.

When the FMU and its respective block are powered down, the system software must not allow outstanding APB5 accesses to reach the FMU.
