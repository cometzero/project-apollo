# APB4 PDEBUG

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface/APB4-PDEBUG>

### APB4 PDEBUG

The APB4 interface has a sideband signal that allows a debugger to access the DMAC without causing side-effects when sweeping the memory range in Non-secure mode. When the debugger creates the APB4 access this signal can be set HIGH, which disables the security violation error and interrupt generation while still protecting the Secure registers by responding with RAZ/WI. This signal must be stable throughout the 2 cycles of the access.
