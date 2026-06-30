# Error record classification

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-record-classification>

### Error record classification

The MHU reports errors in Arm RASv1.1 architecture-compliant error records, separately in the MHU Sender and MHU Receiver, which are accessible through the respective subordinate programming interfaces.

- The MHU Sender error records are placed in the SRAS register block in the MHU Sender. For more information, see the [External MHUS register summary](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary?lang=en "The following summary table provides an overview of IMPLEMENTATION DEFINED memory-mapped MHU Sender RAS (SRAS) registers.").
- The MHU Receiver error records are placed in the RRAS register block in the MHU Receiver, see the [External MHUR register summary](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary?lang=en "The following summary table provides an overview of IMPLEMENTATION DEFINED memory-mapped MHU Receiver RAS (RRAS) registers.").

The classes of error records are:

- Correctable ECC errors
- Uncorrectable ECC errors
- Software access errors

> ### Note
>
> In configurations where multiple security states are present software can use SRAS\_ERRACR and RRAS\_ERRACR registers in the MHU Sender and MHU Receiver respectively to control which security states are allowed to perform accesses to MHU error records.

For more information about RASv1.1 architecture, see the RAS System Architecture chapter of the [Arm® Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487).
