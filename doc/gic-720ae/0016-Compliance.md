# Compliance

Source: <https://developer.arm.com/documentation/102666/0201/About-the-GIC-720AE/Compliance>

### Compliance

The GIC-720AE interfaces are compliant with Arm specifications and protocols.

The GIC-720AE is compliant with:

- The AMBA® AXI5-Stream protocol. See the [AMBA® AXI-Stream Protocol Specification](https://developer.arm.com/documentation/ihi0051/b).
- The AMBA ACE5-Lite protocol. See the [AMBA® AXI Protocol Specification](https://developer.arm.com/documentation/ihi0022/j).
- Version 3.1, 3.2, 3.3, 4.1, and 4.2 of the Arm GIC architecture specification. See the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb).
- The Arm® GIC MSI Delivery Interface.
- The GIC Stream protocol. See the GIC Stream Protocol interface appendix in the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb). If [GICR\_FCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en "This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.").ECP == 1, the GIC Cluster Interface (GCI) uses implementation-specific extended packets, which a core must support.
