# Utility bus accesses

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Utility-bus-accesses>

### Utility bus accesses

All the Power Policy Unit (PPU) control and data registers are accessed using the memory-mapped utility bus. The utility bus is implemented as a 64-bit AMBA AXI5 subordinate port.

Accesses to PPU registers over the utility bus must be 32-bits long. Any other sized access gets a SLVERR response from the bus.

There is no access to these registers directly from the cores. Instead, you must provide a memory mapped address for the cores to access the utility bus through the interconnect. The registers for the cluster PPU and each of the core PPUs are grouped on separate 64KB page boundaries allowing access control to be enforced by a Memory Management Unit (MMU).

You can only access PPUs by Secure access on the utility bus. Accesses to these registers with the Non-secure bit set are treated as RAZ/WI.
