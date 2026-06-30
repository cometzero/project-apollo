# Product revisions

Source: <https://developer.arm.com/documentation/102666/0201/About-the-GIC-720AE/Product-revisions>

### Product revisions

This section describes the differences in functionality between product revisions.

r0p0
:   First release.

r0p0‑r0p1
:   The functional changes are:

    - Bug fixes.

r0p1‑r1p0
:   The functional changes are:

    - Added the multi view feature. See [Multi view](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Multi-view?lang=en "The multi view feature allows software to allocate GIC resources into three or fewer different views. This feature allows control firmware to allocate the GIC to three, or fewer, different OS or hypervisors that are running independent software stacks.") for more information.
    - Added GIC Stream Protocol Validator (GSPV), which enables a GCI to connect to a processor with a safety level that is lower than ASIL-D. See [GIC Cluster Interface](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface?lang=en "The GIC Cluster Interface (GCI) is responsible for PPIs and SGIs that are associated with its related cluster or group of cores.").
    - Added CRC protection to the cross-chip ACE5-Lite interface.

r1p0‑r2p0
:   The functional changes are:

    - Added real-time interrupts. See [Low latency support](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Low-latency-support?lang=en "GIC-720AE can be integrated into systems that require interrupts to be distributed to real-time peripherals with a deterministic low latency. To support this requirement, GIC-720AE provides up to 960 real-time SPIs and up to 48 real-time PPIs.") for more information.

r2p0‑r2p1
:   The functional changes are:

    - Added a 1024-bit data width option for an ITS. See [ITS configuration](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-configuration?lang=en "You can configure several options that relate to the operation of the ITS block.").
    - Added configurable Memory Partitioning and Monitoring (MPAM) widths. See [MPAM information](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Memory-access-and-attributes/MPAM-information?lang=en "The GIC-720AE supports Memory Partitioning and Monitoring (MPAM) and it assigns PARTIDR and PMG values to all memory accesses that it issues on the ACE5-Lite manager interface.").
    - Added the error\_DetectionPaused, BISTBusy, and error\_BIST\_valid bits in [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access."), for page 2 interrupt protection. Added the clear\_error\_DetectionPaused bit in [FMU\_SMWDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Write-Data-register?lang=en "This register contains the data that is written during a page write access."), for page 2 interrupt protection.
