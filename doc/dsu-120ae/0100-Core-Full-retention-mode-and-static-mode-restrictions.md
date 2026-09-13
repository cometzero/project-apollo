# Core Full retention mode and static mode restrictions

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Core-Full-retention-mode-and-static-mode-restrictions>

### Core Full retention mode and static mode restrictions

The use of Full retention (FULL\_RET) mode for a core is not recommended when the Power Policy Unit (PPU) is programmed in static mode.

This is because when a utility bus transaction is made to a core that is in FULL\_RET, the core must transition to ON to service the utility bus transaction. However in static mode the transition requires programming of the PPU using the utility bus, which is already in use. To avoid this dependency causing a deadlock, if the PPU is in static mode any utility bus access to a core in FULL\_RET receives a SLVERR response.

> ### Note
>
> For both
> core and cluster power modes,
> Arm® recommends not using FULL\_RET or FUNC\_RET mode with static mode. This is because of the responsiveness of the system to wake from full retention or functional retention. It is expected that for most use cases that dynamic mode is used.
