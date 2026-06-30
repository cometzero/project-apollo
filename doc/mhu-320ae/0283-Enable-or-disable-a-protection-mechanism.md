# Enable or disable a protection mechanism

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-recovery-procedures/Enable-or-disable-a-protection-mechanism>

### Enable or disable a protection mechanism

All protection mechanisms are enabled on reset.

To enable or disable a protection mechanism, write to the following fields in the FMU\_SMEN register:

- BLKTYPE, selects the MHU block type
- BLKID, selects the MHU block
- SMID, selects the specific protection mechanism in the MHU block to be enabled or disabled.

We recommend that software does not disable protection mechanisms.
