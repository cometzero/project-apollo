# RAM error simulation

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/RAMs-and-ECC/RAM-error-simulation>

### RAM error simulation

For each RAM present in the configuration, software can use the following registers to simulate a transient ECC single-bit or double-bit error:

- PBX\_FIFO\_ERRINS register: Sender FIFO channel RAM
- MBX\_DB\_ERRINS register: Receiver doorbell channel RAM
- MBX\_FST\_ERRINS register: Receiver fast channel RAM
- MBX\_FCFG\_ERRINS register: Receiver FIFO channel configuration RAM
- MBX\_FDATA\_ERRINS register: Receiver FIFO channel data RAM

These registers cause an error to be inserted, to a specified address and location in the associated RAM. The ECC encoder and decoder are checked but the RAM content is not modified. These registers can only be accessed by the most trusted security state present in the configuration.

After software inserts an error, MHU-320AE reports the error in the associated error record, in the same manner as any regular ECC error. However, the software injected error has no effect on the functionality of the MHU, so software can inject errors injection during operation.

If a coincident real error occurs, then the MHU reports the real error instead and triggers the normal containment mechanism for that channel type.

### Related information

- [PBX\_FIFO\_ERRINS register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FIFO-ERRINS--Postbox-FIFO-channel-RAM-ECC-Error-Insertion-Register?lang=en "Enables ECC error insertion in the Postbox FIFO channel RAM. The bit descriptions for this register depend on whether the access is a read or a write.")
- [MBX\_DB\_ERRINS register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-DB-ERRINS--Mailbox-doorbell-channel-RAM-ECC-Error-Insertion-Register?lang=en "Enables ECC error insertion in the Mailbox doorbell channel RAM. The bit descriptions for this register depend on whether the access is a write or a read.")
- [MBX\_FST\_ERRINS register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FST-ERRINS--Mailbox-fast-channel-RAM-ECC-Error-Insertion-Register?lang=en "Enables ECC error insertion in the Mailbox Fast channel RAM. The bit descriptions for this register depend on whether the access is a write or a read.")
- [MBX\_FCFG\_ERRINS register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCFG-ERRINS--Mailbox-FIFO-channel-config-RAM-ECC-Error-Insertion-Register?lang=en "Enables ECC error insertion in the Mailbox FIFO channel configuration RAM. The bit descriptions for this register depend on whether the access is a write or a read.")
- [MBX\_FDATA\_ERRINS register](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FDATA-ERRINS--Mailbox-FIFO-channel-data-RAM-ECC-Error-Insertion-Register?lang=en "Enables ECC error insertion in the Mailbox FIFO channel data RAM. The bit descriptions for this register depend on whether the access is a write or a read.")
