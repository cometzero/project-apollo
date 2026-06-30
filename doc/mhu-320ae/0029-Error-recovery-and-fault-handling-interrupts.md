# Error recovery and fault handling interrupts

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-recovery-and-fault-handling-interrupts>

### Error recovery and fault handling interrupts

You can assign a recorded correctable or uncorrectable error to the fault handling interrupt (fault\_int signal) by setting the associated ERR<n>CTLR.FI register field. For more information, see either [SRAS\_ERR<n>CTLR](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---3?lang=en "The error control register contains enable bits for the node that writes to this record.") or [RRAS\_ERR<n>CTLR](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---9?lang=en "The error control register contains enable bits for the node that writes to this record.").

All correctable ECC errors have error counters, where by default the interrupt would only be signaled when the counter in the associated ERR<n>MISC0 register overflows. For more information, see either [SRAS\_ERR<n>MISC0](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-MISC1--Error-Record--n--Miscellaneous-Register-1--n---0---3?lang=en "Records additional information on reported error.") or [RRAS\_ERR<n>MISC0](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-MISC0--Error-Record--n--Miscellaneous-Register-0--n---0---9?lang=en "Records information on the reported error and error counters."). This counter can be preset to any value by writing to ERR<>MISC0.Count. For example:

- To fire an interrupt on any correctable error, write 0xFF
- To fire an interrupt on every second correctable error, write 0xFE

Alternatively, the correctable error record can be configured to signal a fault handling interrupt on any recorded error by setting the associated ERR<n>CTRL.CED field.

For uncorrectable error records, fault handling interrupts are generated on every recorded error, if enabled. Uncorrectable error records can also generate an error recovery interrupt (err\_int signal), by setting the associated ERR<n>CTLR.UI field. The interrupt fires on every uncorrectable interrupt occurrence, irrespective of the counter value.
