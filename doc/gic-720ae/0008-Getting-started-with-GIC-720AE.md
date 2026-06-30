# Getting started with GIC-720AE

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE>

### Getting started with GIC-720AE

There are some basic tasks that you must complete before you can start to use GIC-720AE.

Each Redistributor must be powered on using its [GICR\_PWRR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-PWRR--Power-Register?lang=en "This register controls the powerup sequence of the Redistributors. Software must write to this register during the powerup sequence.") register to enable the Redistributors to be accessed, see [Redistributor power management](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management/Redistributor-power-management?lang=en "At reset, the Redistributors are considered to be powered down. To power up the Redistributors, software must use the GICR_PWRR register.") for more information.

When the GIC-720AE is powered up, it must be programmed as the [Learn the architecture - Generic Interrupt Controller v3 and v4, Overview](https://developer.arm.com/documentation/198123/latest) describes.
