# FIFO channel error recovery procedure

Source: <https://developer.arm.com/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/FIFO-channels/FIFO-channel-error-recovery-procedure>

### FIFO channel error recovery procedure

If an uncorrectable FIFO channel error occurs, then the data being transferred in this channel may have been corrupted and a recovery sequence needs to be performed by software to bring the FIFO channel back to a known state.

The following error record registers contain status information on uncorrectable FIFO channel errors:

- SRAS\_ERR1STATUS register - Sender view errors in MHU Receiver for all channel types
- SRAS\_ERR3STATUS register - Sender FIFO channel errors
- RRAS\_ERR1STATUS register - Receiver view of MHU Sender FIFO channel errors
- RRAS\_ERR7STATUS register - Receiver FIFO channel configuration errors
- RRAS\_ERR9STATUS register - Receiver FIFO channel data errors

Any uncorrectable FIFO channel error reported in the MHU Receiver also results in the same error being subsequently reported in the MHU Sender.

For more information on error handling procedures, see [Reliability, Accessibility, and Serviceability](/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability?lang=en "MHU-320AE uses a range of configurable RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and scrub, software and bus error reporting.").

For uncorrectable errors, software is required to perform the following recovery sequence:

1. Read the error record to determine if an uncorrectable error has occurred and record the corrupted FIFO channel number.
2. Clear the error record to enable tracking of any future errors.
3. If an error has occurred in the MHU Receiver, the MHU Sender must wait for the corresponding error to be reported in SRAS\_ERR1STATUS.
4. Ensure the FIFO channel is empty and any remaining transfers have been popped for FIFO channel by the MHU Receiver.
5. Read PFFCW<n>\_ACK\_CNT for FIFO channel to determine the number of previously acknowledged transfers, and clear stored ACK\_CNT.
6. Reprogram the FIFO channel states, for example the interrupt enables, as required.
7. Align the MHU Sender and the MHU Receiver with what data is expected to be sent next.

### Related information

- [SRAS\_ERR<n>STATUS](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-STATUS--Error-Record--n--Status-Register--n---0---3?lang=en "Contains status information for error record <n>.")
- [RRAS\_ERR<n>STATUS](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-STATUS--Error-Record--n--Status-Register--n---0---9?lang=en "Contains status information for error record <n>.")
