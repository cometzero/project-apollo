# Changing the Routing table owner

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Changing-the-Routing-table-owner>

### Changing the Routing table owner

In a multichip system, you can change the chip that owns the Routing table at any time. However, the Routing table owner must be the last chip to be powered down.

### About this task

The following procedure describes how to change the owner of the Routing table:

### Procedure

1. Write to [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").rt\_owner with a value that selects the appropriate chip to be the Routing table owner.

   The
   chip\_id signal sets the identification value of a chip.
2. Poll for [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").PUP == 0.
