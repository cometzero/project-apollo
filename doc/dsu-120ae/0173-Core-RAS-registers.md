# Core RAS registers

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Core-RAS-registers>

### Core RAS registers

The cores support Error Correcting Code (ECC) and parity protection on their RAMs, which normally updates the core RAS registers, when a fault is detected. However, when running in Lock-Step, the core's RAMs are duplicated, therefore a fault in one set of the RAMs causes the fault to be reported in one copy of the core. If the core or complex RAS registers are read using memory mapped accesses on the utility bus, then the value read from the two cores or complexes are different, which causes a Dual-Core Lock-Step (DCLS) fault to be reported. To avoid this case, the DSU provides two address ranges for the RAS registers of each core or complex.

The two address ranges are as follows:

First address range
:   - For the core: 0x<n>A0000
    - For the complex: 0x<n>C0000

    When performing a read from the first address, it reads the data from the primary core or from the primary complex. It does not report a fault if the redundant register content does not match.

    Writing to the first address range updates the registers in both the primary and redundant core or complexes.

Second address range
:   - For the core: 0x<n>F0000
    - For the complex: 0x<n>E0000

    When performing a read from the second address, it reads the data from the redundant core or from the redundant complex. It does not report a fault, if the primary register content does not match.

    Writing to the second address range is ignored.

> ### Note
>
> Note that, there is a single set of fault reporting interrupt pin from the cores, which indicates if the primary or redundant core reported a fault in the RAS registers. Therefore, software responding to these interrupt pins must read from both the primary and redundant address ranges to determine the true location of the reported fault.
