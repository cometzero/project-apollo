# ITS AXI5-Stream interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-AXI5-Stream-interface>

### ITS AXI5-Stream interface

The ITS AXI5-Stream interface is a bi-directional interface of either 16-bit or 64-bit width, for communication between the ITS and the Distributor on the same chip.

We expect that a typical distributed system is 16 bits wide. When a pre-existing wide interconnect is used, the 64-bit option allows messages to be efficiently packed.

The interface is fully credited so all messages can be accepted without dependency on any other ports.
