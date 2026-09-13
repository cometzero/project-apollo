# PPU and CLUSTERAE register protection

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/PPU-and-CLUSTERAE-register-protection>

### PPU and CLUSTERAE register protection

When DynamIQ Shared Unit-120AE (DSU-120AE) is configured for Lock-configuration or Mixed-configuration (including Split-mode), the Power Policy Unit (PPU) and clusterAE programming registers, that reside in the PDTOP power domain, are protected against incorrect writes to these registers.

The protection is implemented by using a write key register (CLUSTERAE\_CLUSTERWRITEKEY), which has to be written to before any write access can be performed in any of the core PPU registers, cluster PPU registers, or clusterAE registers.

> ### Note
>
> - To unlock CLUSTERAE registers and Power Policy Unit (PPU) registers, write to the CLUSTERAE\_CLUSTERWRITEKEY register, offset address 0x050060, value 0x000000BA.
> - Each time you want to write to any of the PPU and CLUSTERAE registers, you must first write to the CLUSTERAE\_CLUSTERWRITEKEY register. This is because the key is reset after any successful write to the PPU or CLUSTERAE registers. Therefore, the key grants access for only a single write.

If an incorrect value is written to the CLUSTERAE\_CLUSTERWRITEKEY register, then the subsequent write access to the PPU or CLUSTERAE register receives a SLVERR response and the write does not take effect. Similarly, if a PPU or CLUSTERAE register is written to without previously writing to the CLUSTERAE\_CLUSTERWRITEKEY register, then the register receives a SLVERR response and again the write is ignored.

> ### Note
>
> If the
> DSU-120AE is configured for
> Split-configuration, there is no register protection, and therefore no requirement to write to the CLUSTERAE\_CLUSTERWRITEKEY register.

For the CLUSTERAE\_CLUSTERWRITEKEY register description, see [CLUSTERAE\_CLUSTERWRITEKEY, Cluster Write Key Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERWRITEKEY--Cluster-Write-Key-Register?lang=en "Control register for setting the Cluster KEY to enable writing of AE and PPU registers.").
