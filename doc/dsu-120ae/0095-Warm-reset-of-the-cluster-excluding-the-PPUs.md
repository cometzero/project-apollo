# Warm reset of the cluster, excluding the PPUs

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Explicit-reset-of-the-cluster-and-cores/Warm-reset-of-the-cluster--excluding-the-PPUs>

### Warm reset of the cluster, excluding the PPUs

To provide a Warm reset to all the cores and the cluster use one of the following four methods. This type of reset can be used to recover from a watchdog timeout or a RAS error.

> ### Note
>
> Arm recommends using either methods 2, 3, or 4 when resetting the cores and cluster rather than method 1.
>
> Because the WARM\_RST and DBG\_RECOV power modes do not wait for transactions to reach a quiescent state before entry, the cluster might be in any power state. Any external component that is communicating with the power domains being reset, for example the system interconnect, must also be reset to ensure any outstanding transactions are terminated. If there is a power transition or a clock gating transition in progress at the time, then the transition might depend on other transactions completing. Therefore, this can prevent the completion of the power or clock transition which in turn can prevent the entry into WARM\_RST or DBG\_RECOV mode. Therefore, Arm recommends resetting the cluster by using the CLUSTERRECOV register or the input/output domain P-Channel signals (methods 2 to 4) over direct programming of the PPUs (method 1), as it increases the chances of a successful reset as well as being a simpler sequence.

### Method 1: Warm reset of the cluster using PPU programming

To apply a Warm reset to the cores and cluster use the following sequence.

> ### Note
>
> If the
> DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address
> 0x050060, value
> 0x0000\_0000\_0000\_00BA. If the
> DSU-120AE is configured for Split-configuration, then this step is not required.

1. Ensure that the cluster is in On mode and the cores are either in On mode, Off mode, or Emulated off mode. Read the PPU\_PWSR for the cluster to determine the current cluster operating mode.
2. For any of the cores that are in the On mode, write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x00000009. This sets the core to the WARM\_RST power mode.
3. Write to the cluster PPU\_PWPR, address 0x030000, value 0x00000009. This sets the cluster to the WARM\_RST power mode.
4. Write to the cluster PPU\_PWPR, address 0x030000, value 0x000<p>0008, where <p> is the operating mode value read in step 1. This sets the cluster to the ON power mode.
5. For each core that is in WARM\_RST, write to the core PPU\_PWPR register, for core <y>, address 0x<y>80000, value 0x00000008. This puts each core back to the ON power mode.

### Method 2: Using the CLUSTERRECOV register, and not held in reset.

To apply a Warm reset to the cores and the cluster, and immediately come out of reset, use the following sequence.

> ### Note
>
> Arm strongly recommends that the reset sequence is done automatically. However, if you decide to leave the cluster and
> core PPUs in static mode, for example for debugging, then you must ensure the System Control Processor (SCP) responds to the
> DEVPACTIVE\* signal requests. This can be done either by polling the PPUs or by programming the PPUs to raise interrupts to notify your system power controller when the cluster or a
> core needs to transition to a new power mode. Your system power controller must respond appropriately. For more information on programming the PPUs for static power management and raising interrupts, see section
> Configure the PPU for static power management  in chapter
> System design in the
> Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

1. If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode), write to the cluster register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA, to unlock access to the CLUSTERAE\_CLUSTERRECOV register. If the DSU-120AE is configured for Split-configuration, then this step is not required.
2. Write to the cluster register CLUSTERAE\_CLUSTERRECOV, offset address 0x050050 , value 0x0000\_0000\_0000\_0010 . This places the cores and cluster in WARM\_RST power mode.

Once the reset is applied, the hardware automatically places the cluster and cores in the ON power mode. If the PPUs are in dynamic mode, then the cluster operating mode is also preserved and so no programming of the PPUs is required.

### Method 3: Using CLUSTERRECOV register, and held in reset

To apply a Warm reset to the cores and the cluster, and to control the exit from reset, use the following sequence:

> ### Note
>
> - Arm strongly recommends that the reset sequence is done automatically. However, if you decide to leave the cluster and core PPUs in static mode, for example for debugging, then you must ensure the System Control Processor (SCP) responds to the DEVPACTIVE\* signal requests. This can be done either by polling the PPUs or by programming the PPUs to raise interrupts to notify your system power controller when the cluster or a core needs to transition to a new power mode. Your system power controller must respond appropriately. For more information on programming the PPUs for static power management and raising interrupts, see section Configure the PPU for static power management  in chapter System design in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to the CLUSTERAE\_CLUSTERRECOV register, you must first unlock access to this register. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

1. Write to the cluster register CLUSTERAE\_CLUSTERRECOV, offset address 0x050050 , value 0x0000\_0000\_0000\_0030 . This requests that the cores and cluster are placed in the WARM\_RST power mode.
2. Wait until the cluster register CLUSTERAE\_CLUSTERRECOV, offset address 0x050050 , reads value 0x0000\_0000\_0000\_0070. This indicates all the cores and cluster are held in the WARM\_RST power mode.
3. When required, exit from WARM\_RST and transition the cores and cluster to the ON power mode by writing to the CLUSTERAE\_CLUSTERRECOV register, offset address 0x050050 , value 0x0000\_0000\_0000\_0000.

When the cluster and cores are placed in the ON power mode, if the PPUs are in dynamic mode, as recommended, then the cluster operating mode is also preserved and so no programming of the PPUs is required.

### Method 4: Warm reset of the cluster using INPUTDOMAINPACTIVE and OUTPUTDOMAINPACTIVE signals

To apply a Warm reset to the cores and cluster using either the input or output P-Channel interfaces, and to control when the cores and cluster exit from reset, use the following sequence:

> ### Note
>
> Arm strongly recommends that the reset sequence is done automatically. However, if you decide to leave the cluster and
> core PPUs in static mode, for example for debugging, then you must ensure the System Control Processor (SCP) responds to the
> DEVPACTIVE\* signal requests. This can be done either by polling the PPUs or by programming the PPUs to raise interrupts to notify your system power controller when the cluster or a
> core needs to transition to a new power mode. Your system power controller must respond appropriately. For more information on programming the PPUs for static power management and raising interrupts, see section
> Configure the PPU for static power management  in chapter
> System design in the
> Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

1. Drive the INPUTDOMAINPACTIVE[9] signal or the OUTPUTDOMAINPACTIVE[9] signal HIGH (depending on what interface you are using) to request WARM\_RST power mode for the cluster and cores. This ensures the cores and cluster are placed in the WARM\_RST power mode.
2. Wait until the signal CLUSTERPPUHWSTAT[9] is driven HIGH. This indicates that the cluster and cores have been placed in the WARM\_RST power mode.

   > ### Note
   >
   > Optionally, keeping the
   > INPUTDOMAINPACTIVE[9] or
   > OUTPUTDOMAINPACTIVE[9] driven HIGH, after the
   > CLUSTERPPUHWSTAT[9] indicates HIGH, holds the
   > cores and the cluster in Warm reset.
3. When required to exit from WARM\_RST power mode, drive either the INPUTDOMAINPACTIVE[9] signal or OUTPUTDOMAINPACTIVE[9] signal LOW depending on what interface you are using.

   Once the reset is applied, the hardware automatically places the cluster and cores to the ON power mode. If the PPUs are in dynamic mode, as recommended, then the cluster operating mode is also preserved and so no programming of the PPUs is required.
