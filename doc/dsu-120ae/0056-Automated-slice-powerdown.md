# Automated slice powerdown

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-slice-powerdown/Automated-slice-powerdown>

### Automated slice powerdown

This feature provides more hardware automation of the slice powerdown decision.

When the CLUSTERPWRCTLR.AUTOSLC field is zero, only the SLCRQ field controls the slice powerdown. When the AUTOSLC field is nonzero, it enables the automation and indicates the time period with which the slice powerdown decisions are made.

The decision to change the slice power mode depends on these conditions:

- SLCRQ bits. These indicate a minimum mode, below which the slices are not powered off. For example, this allows the use of HALF SLICES mode while preventing the L3 cache from entering ONE SLICE mode.
- If the SLCSF bit is set and the number of cores powered on requires a snoop filter size greater than the current slice power mode, the slice power mode is increased.
- If the CLUSTERPWRDN.SHORTSLP bit for a core is set high, this indicates that the core must be treated as if it were ON for the automated slice power down calculation, even if the core is OFF.
- If the SLCBW bit is set and the slice bandwidth is higher than the threshold for this time period, the slice power mode is increased.
- If the number of cores powered on is greater than the HSLCCNT or OSLCCNT fields, after masking with the HSLCMASK or OSLCMASK fields, the slice power mode is increased. This allows configuring behaviors based on the number and types of core. For example, if you have a configuration with 4 high-performance cores and 4 high-efficiency cores, you can ensure that:
  - If any high-performance core is powered on, it uses ALL SLICE mode.
  - If no high-performance cores are powered on, they use HALF SLICE mode.
  - If only two or less high-efficiency cores are powered on, ONE SLICE mode can be entered.

This example can be configured with these settings:

- Set HSLCMASK to include all the high-performance cores
- Set HSLCCNT to 0.
- Set OSLCMASK to include all the high-efficiency cores.
- Set OSLCCNT to 2.

> ### Note
>
> If the SLCPRTN bit is set, then the AUTOPRTN mechanism can indicate if more cache capacity is required.

These conditions are checked continuously, and if any become true indicating that more slices are needed, then the SLCPRTN bit operating mode immediately transitions to a higher number of slices. Depending on the current conditions, in ONE SLICE mode, the transition can be to HALF SLICES, or directly to ALL SLICES. This occurs because a single direct transition is more efficient than going through HALF SLICES mode with two separate transitions.

For transitions to a smaller number of slices, the decision is more conservative. This decision is made only at the end of each configured time period, and all of the conditions must indicate that a lower number of slices is suitable. This must also be true for the whole of the time period. The transitions to a smaller number of slices is always done in steps, from ALL to HALF, and then only HALF to ONE, after at least one more time period has passed.

Conditions that include the core power status by default treat the core as ON if it is in any power mode other than OFF or OFF\_EMU.

However, in some cases the operating system might have more information about how long the core is likely to remain off. If the OS has information that the core is only likely to remain off for a short time, it can set the CLUSTERPWRDN.SHORTSLP bit high before powering off the core. If the operating system anticipates that the core will be powered off for longer, it sets the CLUSTERPWRDN.SHORTSLP bit low before powering off the core.

The AUTOSLC logic takes this into account, and treats any core with the SHORTSLP bit set to the same value as if it was still on. This means that the slice power off decisions only take place if the core is likely to remain in that state for a long period.

When the SLCPRTN bit is clear, the slice powerdown decisions are made independently of the RAM powerdown decisions. However, when the SLCPRTN bit is set, the two mechanisms interact with each other to give a complementary sequence of steps. Starting from ALL SLICE FULL RAM, the AUTOPRTN mechanism decides in the usual way whether to power down half the RAMs, giving half the cache capacity.

When the DSU has been in ALL SLICE HALF RAM mode for at least the AUTOSLC timeout period, and all the other conditions are met, then a transition starts to HALF SLICES mode, followed immediately by a transition to FULL RAM. This means that the bandwidth and power are reduced in HALF SLICE mode, but the cache capacity remains unchanged at half the overall capacity. The AUTOPRTN can then continue and choose to go back to HALF RAM, giving a quarter of the overall cache capacity.

When the DSU has been in HALF SLICE HALF RAM mode for at least the AUTOSLC timeout period, and all the other conditions are met, then a transition starts to ONE SLICE, followed immediately by a transition to FULL RAM. This keeps the capacity at a quarter if four slices are configured, or reduces to one eighth if 8 slices are configured. The AUTOPRTN mechanism can then continue in the usual manner and enter HALF RAM, or eventually SFONLY mode, while remaining in ONE SLICE mode.

If at any time in a FULL RAM mode, the AUTOPRTN mechanism indicates that more cache capacity is required, the slice power state changes to enable more capacity, if it is not already in ALL SLICE mode. The IMP\_CLUSTERL3UPTH2\_EL1 / CLUSTERL3UPTH2 upsize threshold 2 register configures this transition threshold.
