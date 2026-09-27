# Controlling PD_VMR<i> power mode

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-SYS-power-modes/Controlling-PD-VMR-i--power-mode>

### Controlling PD\_VMR<i> power mode

To configure the required low-power state of each PD\_VMR<i>, software must configure the register fields PDCM\_PD\_VMR<i>\_SENSE.MIN\_PWR\_STATE as follows:

- Set to 0b00 to set the low-power state of the PD\_VMR<i> to OFF. Therefore PD\_VMR<i> only ever transitions between ON and OFF state, and is never in retention, meaning that in low-power state, all state in VM<i> is lost.

  With this setting, when PD\_SYS is ON and the BR\_SYS is in one of the ON\_OPMODE modes that currently has PD\_VMR<i> ON, it transitions to another ON\_OPMODE where PD\_VMR<i> is OFF automatically when the PD\_VMR<i> domain is idle. Therefore, expect to see PD\_VMR<i> turn off quickly once PDCM\_PD\_VMR<i>\_SENSE.MIN\_PWR\_STATE is set to 0b00.

  Once PD\_VMR<i> is OFF, it can only be returned to ON by an access on the bus targeting PD\_VMR<i>, but following that, when PD\_VMR<i> is idle again, it turns off again. To avoid this, configure PDCM\_PD\_VMR<i>\_SENSE.MIN\_PWR\_STATE to a nonzero value before accessing the VM<i>.
- Set to 0b01 to set the low-power state of the PD\_VMR<i> to Retention. PD\_VMR<i> only ever transitions between ON and Retention state, and is never OFF, meaning that in low-power state, all registers states in VM<i> are retained. Therefore, for BR\_SYS, it never transitions to a power mode that has PD\_VMR<i> turned off. To place the PD\_VMR<i> into Retention, the BR\_SYS power modes have to enter one of the FULL\_RET\_OPMOE modes or MEM\_RET\_OPMODE mode where PD\_VMR<i> is in Retention. This means that it is not possible to place a PD\_VMR into retention while keeping PD\_SYS ON.
