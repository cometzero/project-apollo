# Cluster and core Debug power control

Source: <https://developer.arm.com/documentation/107721/0001/Debug/Cluster-and-core-Debug-power-control>

### Cluster and core Debug power control

The cores included in the DSU-120AE, support the FEAT\_DoPD Debug over PowerDown architectural extension.

The FEAT\_DoPD provides a Debug programmers model where:

- The Debug, Performance Monitoring Unit (PMU), and Embedded Trace Extension (ETE) registers are all in the core power domain.
- The Cross Trigger Interface (CTI) registers for the cores and cluster are all in the Debug power domain.
  > ### Note
  >
  > In the DSU, the CTI registers for both the cores and the cluster are included in the DebugBlock.

The CoreSight Granular Power Requesters, in the DebugBlock ROM table and cluster ROM table, provide the Debug power control for the cluster and core power domains.

### Requesting powerup of the core and cluster Debug registers with the Granular Power Requester registers

In order to access the debug registers included in the core and cluster, the debugger makes power control requests for the cluster power domain, using the DebugBlock ROM table power control (DBROM\_DBGPCR0) register. After the cluster is confirmed as powered up, the debugger makes debug power requests for the core power domains using the cluster ROM table power control registers (CLUSTERROM\_DBGPCR0-CLUSTERROM\_DBGPCR13).

> ### Note
>
> - If the Debugger attempts to access the core Debug registers before the core domain is powered up, it receives an error response.
> - Support for reset catch, to make the cores enter Debug state immediately upon exiting reset, is provided with the cross trigger interface Device Control (CTIDEVCTL) register Reset Catch Enable (RCE) field.

For example, for a cluster configured with a single core, the powerup request sequence is:

1. The debugger makes a power control request to the cluster power domain, for the cluster to be powered up, using the DBROM\_DBGPCR0 register.
2. The Debugger must poll the Cluster Power Status Register (DBROM\_DBGPSR0) to confirm that the cluster is powered up.
3. Once confirmed that the cluster is powered up, the debugger makes a power control request to the core 0 power domain for core 0 to be powered up, using the CLUSTERROM\_DBGPCR0 register.
4. The Debugger must poll the Cluster ROM table Debug Power Status Register0 (CLUSTERROM\_DBGPSR0) for core 0 to confirm that the core is powered up.

### Related information

- [DBROM\_DBGPCR0, DebugBlock ROM table Debug Power Control Register 0](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary/DBROM-DBGPCR0--DebugBlock-ROM-table-Debug-Power-Control-Register-0?lang=en "Controls power requests for PDCLUSTER.")
- [DBROM\_DBGPSR0, DebugBlock ROM table Debug Power Status Register 0](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary/DBROM-DBGPSR0--DebugBlock-ROM-table-Debug-Power-Status-Register-0?lang=en "Indicates the power status for PDCLUSTER.")
- [CLUSTERROM\_DBGPCR0, Cluster ROM table Debug Power Control Register 0](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-DBGPCR0--Cluster-ROM-table-Debug-Power-Control-Register-0?lang=en "Controls power requests for PDCOMPLEX0.")
- [CLUSTERROM\_DBGPSR0, Cluster ROM table Debug Power Status Register 0](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-DBGPSR0--Cluster-ROM-table-Debug-Power-Status-Register-0?lang=en "Indicates the power status for PDCOMPLEX0.")
- [CTIDEVCTL, CTI Device Control register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVCTL--CTI-Device-Control-register?lang=en "Provides target-specific device controls")
- [External debug ROM registers summary](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary?lang=en "The debug ROM table registers are only accessible using memory-mapped accesses over the debug APB interface.")
- [External cluster ROM registers summary](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary?lang=en "The cluster ROM table registers are only accessible using memory-mapped accesses over the debug APB interface.")
