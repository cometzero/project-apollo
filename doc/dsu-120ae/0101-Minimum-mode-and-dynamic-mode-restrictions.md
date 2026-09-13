# Minimum mode and dynamic mode restrictions

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Minimum-mode-and-dynamic-mode-restrictions>

### Minimum mode and dynamic mode restrictions

When the Power Policy Unit (PPU) is programmed in dynamic mode, Arm recommends that the minimum power mode (PWR\_POLICY) and minimum operating mode (OP\_POLICY) are 0x0. This is because they can prevent power transitions in a way that is hard to predict. In dynamic mode, the PPU determines the target power mode from the maximum of PWR\_POLICY and the dynamically hinted power mode.

The target operating mode is the maximum of OP\_POLICY and the dynamically hinted operating mode. The dynamically hinted values always indicate a power state that can be reached directly from the current power state. However, when the PWR\_POLICY and OP\_POLICY are nonzero, the target power state might not be reachable from the current power state.

If this is the case, the PPU might request an unsupported power transition and the request will be denied. As a result, the power state will not change.
