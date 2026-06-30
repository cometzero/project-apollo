# RAM scrub

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/RAMs-and-ECC/RAM-scrub>

### RAM scrub

MHU-320AE can hold channel specific programming and transfer information in RAMs, which is protected by Single Error Correction and Double Error Detection (SECDED).

However, some RAM contents might be static for a long duration, and there is a potential for errors to accumulate if a particular address is not periodically accessed. To prevent this occurring, software can periodically trigger a low-priority scrub of a RAM, by setting the PBX\_FCTRL.SIP and MBX\_FCTRL.SIP register bits in the MHU Sender and MHU Receiver respectively. This process triggers a check and if necessary, a write-back of all valid RAM entries. Any errors that are found during a scrub are also reported in the relevant RAS error records.

### Related information

- [PBX\_FCTRL](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FCTRL--Postbox-Feature-Control-Register?lang=en "Controls non-architectural postbox functionality")
- [MBX\_FCTRL](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCTRL--Mailbox-Feature-Control-Register?lang=en "Controls non-architectural mailbox functionality")
