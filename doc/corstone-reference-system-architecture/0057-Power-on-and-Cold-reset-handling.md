# Power-on and Cold reset handling

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Reset-infrastructure/Power-on-and-Cold-reset-handling>

### Power-on and Cold reset handling

The input nPORESET is the power-on reset input that resets all registers in the design. This includes resetting the Reset Syndrome, see [RESET\_SYNDROME](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-SYNDROME?lang=en "The RESET_SYNDROME register stores the reason for the last Reset event. Writing HIGH to a bit results in that bit write value to be ignored and the bit maintaining its previous value. RESET_SYNDROME is cleared by software writing zero to each bit to clear. If after starting from a reset event, RESET_SYNDROME is not cleared, on another reset event, the register may no longer accurately reflect the last reset event. CPU<n>LOCKUP does not actually generate reset, but when HIGH, it indicates that a CPU has locked-up and could be a precursor to another reset event, for example, watchdog timer reset request.").

The nPORESET is combined with the masked and combined reset requests to generate the internal combined Cold reset, which is available for use by expansion through the nCOLDRESETAON output. These requests are from the following:

- All watchdog timers’ reset requests, through a relevant mask if it exists for each, and only if COLDRESET\_MODE = 0.
- Reset request input RESETREQ if COLDRESET\_MODE = 0.
- Reset request through the SWRESET.SWRESETREQ register value, if COLDRESET\_MODE = 0.
- Reset request input HOSTRESETREQ.
- And reset generated from nSRST request by using negative-edge detection first and then stretching the result.

The nCOLDRESETAON signal resets almost all logic within the system except the [RESET\_SYNDROME](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-SYNDROME?lang=en "The RESET_SYNDROME register stores the reason for the last Reset event. Writing HIGH to a bit results in that bit write value to be ignored and the bit maintaining its previous value. RESET_SYNDROME is cleared by software writing zero to each bit to clear. If after starting from a reset event, RESET_SYNDROME is not cleared, on another reset event, the register may no longer accurately reflect the last reset event. CPU<n>LOCKUP does not actually generate reset, but when HIGH, it indicates that a CPU has locked-up and could be a precursor to another reset event, for example, watchdog timer reset request.") registers.

> ### Note
>
> In each power domain that is directly controlled by a PPU that resides in the PD\_AON or PD\_MGMT domain, the PPU is reset using nCOLDRESETAON or nCOLDRESETMGMT respectively. Each PPU then in turn generates the Cold reset that is used within the power domain it controls. For example, the PPU for PD\_SYS is responsible for generating nCOLDRESETSYS.

When COLDRESET\_MODE = 1, it allows the system to ignore watchdog timers, RESETREQ and SWRESET.SWRESETREQ based reset when generating Cold reset. This is essential if the Cold reset control is owned by a different system. When COLDRESET\_MODE = 1, if any of the five statuses, NSWDRSTREQSTATUS, SWDRSTREQSTATUS, SSWDRSTREQSTATUS, RESETREQSTATUS, SWRSTREQSTATUS is ‘1’, the external entity must, in a short time, the duration of which is IMPLEMENTATION DEFINED, cause a reset by using the HOSTRESETREQ input.

> ### CAUTION
>
> Failing to reset the system can potentially cause system deadlock or even compromise security.
