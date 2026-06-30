# Enable or disable both error signals on a block

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-recovery-procedures/Enable-or-disable-both-error-signals-on-a-block>

### Enable or disable both error signals on a block

Each block has a critical error signal output and a non-critical error signal output. Software can enable or disable both output signals on a block.

At reset, the MHU-320AE, enables the error wire outputs for the MHU Sender, MHU Receiver, and the FMU blocks.

To enable or disable the block error signals, write to the following fields in the FMU\_SMEN register:

- BLKTYPE, selects the type of MHU block such as MHU Sender or MHU Receiver.
- BLKID, selects a block
- SMID, set to 255
- EN, set to:
  - 0, to disable both error signal outputs on the block.
  - 1, to enable both error signal outputs on the block.

### Block error signals status

To discover if the block error signals are enabled, software can write to the FMU\_SMRD register with the following fields:

- BLKTYPE, selects the type of MHU block such as MHU Sender or MHU Receiver.
- BLKID, selects a block
- SMID, set to 255
- PAGEID, set to 0

The MHU returns the enable status of these signals when software reads FMU\_SMRDATA.enable:

- 0 - Both error wire outputs for that block are not enabled.
- 1 - Both error wire outputs for that block are enabled.
