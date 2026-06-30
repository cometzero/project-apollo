# Doorbell channel error recovery procedure

Source: <https://developer.arm.com/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/Doorbell-channels/Doorbell-channel-error-recovery-procedure>

### Doorbell channel error recovery procedure

If an uncorrectable doorbell channel error occurs, then the data being transferred in this channel is lost together with the channel configuration information.

The following error record registers contain status information on uncorrectable doorbell channel errors:

- SRAS\_ERR1STATUS - Sender view errors in MHU Receiver for all channel types.
- RRAS\_ERR3STATUS - Receiver doorbell channel errors.

Any uncorrectable doorbell channel error reported in the MHU Receiver results in the same error being subsequently reported in the MHU Sender. For more information, see [Reliability, Accessibility, and Serviceability](/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability?lang=en "MHU-320AE uses a range of configurable RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and scrub, software and bus error reporting.").

For all uncorrectable doorbell channel errors, the channel transfer data and any corrupted configuration information are set back to their respective reset values, after which the channel is ready to use without performing any additional recovery steps. Software must only ensure that the channel configuration is reprogrammed as necessary and that the MHU Sender and MHU Receiver have been aligned with what data is expected to be sent next.

### Related information

- [SRAS\_ERR<n>STATUS](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-STATUS--Error-Record--n--Status-Register--n---0---3?lang=en "Contains status information for error record <n>.")
- [RRAS\_ERR<n>STATUS](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-STATUS--Error-Record--n--Status-Register--n---0---9?lang=en "Contains status information for error record <n>.")
