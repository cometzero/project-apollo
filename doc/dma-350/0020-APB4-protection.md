# APB4 protection

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface/APB4-protection>

### APB4 protection

Certain registers in the APB4 register space are protected for higher privilege and security software modules. These registers configure the overall behavior of the DMAC and are protected internally within the DMAC by checking the privilege and security attribute of the access.

### Privilege protection

The DMAC checks pprot[0] bit when accessing registers with higher privilege rights. The DMAC returns with RAZ/WI when the access is denied.

### Security protection

The DMAC supports the Security Extension by checking pprot[1] when accessing registers with higher security rights. When accesses are violating security the DMAC returns RAZ/WI or error response depending on the SW configurable register and it might also generate an interrupt if enabled.
