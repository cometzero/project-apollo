# L3 RAM power control

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control>

### L3 RAM power control

In addition to retention features, the DynamIQ Shared Unit-120AE (DSU-120AE) can further reduce static leakage power, using three powerdown features.

- Optionally power down half, or all except one, of the L3 cache slices.
- Within each L3 cache slice, power down a portion of the L3 cache RAM that the cache slice contains.
- Use Quick Nap with L3 data RAMs, for fine-grained automatic transitions to a low-leakage power mode.
