# RAM protection

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/RAM-protection>

### RAM protection

RAM instances are not duplicated and are shared by both primary and secondary `noram` instances.

RAMs are protected with the GIC ECC scheme that distinguishes between:

- SEC errors on the data.
- SEC errors on the address.
- DED errors.
- White noise errors, that is, detection of all 0s or all 1s data.

For each RAM, the fault collator allocates a different protection mechanism ID for these RAM error types. Therefore, for a block with many RAMs such as GICD, the RAM errors are a significant proportion of the protection mechanism ID space.

RAM protection also performs lock-step checking of the RAM address, data, and control outputs for the primary and secondary logic.
