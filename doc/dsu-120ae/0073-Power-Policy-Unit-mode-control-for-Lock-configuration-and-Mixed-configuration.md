# Power Policy Unit mode control for Lock-configuration and Mixed-configuration

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Power-Policy-Unit-mode-control-for-Lock-configuration-and-Mixed-configuration>

### Power Policy Unit mode control for Lock-configuration and Mixed-configuration

When using Lock-configuration or Mixed-configuration, a single Power Policy Unit (PPU) can be used to control the power transitions for two cores.

### PPU power mode control for Lock-configuration

In Lock-configuration a single logical PPU controls the power mode requests for both the primary and redundant core. There is a single Power Control State Machine (PCSM) interface for the primary and redundant core. The single core PCSM is responsible for controlling the power domains for both the primary and redundant core. The single complex PCSM is responsible for both the primary and redundant complex power domains. In Lock-configuration a single logical PPU controls the power mode requests for both the primary and redundant cluster logic. There is a single PCSM interface for the primary and redundant cluster logic. The single core PCSM is responsible for controlling the power domains for both the primary and redundant cluster logic.

### PPU power mode control for Mixed-configuration

In Mixed-configuration, there is a separate logical PPU instance for each physical core.

PPU power mode control for Mixed-configuration, where the cores are in Split-mode
:   In
    core
    Split-mode each physical
    core is controlled by a separate PPU instance.

PPU power mode control for Mixed-configuration, where the cores are in Lock-mode
:   In core Lock-mode a single logical PPU controls the power mode requests for both the primary and redundant core. The PPU is identified by the primary core physical core numbering. For example, if the primary core is physical core 2 then the PPU 2 instance is used to control the power modes for the primary core 2 and its equivalent redundant core. The single PPU drives the PCSM interfaces for both the primary and redundant physical cores. The external core PCSMs must respond to both physical core PCSM interfaces so that the power control for the primary and redundant core is identical. The external complex PCSMs must respond to both physical complex PCSM interfaces so that the power control for the primary and redundant complex domain is identical.

PPU power mode control for Mixed-configuration Split-mode cluster
:   In cluster Split-mode a single logical PPU instance controls the power mode requests for both the primary and redundant cluster logic. The redundant logic is clock gated and remains inactive, but powered up. There is a single PCSM interface for the primary and redundant cluster logic. The single cluster PCSM is responsible for controlling the power domains for both the primary and redundant cluster logic.

PPU power mode control for Mixed-configuration Lock-mode cluster
:   In cluster
    Lock-mode a single logical PPU instance controls the power mode requests for both the
    primary and
    redundant cluster logic. There is a single PCSM interface for the
    primary and
    redundant cluster logic. The single cluster PCSM is responsible for controlling the power domains for both the
    primary and
    redundant cluster logic.
