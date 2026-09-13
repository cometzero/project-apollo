# Fault detection and reporting

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Fault-detection-and-reporting>

### Fault detection and reporting

When the DynamIQ Shared Unit-120AE (DSU-120AE) detects a fault, it raises a Fault Handling Interrupt (FHI) exception through the fault signals. FHIs are reflected in the Error Data Record Registers that are updated in the node that detects the errors.

### Fault handling interrupt

When ERR0CTLR.FI is set, all Deferred errors and Uncorrected errors that the DSU-120AE detects generate an FHI through the nCLUSTERFAULTIRQ signal.

When ERR0CTLR.CFI or any other CE-counter overflow bits are set, then all detected Corrected errors also cause an FHI to be generated.

### Error recovery interrupt

When ERR0CTLR.UI is set, all Uncorrected errors that are detected and not deferred generate an error recovery interrupt through the nCLUSTERERRIRQ signal.

### Critical error interrupt

When ERR0CTLR.CI is set, all critical errors that the DSU-120AE detects generate a critical error interrupt on the nCLUSTERCRITIRQ signal.

### Clearing reported faults

The signals nCLUSTERFAULTIRQ, nCLUSTERERRIRQ, and nCLUSTERCRITIRQ remain asserted until software clears them by writing to the ERR0STATUS register.
