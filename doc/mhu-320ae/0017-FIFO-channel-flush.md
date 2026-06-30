# FIFO channel flush

Source: <https://developer.arm.com/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/FIFO-channels/FIFO-channel-flush>

### FIFO channel flush

FIFO channel flush is a mechanism that returns a FIFO channel to a clean state following an unexpected event that causes the channel state to get corrupted.

FIFO channel flush can be triggered from either the MHU Sender or MHU Receiver and clears all of the transfer data and flags associated with that channel. To perform a FIFO flush, software must perform the following steps:

1. Set the control bit to 0b1.
2. Wait for the corresponding status bit to become 0b1.
3. Set the control bit to 0b0.
4. Poll for the corresponding status bit to become 0b0.

The control and status registers involved depend on whether the FIFO channel flush is triggered from the MHU Sender or MHU Receiver:

- The MHU Sender writes to PFFCW<n>\_CTRL.FF control register and polls the PFFCW<n>\_ST.FF status register.
- The MHU Receiver writes to the MFFCW<n>\_CTRL.FF control register and polls the MFFCW<n>\_ST.FF status register.

For more information, see FIFO flush in the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072/aa).

### Related information

- [PFFCW<n>\_CTRL register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--CTRL--Postbox-FIFO-Channel-Window--n--Control-Register--n---0---63?lang=en "This register contains control bits for FIFO channels")
- [PFFCW<n>\_ST register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ST--Postbox-FIFO-Channel-Window--n--Status-Register--n---0---63?lang=en "Contains status information for FIFO channel")
- [MFFCW<n>\_CTRL register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--CTRL--Mailbox-FIFO-Channel-Window--n--Control-Register--n---0---63?lang=en "This register contains control bits for FIFO channels")
- [MFFCW<n>\_ST register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--ST--Mailbox-FIFO-Channel-Window--n--Status-Register--n---0---63?lang=en "Contains status information for FIFO channel")
