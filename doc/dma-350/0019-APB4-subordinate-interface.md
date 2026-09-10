# APB4 subordinate interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface>

### APB4 subordinate interface

The APB4 subordinate interface is for accessing the internal configuration registers of the DMA-350.

The DMA-350 supports the AMBA APB4 Protocol Specification. For more information, see the [AMBA® APB Protocol Specification](https://developer.arm.com/documentation/ihi0024/) document.

### Register access

Only 32-bit wide accesses are supported. When an APB4 Write-Access uses pstrb other than 4’b1 it results in an error response. Unaligned accesses are treated as normal accesses by having paddr[1:0] tied to 0 internally.

- **[APB4 protection](/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface/APB4-protection?lang=en)**
   Certain registers in the APB4 register space are protected for higher privilege and security software modules. These registers configure the overall behavior of the DMAC and are protected internally within the DMAC by checking the privilege and security attribute of the access.
- **[APB4 PWAKEUP](/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface/APB4-PWAKEUP?lang=en)**
   The APB4 interface is extended with a clock wakeup signaling through the pwakeup port. This allows faster clock request mechanism when the pwakeup is generated from a registered source.
- **[APB4 PDEBUG](/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface/APB4-PDEBUG?lang=en)**
   The APB4 interface has a sideband signal that allows a debugger to access the DMAC without causing side-effects when sweeping the memory range in Non-secure mode. When the debugger creates the APB4 access this signal can be set HIGH, which disables the security violation error and interrupt generation while still protecting the Secure registers by responding with RAZ/WI. This signal must be stable throughout the 2 cycles of the access.
