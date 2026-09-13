# Complex power management

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Complex-power-management>

### Complex power management

Each core in a complex has its own Power Policy Unit (PPU), but there is no PPU for the shared logic or dedicated logic of a complex.

For a dual-core complex, the state of the shared logic is automatically managed based on the combined requirements of both of the cores. For example, if one core is powered down (Off mode), the shared logic remains in the On mode while the other core is also in the On mode. When the second core is also powered down, the shared logic powers down (Off mode).
