# Distributor P-Channel

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-P-Channel>

### Distributor P-Channel

The P-Channel is used for power control of the GIC-720AE Distributor.

The P-Channel is present only in multichip configurations. It is used to safely isolate the Distributor from other chips to allow the save and restore of its register states.

### Related concepts

- [Power management](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Power-management?lang=en "The GIC-720AE can be powered down by the system power controller. The GIC also supports the power controller powering down the cores that the GIC services. The GICR_WAKER and the GICR_PWRR registers provide bits to control functions that are associated with power management.")
