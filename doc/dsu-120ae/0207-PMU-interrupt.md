# PMU interrupt

Source: <https://developer.arm.com/documentation/107721/0001/Performance-Monitors-Extension-support-/PMU-interrupt>

### PMU interrupt

The DSU-120AE asserts the nCLUSTERPMUIRQ signal when the PMU generates an interrupt.

You can route this signal to an external interrupt controller for prioritization and masking. This is the only mechanism that signals this interrupt to a core. When the interrupt is generated, a trigger is also sent to the cluster Cross Trigger Interface (CTI).
