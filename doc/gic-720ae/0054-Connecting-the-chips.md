# Connecting the chips

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Connecting-the-chips>

### Connecting the chips

Use the following procedure to connect the chips in a multichip configuration.

### Before you begin

The following restrictions apply when connecting or removing chips:

- You must consider that data that is read from [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.") is valid only when [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").PUP == 0, otherwise the data might be updating.
- If you are connecting a new chip, the accesses must be done through a chip that is in the Consistent state and not by writing to the new chip directly.
- If you access [GICD\_CHIPSR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register?lang=en "This register returns the status of the chip in a multichip configuration. A single copy of this register exists on each chip in a multichip configuration.") while a chip is being connected, it shows RTS == Updating. Also, the [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").PUP bit is set, indicating that the Routing table is updating, so the values cannot be trusted.
- Adding or removing a chip when [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.") group enables are set is unpredictable. To check that group enables are off, software must poll [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.").RWP.
- If you are connecting together multiple different instances of the GIC-720AE, the settings of the gicd\_ctlr\_ds signal must match in all chips.
- If you are connecting together multiple different instances of the GIC-720AE, the settings for the following parameters must match in all chips:
  - All affinity widths (`max_affinity_width`\*)
  - Number of SPI blocks supported (`spi_blocks`)
  - LPI support type (`lpi_support`)
  - Total number of chips supported (`chip_count`)
  - Chip address width (`chip_addr_width`)
  - Chip affinity select level (`chip_affinity_select_level`)
  - Maximum number of cores on any single chip (`max_pe_on_chip`)
  - The number of vPEs (`vpe_width`)
  - GICv4.1 architecture support (`gicv41_support`)
  - 1 of N support (`spi_1ofn_support`)
  - Cross-chip interface protocol (`ace_cc`)
  - Cross-chip addressing mode (`local_chip_addr`)
  - Non-maskable interrupt (NMI) support (`nmi_support`)
  - Multi view support (`multi_view_support`)

  See the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual for information about configuration parameters and their options.

### About this task

The procedure for connecting the chips in a multichip configuration is as follows:

### Procedure

1. Ensure that the values of the chip\_id tie-off input signals to all chips are correct.
2. Ensure that all Group enables in the [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.") register are disabled and [GICD\_CTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CTLR--Distributor-Control-Register?lang=en "This register enables interrupts for Group 0 and Group 1. It also indicates whether the Distributor supports 1 or 2 security states, and whether a register write is in progress.").RWP == 0.
3. Designate a chip, chip `x`, to own the Routing table.

   You can designate a different chip later, if necessary.
4. Before software brings a chip online by writing to the RT owner, it must program all local [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").ADDR fields. The procedure depends on whether local chip addressing is enabled.

   When
   [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").LCA == 0:

   1. Software programs all the [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").ADDR fields from a single chip, ideally the RT owner, by writing to a single Distributor instance.

      When the chip comes online, it broadcasts the address values to the other chips.

   When
   [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").LCA == 1:

   1. Software programs all the [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").ADDR fields, for each chip separately.

      For example, each chip writes all the required [GICD\_CHIPRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").ADDR values to its own Distributor. Software must ensure that all remote chip addresses are unique from any given chip.

      When the chip comes online, the address values are not broadcast to the other chips.
5. In a single register write, program [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.") with:
   1. [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").ADDR so that each chip can forward messages to chip `x`.

      Depending on how cross-chip messages are routed, this value can be the
      chip\_id signal value or a more complex identifier. For an:
      - AXI5-Stream cross-chip interface, this value is sent on the icdrtdest signal.
      - ACE5-Lite cross-chip interface, this value is sent on the awaddr[AXIM\_ADDR\_WIDTH−1:16] signal.
   2. [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").SPI\_BLOCK\_MIN and [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").SPI\_BLOCKS to appropriate values for the SPIs that chip `x` owns.

      Step example: If the range of interrupt ids for chip
      `x` is ID96-ID159:
      - Set SPI\_BLOCK\_MIN = (96 – 32) / 32 = 2
      - Set SPI\_BLOCKS = (159 – 96 + 1) / 32 = 2
   3. [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").SocketState = 1
6. To check that the writes are successful, read [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").

   The writes might fail due to security settings, an overlapping or nonexistent SPI, or if another update is still in progress. If the accesses fail, then
   [GICD\_CHIPRx](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").SocketState == 0, indicating that the chip is offline.
7. To check that the actions of this sequence have executed correctly, read the following register fields and ensure that their values are as follows:

   1. [GICD\_CHIPSR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPSR--Chip-Status-Register?lang=en "This register returns the status of the chip in a multichip configuration. A single copy of this register exists on each chip in a multichip configuration.").RTS == 2 (Consistent)
   2. [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").rt\_owner == chip `x`
   3. [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.").PUP == 0

   Step result: Chip
   `x` is now in the Consistent state and ready to accept connections to other chips in the system configuration.

To connect more chips:

8. Set the relevant address and SPI ownership information of the next chip you want to connect to, chip `y`, by writing to [GICD\_CHIPRy](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").

   You can do this step through any chip that is already connected, or more efficiently by writing to the chip that owns the Routing table,
   chip\_id signal value == rt\_owner.
9. Poll [GICD\_DCHIPR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-DCHIPR--Default-Chip-Register?lang=en "This register allows Secure software to access the status of a chip in a multichip system. A single copy of this register exists on each chip in a multichip configuration.") until bit PUP == 0, indicating that the connection is complete.
10. To check whether the write to [GICD\_CHIPRy](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.") is accepted, read [GICD\_CHIPRy](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CHIPR-n---Chip-Registers?lang=en "Each register controls the configuration of the chip in a multichip system. This register exists on each chip in a multichip configuration and is identified by the chip number.").

    For each chip connection, repeat steps
    [8](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Connecting-the-chips?lang=en#csb1535012996381__step.add_chipY) through
    [10](https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Connecting-the-chips?lang=en#csb1535012996381__step.verify_chipY).
