# L3 cache RAM Quick Nap

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/L3-RAM-power-control/L3-cache-RAM-Quick-Nap>

### L3 cache RAM Quick Nap

Some RAMs, such as the Arm POP RAMs, provide a quick nap (or light sleep) mode. This allows powering down some of the RAM periphery logic to reduce leakage, and also being able to power up again within a small number of cycles so that normal operation can be resumed without impacting performance.

Quick nap is enabled by default, if the RAMs that are implemented support it. There is no need for additional software control.

The L3 cache enters Quick Nap mode automatically after a short period of no activity. Quick Nap is controlled at a granular level for each slice. Therefore, access to one slice does not need to wake the RAMs in another slice. The wakeup is requested when a new access enters the tag pipeline, and so the wakeup can happen in parallel with the tag access. There is no mechanism for stalling the access, so the RAM must be awake by the time the data RAM access occurs. There is no performance impact from this behavior.
