# Initial cluster operating mode

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Power-policy-unit-operation/Initial-cluster-operating-mode>

### Initial cluster operating mode

When using dynamic power state management for the cluster and the cluster moves from the OFF power mode to the ON power mode, the cluster Power Policy Unit (PPU) is requested to initialize the cluster into the ALL SLICE, FULL RAM operating mode.

If you want to initialize the cluster into a different operating mode:

1. Configure the cluster PPU to use a static operating policy.
2. Program the cluster PPU to request the operating mode required.
3. Either use your System Control Processor (SCP) or software running on a core in the cluster to program the Cluster Power Control Register, CLUSTERPWRCTLR. The CLUSTERPWRCTLR register is programmed to configure the cluster to request the preferred operating mode for the cluster.
4. The cluster PPU operating mode control can then be programmed to use dynamic operating mode management.

> ### Note
>
> By default, the cluster powers on in the ALL SLICE, FULL RAM operating mode. However, if the OPRES field in the CLUSTERPWRCTLR register is set, then when the cluster next powers on, the operating mode is set instead to the operating mode that was in use at the time the cluster was powered down.
>
> This state is stored in the PPU logic, and therefore can only be used if the PPUs remain powered on while the cluster is powered OFF.

When dynamic power state management is used to control when the cluster moves from the MEM\_RET power mode to the ON power mode, the cluster PPU is requested to initialize the cluster into the operating mode that was used for the MEM\_RET power mode. The values of the CLUSTERPWRCTLR register and the associated threshold registers reflect the state of the registers when the MEM\_RET power mode was entered. For example, if the cluster was in MEM\_RET power mode and ONE SLICE, FULL RAM operating mode, then the cluster PPU requests that the cluster enters ON power mode, ONE SLICE, FULL RAM operating mode. This means that the dynamic operating mode request should request the most appropriate initial operating mode for the cluster, based on the memory retention operating mode settings.
