# Discover the active errors on the block

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-recovery-procedures/Discover-the-active-errors-on-the-block>

### Discover the active errors on the block

To discover if a block has some active errors, software can write to an FMU register, to request that the block resends any errors that have not been cleared.

To request that the block resends any active errors that have not been cleared, software can write SMID=255 to any of the following registers:

- FMU\_SMEN
- FMU\_SMERR
- FMU\_SMCR
- FMU\_SMWR

When the selected block receives the message, then it resends any errors that have not been cleared.
