# Software interaction

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Software-interaction>

### Software interaction

Software interacts with the FMU during initialization, when handling interrupts, preventing backpressure, and managing power.

### Initialization

The initialization routine can iterate over the FMU\_ERR<n>FR registers to discover the capabilities of each error record.

> ### Note
>
> All protection mechanisms are enabled on reset, which might lead to errors being logged in the error records. If the system does not support or want to check a particular safety feature, then the software can disable that protection mechanism.

To disable a protection mechanism, write the corresponding block type, block ID, and protection mechanism ID to the FMU\_SMEN register.

To analyze the logged errors, read the FMU\_ERR<n>STATUS register.

To clear all logged errors, read the FMU\_ERR<n>STATUS and write back the V, UE, and OF bits with the same value that is read.

To enable error reporting through either the ERI or CRI, write to FMU\_ERR<n>CTLR.UI or FMU\_ERR<n>CTLR.CI, respectively.

### Interrupt handler

When an interrupt is received, the interrupt handling software identifies the error record ID by reading the FMU\_ERRGSR register. The asserted bit[n] indicates that error record n is in error. For more information about the error, read the FMU\_ERR<n>STATUS register.

FMU\_ERR<n>STATUS.BLKID indicates the BLKID that reported an error, and BLKTYPE indicates the block type. FMU\_ERR<n>STATUS.IERR indicates which protection mechanism reported the error.

If more than one error of the same criticality has been reported by this block type to this error record, then FMU\_ERR<n>STATUS.OF is set to 1. If there is overflow, the error record retains the protection mechanism ID of the first error.

When the recovery procedure is complete, the error from this error record can be cleared by reading FMU\_ERR<n>STATUS and writing back the V and OF bits with the same value that is read. The software then polls for FMU\_STATUS.busy==0.

### FMU busy

The APB5 port to the FMU is designed not to introduce backpressure by deasserting the pready signal. This design feature prevents software lockup and always keeps the error records accessible.

There are several operations which take multiple clock cycles to complete within the FMU. The FMU frees up the APB5 bus by asserting the pready signal to complete the APB transaction. However, it might still be processing the previous request.

When software writes to one of the following FMU registers, it must poll the register field FMU\_STATUS.BUSY==0, before it issues another write to these registers:

- FMU\_ERR<n>STATUS
- FMU\_SMEN
- FMU\_SMERR
- FMU\_SMCR
- FMU\_SMWR
- FMU\_SMRD
- FMU\_ERRUPDATE

### Power management

Software can power down either the MHU Sender or MHU Receiver by using the procedure described in [Power management](/documentation/107612/0001/Operations-of-MHU-320AE/Power-management?lang=en "Each domain present in a MHU-320AE configuration exposes a power Q-Channel interface that allows the system power controller to power down the corresponding domain."). However, performing FMU accesses can result in messages being sent to the remote MHU block, which can affect its power down state. Writing to the following registers generates messages to the remote MHU block.

- FMU\_ERR<n>STATUS
- FMU\_SMEN
- FMU\_SMERR
- FMU\_SMCR
- FMU\_SMWR
- FMU\_SMRD
- FMU\_ERRUPDATE
