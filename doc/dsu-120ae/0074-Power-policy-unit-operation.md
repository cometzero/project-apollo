# Power policy unit operation

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Power-policy-unit-operation>

### Power policy unit operation

The Power Policy Unit (PPU) supports all the DSU-120AE DynamIQ™ cluster power modes (ON, OFF, FUNC\_RET, FULL\_RET, MEM\_RET, OFF\_EMU, MEM\_RET\_EMU, WARM\_RST, DBG\_RECOV), and operating modes. It has extensive support to reflect the various combinations of logic and memory power states into which a domain can be set.

Your software can program a PPU to set a PPU mode in one of two ways:

Static policy
:   The PPU is programmed to request a specific PPU mode for the power domain. The hardware request to the core or cluster is only made once the core or DSU-120AE indicates it is ready to enter this PPU mode.

    When a PPU is using static policy to manage power state transitions, this is called static power state management.

Dynamic policy
:   Sets a minimum mode, so the PPU can autonomously change the PPU mode at or above this mode depending on hardware inputs. The upper limit for the range of power modes is ON. The upper limit for the range of operating modes is All slices mode and all RAM instances are active.

    When a PPU is using dynamic policy to manage power state transitions, this is called dynamic power state management.

> ### Note
>
> For general use,
> Arm® recommends using dynamic policy as this gives the most automation and quickest response times to requested power mode changes. However, there are situations where more explicit control is required, such as debugging, and for these situations a static policy might be necessary.

Each PPU contains a state machine representation of its supported PPU mode transitions. For example, the cluster PPU has the PPU mode transitions for the cluster, see [Cluster PPU mode transitions](/documentation/107721/0001/Power-management/Cluster-PPU-mode-transitions?lang=en "The DynamIQ Shared Unit-120AE (DSU-120AE) supports transitions between power and operating modes. Each combination of power mode with an L3 cache slice and L3 cache RAM operating mode forms a Power Policy Unit (PPU) mode, for example, ONE SLICE FULL RAM ON. Some power modes do not have associated operating modes, but these can also be referred to as PPU modes."). Therefore, a PPU can be programmed to target any supported PPU mode and the route taken follows the permissible route, passing through any intermediate PPU modes.

Each of the PPUs has an interrupt output signal that indicates events such as the completion of power mode transitions and the completion of operating mode transitions. For the cluster, this signal is CLUSTERPPUIRQ and for the cores these signals are COREPPUIRQ[<y>], where y is the core instance number.

For the DynamIQ Shared Unit-120AE (DSU-120AE), a PPU is programmed by the System Control Processor (SCP) through the DSU-120AE utility bus. The SCP programs the PPU mode or range of PPU modes that it wants the DSU-120AE DynamIQ™ cluster to enter based on the current system requirements.

The requested PPU mode (power mode and operating mode) is programmed using registers within the PPU. The role of the PPU is to handle the logical operation of a power domain therefore ensuring that the power domain can enter a new power mode safely.

> ### Note
>
> Before performing a write to any of the PPU registers, if the
> DSU-120AE is configured for Lock-configuration or Mixed-configuration, the registers must be unlocked by writing to the CLUSTERAE\_CLUSTERWRITEKEY register. This must be done for each write access to the PPU registers. For more information, see
> [PPU and CLUSTERAE register protection](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/PPU-and-CLUSTERAE-register-protection?lang=en "When DynamIQ Shared Unit-120AE (DSU-120AE) is configured for Lock-configuration or Mixed-configuration (including Split-mode), the Power Policy Unit (PPU) and clusterAE programming registers, that reside in the PDTOP power domain, are protected against incorrect writes to these registers.").

The PPU and the power domain communicate through the device P-Channel. This device P-Channel is internal to the DSU-120AE. The communication is both from the power domain to the PPU and from the PPU to the power domain. For example, communication between the power domain and the PPU could include:

- The power domain indicating to the PPU when the domain needs to enter a higher power mode to complete a function. For example, bringing the L3 cache from a memory retention state to an On state to respond to a cache access.
- The power domain indicating to the PPU when the domain could enter a lower power mode.

The PACTIVE signal of the P-Channel is used to communicate this information to the PPU.

The PPU can also drive the communication to the power domain. For example, when a request is made to go to a higher power mode, the PPU requests that the domain enters the new power mode. The domain can then accept or deny this new power mode.

The Power Control State Machine (PCSM) is responsible for handling functional power requirements, for example controlling power switches to the domain, isolating power supplies, and retention controls. The PPU communicates to the PCSM through an external PCSM P-Channel interface. The P-Channel handshake between the PPU and the PCSM is there to request the specific power rail status change required. It also ensures that the power change happens at the correct time in the PPU power management sequence.

For more information on PPU operation, see [Arm® Power Policy Unit Architecture Specification](https://developer.arm.com/documentation/den0051/latest). For information on system design considerations when designing the PCSM, see System Design in Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
