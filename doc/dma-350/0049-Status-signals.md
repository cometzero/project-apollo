# Status signals

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Status-signals>

### Status signals

These signals indicate different status of the individual channels:

- ch\_enabled shows when a channel is active
- ch\_err shows when a channel has encountered an error
- ch\_stopped shows when the channel is stopped
- ch\_paused shows when the channel is paused
- ch\_priv shows the privilege setting of the channel
- ch\_nonsec shows the security setting of the channel

> ### Note
>
> When SECEXT\_PRESENT is set to 1 the ch\_enabled, ch\_err, ch\_stopped, ch\_paused and ch\_priv signals must be separated based on the ch\_nonsec signals.
>
> The ch\_nonsec signals are not present when SECEXT\_PRESENT is set to 0.
