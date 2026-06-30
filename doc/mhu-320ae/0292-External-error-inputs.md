# External error inputs

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/External-error-inputs>

### External error inputs

Each MHU-320AE block has generic fault inputs that allow the SoC integrator to connect and flag external faults to the FMU.

For example, an SoC integrator might have an external safety mechanism that is physically located next to a MHU block. The SoC integrator can connect the fault signal from this external SM to the ext\_err0\_req\_\* or ext\_err1\_req\_\* input signals of the MHU block. If a fault occurs, the MHU flags and reports a fault in the same manner it does with internal faults.

A captured fault is reported in the MHU block error record with a SM\_EXT<n>\_<BLKTYPE> protection name such as SM\_EXT0\_SND or SM\_EXT1\_REC.
