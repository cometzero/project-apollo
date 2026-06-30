# GCI PPI signals

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface/GCI-PPI-signals>

### GCI PPI signals

GIC-720AE supports 16, 32, or 48 PPIs, and synchronized output return wires, for each core. The number of PPIs and return wires must be the same for all cores that are sharing a GCI.

Level-sensitive PPI signals are active-LOW by default, as with previous Arm GIC implementations. However, individual PPI signals can be inverted and synchronized using the following parameters:

- `FAINLIGHT_<usrcfg>_PPI<ppi_id>_<cpu_number>_<ppi_number>_INV`
- `FAINLIGHT_<usrcfg>_PPI<ppi_id>_<cpu_number>_<ppi_number>_SYNC`

  Where `<usrcfg>` is user-defined text that is assigned when the GIC is configured, which can help with identifying a GIC configuration.

Every ppi<n> signal has a corresponding ppi<n>\_r signal from after the synchronizer or capture flop. These ppi<n>\_r signals can be used to create pulse extenders for edge-triggered interrupts that cross clock domains. The `FAINLIGHT_<usrcfg>_PPI<ppi_id>_<cpu_number>_<ppi_number>_INV` parameter also inverts the ppi<n>\_r signal.

Both ppi<n> and ppi<n>\_r have an associated odd parity check signal, that is, ppi<n>\_chk and ppi<n>\_r\_chk.

If you plan to use edge-triggered PPIs and use the Q-Channel to clock gate the GCI hierarchically, then you must include pulse extenders. The pulse extenders ensure that interrupts are not missed while the clock restarts.

For information about the purpose of each PPI used by the core in your system, refer to the relevant core Technical Reference Manual.

### Related concepts

- [PPI signals](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/PPIs/PPI-signals?lang=en "Each PPI is a physical interrupt signal that can be configured to be either a level-sensitive interrupt or an edge-triggered interrupt.")
- [SPI Collator wires](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/SPI-Collator-wires?lang=en "The SPI Collator wires can be extended to create other functions.")
