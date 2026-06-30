# RAMs and ECC

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/RAMs-and-ECC>

### RAMs and ECC

MHU-320AE can use multiple RAMs to store a range of channel specific information, including transfer data. In typical operation, the RAMs are transparent to software.

Each RAM is protected from errors using an ECC with Single Error Correction and Double Error Detection (SECDED).

If single or double errors are detected, they are reported in the software visible error records, see [Reliability, Accessibility, and Serviceability](/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability?lang=en "MHU-320AE uses a range of configurable RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and scrub, software and bus error reporting.") for more information.
