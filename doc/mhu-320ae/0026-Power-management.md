# Power management

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Power-management>

### Power management

Each domain present in a MHU-320AE configuration exposes a power Q-Channel interface that allows the system power controller to power down the corresponding domain.

This interface also controls the entry of the MHU into the non-operational architectural state. In configurations where the MHU Sender and MHU Receiver are in separate domains, both domains act independently in terms of power control.

For the MHU domain to accept entry into the non-operational state, all of the following statements must be true:

- No outstanding messages are being sent between the MHU Sender and MHU Receiver.
- No programming accesses are being performed to respective domain.
- All doorbell and FIFO channels present in configuration are idle.
- All fast channels present in configuration are idle, if the domain contains an MHU Receiver.
- FIFO flush operations are not outstanding.

Software can also prevent the MHU Sender or MHU Receiver from entering the non-operational state by setting the PBX\_CTRL.OP\_REQ or MBX\_CTRL.OP\_REQ register fields respectively.

For the purposes of entering the non-operational state, a channel is considered non-idle if it has unread or unacknowledged data stored in it. When entering a non-operational state software can disregard non-idle channels by setting the PBX\_CTRL.CH\_OP\_MSK or MBX\_CTRL.CH\_OP\_MSK register fields for the domain that is being powered down.

To ensure that MHU-320AE is isolated from the system, MHU-320AE must enter the non-operational state before reset is asserted.

In configurations where `FUSA_PRESENT == 1`, if the power Q-channel fails to respond due to a hardware fault, a full system reset may be necessary.

For more detailed information about the non-operational state and power control, see the [Message Handling Unit Architecture version 3.0](https://developer.arm.com/documentation/aes0072/aa).

### Related information

- [PBX\_CTRL](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CTRL--Postbox-Control-Register?lang=en "This register contains control bits for the postbox")
- [MBX\_CTRL](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-CTRL--Mailbox-Control-Register?lang=en "This register contains control bits for the mailbox")
