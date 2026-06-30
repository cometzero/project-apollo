# About the GIC-720AE

Source: <https://developer.arm.com/documentation/102666/0201/About-the-GIC-720AE>

### About the GIC-720AE

The GIC-720AE is a Functional Safety (FuSa) variant of the GIC‑700. The GIC-720AE is a Generic Interrupt Controller (GIC) that handles interrupts from peripherals to the cores and between cores. The GIC-720AE supports a distributed microarchitecture containing several individual blocks that are used to provide a flexible GIC implementation.

The GIC-720AE supports the GICv3, GICv3.1, and GICv4.1 architecture. For more information, see the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).

The microarchitecture scales from a single core to coherent multichip environments containing up to 64 chips of up to 512 cores each.

> ### Note
>
> This manual defines a chip as an SoC that is integrated with the
> GIC-720AE. A single-chip system has one SoC. A multichip system can have several SoCs that are connected externally, or an SoC comprising several SoCs connected inside a single physical package. In all cases, each SoC is integrated with the
> GIC-720AE.

All the GIC-720AE blocks communicate through fully credited AXI5-Stream interface channels. Therefore, an interface only exerts transient backpressure on its ic<xy>tready signals, enabling packets to be routed over any free-flowing interconnect. Channels can be routed over dedicated AXI5-Stream buses, or over any available free-flowing transport layer in the system. A channel is described as free-flowing when all transactions on that channel complete without a non-transient dependency on any other transaction.

The GIC-720AE includes build scripts that can create appropriate levels of hierarchy for any particular configuration.

> ### Note
>
> The GIC‑700 information is unchanged, and information about the FuSa features available in GIC-720AE can be found in
> [Functional safety in GIC-720AE](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE?lang=en "GIC-720AE is a version of GIC-700 with FuSa detection features added. All FuSa features are “bolted on” to GIC-700 and do not alter the original GIC-700 functionality.").
