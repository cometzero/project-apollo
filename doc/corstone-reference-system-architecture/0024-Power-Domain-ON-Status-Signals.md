# Power Domain ON Status Signals

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Power-Domain-ON-Status-Signals>

### Power Domain ON Status Signals

CRSAS Ma1 provides a set of output signals that indicates if the power domain each is associated with is in the ON Power Mode.

These signals are:

PDMGMTON
:   - HIGH indicates that the PPU of the PD\_MGMT power domain presumes that the domain is ON
    - LOW indicates that the PPU presumes that the power domain is in a lower power state
    - This signal must exist when PILEVEL = 2.

PDSYSON
:   - HIGH indicates that the PPU of the PD\_SYS power domain presumes that the domain is ON
    - LOW indicates that the PPU of the power domain presumes that the domain is in a lower power state.

PDCPU<n>ON
:   - HIGH indicates that the PPU of the PD\_CPU<n> power domain presumes that the domain is ON
    - LOW indicates that the PPU of the power domain presumes that the domain is in a lower power state
    - This signal must exist when PILEVEL > 0.

PDNPU<m>ON
:   - HIGH indicates that the PPU of the PD\_NPU<m> power domain presumes that the domain is ON
    - LOW indicates that the PPU of the power domain presumes that the domain is in a lower power state
    - This signal only exists if NUMNPU > 0.

PDDEBUGON
:   - HIGH indicates that the PPU of the PD\_DEBUG power domain presumes that the domain is ON
    - LOW indicates that the PPU of the power domain presumes that the domain is in a lower power state

PDCRYPTOON
:   - HIGH indicates that the PPU of the PD\_CRYPTO power domain presumes that the domain is ON
    - LOW indicates that the PPU of the power domain presumes that the domain is in a lower power state
    - This signal must exist when PILEVEL = 2 and HASCRYPTO = 1.

> ### Note
>
> These are primarily status signals and are typically driven using PPUHWSTAT signals. We recommend that these are not used as power control signals directly.
