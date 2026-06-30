# Error signaling from a MHU-320AE block to the FMU

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-signaling-from-a-MHU-320AE-block-to-the-FMU>

### Error signaling from a MHU-320AE block to the FMU

MHU-320AE implements several protection mechanisms in each MHU block to protect against random transient or permanent errors. Each protection mechanism sends an error signal to the fault collator in its MHU block. The MHU block then forwards the error signal to the FMU using the existing AXI5-Stream interface.

In addition to reporting errors through the AXI5-Stream interconnect, each remote MHU block has a cr\_err\_out and ncr\_err\_out output signal that indicates either a critical or non-critical error within its block.

As the MHU exits reset, it sets all protection mechanisms to report a critical error, except for the RAM SEC protection mechanisms that report a non-critical error. Software can use FMU\_SMCR register details to alter these criticality assignments.

Connect the \*\_err\_out and \*\_ncr\_err\_out signals from the MHU component that does not contain the FMU to the corresponding signals in the MHU component that contains the FMU.
