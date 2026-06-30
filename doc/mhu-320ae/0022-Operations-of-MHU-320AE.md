# Operations of MHU-320AE

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE>

### Operations of MHU-320AE

The details of the MHU-320AE operation depend on the configuration used in your design.

For the details of steps involved in each transport protocol, see the following sections:

- [Doorbell channels](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/Doorbell-channels?lang=en "You can configure MHU-320AE to have up to 128 doorbell channels.")
- [Fast channels](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/Fast-channels?lang=en "You can configure the MHU-320AE to have up to 1024 fast channels.")
- [FIFO channels](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/FIFO-channels?lang=en "MHU-320AE can be configured to have up to 64 FIFO channels. Each FIFO channel can store up to 1024 bytes of transfer data.")

[RAMs and ECC](/documentation/107612/0001/Operations-of-MHU-320AE/RAMs-and-ECC?lang=en "MHU-320AE can use multiple RAMs to store a range of channel specific information, including transfer data. In typical operation, the RAMs are transparent to software.") are used to store and protect channel-specific information, including transfer data. Configurable [Reliability, Accessibility, and Serviceability](/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability?lang=en "MHU-320AE uses a range of configurable RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and scrub, software and bus error reporting.") features protect the information stored in the RAMs.

MHU-320AE uses MHU Sender and MHU Receiver Q-Channel interfaces for [Power management](/documentation/107612/0001/Operations-of-MHU-320AE/Power-management?lang=en "Each domain present in a MHU-320AE configuration exposes a power Q-Channel interface that allows the system power controller to power down the corresponding domain.").
