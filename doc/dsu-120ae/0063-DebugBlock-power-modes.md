# DebugBlock power modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-PPU-mode-transitions/DebugBlock-power-modes>

### DebugBlock power modes

The DebugBlock supports only two power modes, ON, and OFF. There is no Power Policy Unit (PPU) in the DynamIQ™ Shared Unit-120AE for the DebugBlock. Instead, the DebugBlock has a Q-Channel interface for providing power control to the DebugBlock power domain.

When the DebugBlock is in the Off mode, the DebugBlock does not initiate any accesses and all APB accesses to the DebugBlock receive a PSLVERR response.
