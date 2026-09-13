# AXI or CHI requester peripheral port

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port>

### AXI or CHI requester peripheral port

You can use the peripheral port to program registers for peripherals using Device accesses, for example, to configure tightly coupled accelerators. You can also use the peripheral port as an alternative requester port to support accesses to the rest of the system whilst the main requester ports connect to main memory.

Using the peripheral port as alternative requester port can help to optimize the latency to DRAM memory in some system designs.

The peripheral port can be configured at build-time configuration to either:

- A 64-bit AXI5 non-coherent requester interface
- A 256-bit AXI5 non-coherent requester interface
- A 256-bit CHI Issue E requester interface. This is a non-coherent interface by default, but you can make it coherent setting BROADCASTOUTERMP signal at reset.

You can optionally include the peripheral port at build-time configuration. You can also configure the peripheral port to use the AXI or CHI protocol at build-time configuration. See RTL configuration process in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual for more details on configuring the peripheral port.

### Related reference

- [Supported memory and transaction types](/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Supported-memory-and-transaction-types?lang=en "The peripheral port supports all transactions that a core can generate including, atomic transactions, cacheable and non-cacheable accesses, and load and store exclusives.")
- [AXI 64-bit peripheral port transactions](/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/AXI-64-bit-peripheral-port-transactions?lang=en "The AXI 64-bit configured peripheral port of the DynamIQ Shared Unit-120AE (DSU-120AE) only generates three types of AXI transactions which are, ReadNoSnoop, WriteNoSnoop, and read and write atomic transactions.")
- [AXI 256-bit peripheral port transactions](/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/AXI-256-bit-peripheral-port-transactions?lang=en "The AXI 256-bit configured peripheral port of the DynamIQ Shared Unit-120AE (DSU-120AE) only generates three types of AXI transactions which are, ReadNoSnoop, WriteNoSnoop, and read and write atomic transactions.")
- [CHI peripheral port transactions](/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/CHI-peripheral-port-transactions?lang=en "The CHI configured peripheral port of DynamIQ Shared Unit-120AE (DSU-120AE) supports the same CHI transactions as the CHI configured main requester interface.")
