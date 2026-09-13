# Off mode (OFF)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Off-mode--OFF->

### Off mode (OFF)

In the Off mode, all DynamIQ™ cluster shared logic including the snoop filters and L3 cache RAMs is powered down. The PDCLUSTER domain is inoperable and all state is lost.

In the Off mode, power is removed from PDCLUSTER domain (DSU-120AE DynamIQ™ cluster), but the PDTOP domain is still powered up including all the Power Policy Units (PPUs).

The DynamIQ Shared Unit-120AE (DSU-120AE) can be initialized into this mode on a Cold reset.
