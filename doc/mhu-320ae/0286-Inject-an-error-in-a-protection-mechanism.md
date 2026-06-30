# Inject an error in a protection mechanism

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-recovery-procedures/Inject-an-error-in-a-protection-mechanism>

### Inject an error in a protection mechanism

To inject an error into a protection mechanism, write to the FMU\_SMERR register.

The FMU\_SMERR.BLKTYPE field specifies the MHU-320AE block type, FMU\_SMERR.BLKID field specifies the block ID, and FMU\_SMERR.SMID field specifies the protection mechanism into which to inject the error.

When a write to FMU\_SMERR completes, FMU\_STATUS.BUSY remains set to 1 until any resulting updates to FMU\_ERR<n>STATUS are complete.

This method injects only one error. The injected errors clear when the error clears in FMU\_ERR<n>STATUS.

Software can use the error injection feature to test the software error recovery handler.
