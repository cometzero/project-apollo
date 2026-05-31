<a id="1-zena-css-product-highlights"></a>
# 1. Zena CSS product highlights

<!-- Source PDF page: 6 -->

Arm® Zena™ Compute Subsystem (Zena CSS) supports the design of System-on-Chip (SoC) and
chiplet solutions for automotive applications, such as Advanced Driver-Assistance Systems (ADAS)
and digital cockpit domain controllers.

Zena CSS has the following highlights.

**Table 1-1: Zena CSS product highlights**

Processor Blocks                                                     Mesh interconnect
•   16 Arm® Cortex®-A720AE CPU cores across 4 Processor              •   Arm® Neoverse® CMN S3(AE) Coherent Mesh Network
Blocks
•   Mesh size: 6 x 4
•   64 KB L1 instruction cache, 64 KB L1 data cache, and 512
•   4 MB System-Level Cache (SLC)
KB L2 cache for each core
•   Arm® DynamIQ™ Shared Unit-120AE cluster in each
Processor Block
•   4 MB L3 cache for each cluster

Functional Safety                                                   Security                            Interfaces
•   Features:                                                       •    Features:                      •      One PCIe Gen 6 x8 interface
◦   Arm® Cortex®-R82AE Safety Island                                 ◦     Arm® Runtime             •      Two PCIe Gen 3 x1 interfaces
Security Engine (RSE):
◦   Diagnostic coverage mechanisms used throughout the                                              •      Two CMN Coherent Gateway
an isolated execution
Zena CSS functional blocks                                                                             (CCG) interfaces
environment for
•   Standards:                                                                 security-sensitive       •      AMBA® ATB and AMBA® APB
◦   ISO 26262                                                              processes and data              Debug chain interfaces

▪       Targeting ASIL D systematic and ASIL B diagnostic •      Standards:                     •      AMBA® 5 AXI manager and
requirements                                                                                   subordinate interfaces (RSE and
◦     Zena CSS is targeting
CSS)
▪       Safety Island targeting ASIL D systematic and                  ISO/SAE 21434
diagnostic requirements                                        certification             •      AMBA® ACE-Lite manager and
subordinate interfaces
◦   IEC 61508
•      DMC interfaces (AMBA® 5 ACE-
▪       Targeting SIL 3 systematic and SIL 2 diagnostic                                                Lite, AMBA® 5 AXI)
requirements
▪       Safety Island targeting SIL 3 systematic and
diagnostic requirements
