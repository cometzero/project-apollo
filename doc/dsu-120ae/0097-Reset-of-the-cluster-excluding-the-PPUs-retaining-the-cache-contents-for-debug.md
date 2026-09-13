# Reset of the cluster, excluding the PPUs, retaining the cache contents for debug

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Explicit-reset-of-the-cluster-and-cores/Reset-of-the-cluster--excluding-the-PPUs--retaining-the-cache-contents-for-debug>

### Reset of the cluster, excluding the PPUs, retaining the cache contents for debug

To provide a Cold reset or Warm reset the cluster and cores, excluding the Power Pollicy Units (PPUs) and retaining the cache contents for debug, use one of the following four methods.

> ### Note
>
> - Arm recommends using either methods 2, 3, or 4 when resetting the cores and cluster rather than method 1.
>
>   Because the WARM\_RST and DBG\_RECOV power modes do not wait for transactions to reach a quiescent state before entry, the cluster might be in any power state. Any external component that is communicating with the power domains being reset, for example the system interconnect, must also be reset to ensure any outstanding transactions are terminated. If there is a power transition or a clock gating transition in progress at the time, then the transition might depend on other transactions completing. Therefore, this can prevent the completion of the power or clock transition which in turn can prevent the entry into WARM\_RST or DBG\_RECOV mode. Arm recommends resetting the cluster by using the CLUSTERRECOV register or the input/output domain P-Channel signals (methods 2 to 4) over direct programming of the PPUs (method 1), as it increases the chances of a successful reset as well as being a simpler sequence.
> - The setting of the DBG\_RECOV\_PORST\_EN bit in the PPU\_PTCR register determines if the reset is a Warm reset or a Cold reset.
> - The setting of the PPU\_PTCR.DBG\_RECOV\_PORST\_EN register bit must be consistent across all PPUs (the cluster and all the cores) otherwise the results are UNPREDICTABLE.

### Method 1: Using PPU programming

Arm does not recommend using this method, because it does not guarantee all outstanding power or clock transactions are completed, before the cluster and cores are placed in DBG\_RECOV power mode.

> ### Note
>
> If the
> DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address
> 0x050060, value
> 0x0000\_0000\_0000\_00BA. If the
> DSU-120AE is configured for Split-configuration, then this step is not required.

1. Read the PPU\_PWSR for the cluster and each core, to determine which cores are powered up and what is the current cluster operating mode.
2. For any cores that are already in OFF mode, you must ensure they are in a static OFF, or in a LOCKED OFF state to ensure they do not power up during this process.
3. Check the cluster operating mode and ensure it is in a static configuration so that the operating mode does not change after this step.
4. For each core, and the cluster, program up the corresponding PPU register bit PPU\_PTCR.DBG\_RECOV\_PORST\_EN, for either Cold or Warm reset:

   0
   :   Warm reset

   1
   :   Cold reset

   This must be done for all cores unless in the OFF power mode.
5. Write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x0000000A, which sets the core to the DBG\_RECOV power mode. This must be done for all cores unless:

   - The core is in OFF power mode.
   - PPU\_PTCR.DBG\_RECOV\_PORST\_EN = 0 and
     - the core is either in OFF\_EMU power mode or
     - the core is in WARM\_RST power mode.
6. Write to the cluster PPU\_PWPR, address 0x030000, value 0x0000000A. This sets the cluster to the DBG\_RECOV power mode.
7. Write to the cluster PPU\_PWPR, address 0x030000, value 0x000<p>0008, where <p> is the operating mode value read in step 1. This sets the cluster to the ON power mode.
8. For each core that is in DBG\_RECOV, write to the core PPU\_PWPR register, for core <y>, address 0x<y>80000, value 0x00000008. This puts each core back to the ON power mode.

### Method 2: Using the CLUSTERRECOV register, and not held in reset

To apply a Cold or Warm reset to the cores and the cluster, and immediately come out of reset, use the following sequence.

> ### Note
>
> - For the reset sequence to take effect automatically, ensure steps 1 and 2 are followed. This sets the cluster and core PPUs to dynamic mode, by setting the PWR\_DYN\_EN bit in PPU\_PWPR registers.
> - Arm strongly recommends that the reset sequence is done automatically. However, if you decide to leave the cluster and core PPUs in static mode, for example for debugging, then you must ensure the System Control Processor (SCP) responds to the DEVPACTIVE\* requests. This can be done either by polling the PPUs or by programming the PPUs to raise interrupts to notify your system power controller when the cluster or a core needs to transition to a new power mode. Your system power controller must respond appropriately. For more information on programming the PPUs for static power management and raising interrupts, see section Configure the PPU for static power management  in chapter System design in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to the CLUSTERAE\_CLUSTERRECOV register or PPU registers, you must first unlock access to these registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

1. Write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x100, which sets the core PPU to dynamic mode. This must be done for all coreseven if they are in the OFF power mode.
2. Write to the cluster PPU\_PWPR, address 0x030000, value 0x100. This sets the cluster PPU to dynamic mode.
3. For each core, and the cluster program up the corresponding PPU register bit PPU\_PTCR.DBG\_RECOV\_PORST\_EN, for either Cold or Warm reset:

   0
   :   Warm reset

   1
   :   Cold reset

   This must be done for all cores unless in the OFF power mode.
4. Write to the cluster register CLUSTERAE\_CLUSTERRECOV, offset address 0x050050 , value 0x0000\_0000\_0000\_0001 . This ensures any outstanding power or clock gating transactions are terminated before placing the cores and cluster in DBG\_RECOV power mode.

Once the reset is applied, the hardware automatically places the cluster and cores in the ON power mode. If the PPUs are in dynamic mode, as recommended, then the cluster operating mode is also preserved and so no programming of the PPUs is required.

### Method 3: Using the CLUSTERRECOV register, and held in reset

To apply a Cold or Warm reset to the cores and the cluster, and to control the exit from reset, use the following sequence:

> ### Note
>
> - For the reset sequence to take effect automatically, ensure steps 1 and 2 are followed. This sets the cluster and core PPUs to dynamic mode, by setting the PWR\_DYN\_EN bit in PPU\_PWPR registers.
> - Arm strongly recommends that the reset sequence is done automatically. However, if you decide to leave the cluster and core PPUs in static mode, for example for debugging, then you must ensure the System Control Processor (SCP) responds to the DEVPACTIVE\* requests. This can be done either by polling the PPUs or by programming the PPUs to raise interrupts to notify your system power controller when the cluster or a core needs to transition to a new power mode. Your system power controller must respond appropriately. For more information on programming the PPUs for static power management and raising interrupts, see section Configure the PPU for static power management  in chapter System design in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to the CLUSTERAE\_CLUSTERRECOV register or PPU registers, you must first unlock access to these registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

1. Write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x100, which sets the core PPU to dynamic mode. This must be done for all coreseven if they are in the OFF power mode.
2. Write to the cluster PPU\_PWPR, address 0x030000, value 0x100. This sets the cluster PPU to dynamic mode.
3. For each core, and the cluster program up the corresponding PPU register bit PPU\_PTCR.DBG\_RECOV\_PORST\_EN, for either Cold or Warm reset:

   0
   :   Warm reset

   1
   :   Cold reset

   This must be done for all cores unless in the OFF power mode.
4. Write to the cluster register CLUSTERAE\_CLUSTERRECOV, offset address 0x050050 , value 0x0000\_0000\_0000\_0003 . This ensures any outstanding power or clock gating transactions are terminated before requesting the cores and cluster are placed in the DBG\_RECOV power mode.
5. Wait until the cluster register CLUSTERAE\_CLUSTERRECOV, offset address 0x050050 , reads value 0x0000\_0000\_0000\_0007. This indicates all the cores and cluster are held in the DBG\_RECOV power mode.
6. When required, exit from the DBG\_RECOV power mode and transition the cores and cluster to the ON power mode by writing to the CLUSTERAE\_CLUSTERRECOV register, offset address 0x050050 , value 0x0000\_0000\_0000\_0000 .

When the cluster and cores are placed in the ON power mode, if the PPUs are in dynamic mode, as recommended, then the cluster operating mode is also preserved and so no programming of the PPUs is required.

### Method 4: Reset of the cluster using INPUTDOMAINPACTIVE and OUTPUTDOMAINPACTIVE signals

To apply a Cold reset to the cores and cluster using either the input or output P-Channel interfaces, and to control the exit from reset, use the following sequence:

> ### Note
>
> - Arm strongly recommends that the reset sequence is done automatically. However, if you decide to leave the cluster and core PPUs in static mode, for example for debugging, then you must ensure the System Control Processor (SCP) responds to the DEVPACTIVE\* requests. This can be done either by polling the PPUs or by programming the PPUs to raise interrupts to notify your system power controller when the cluster or a core needs to transition to a new power mode. Your system power controller must respond appropriately. For more information on programming the PPUs for static power management and raising interrupts, see section Configure the PPU for static power management  in chapter System design in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
> - If the DSU-120AE is configured for Lock-configuration or Mixed-configuration (including Split-mode) then each time before writing to a PPU register you must first unlock the PPU registers. To do this, write to the register CLUSTERAE\_CLUSTERWRITEKEY, offset address 0x050060, value 0x0000\_0000\_0000\_00BA. If the DSU-120AE is configured for Split-configuration, then this step is not required.

1. Write to the core PPU\_PWPR for core <y>, address 0x<y>80000, value 0x100, which sets the core PPU to dynamic mode. This must be done for all coreseven if they are in the OFF power mode.
2. Write to the cluster PPU\_PWPR, address 0x030000, value 0x100. This sets the cluster PPU to dynamic mode.
3. For each core, and the cluster program up the corresponding PPU register bit PPU\_PTCR.DBG\_RECOV\_PORST\_EN, for either Cold or Warm reset:

   0
   :   Warm reset

   1
   :   Cold reset

   This must be done for all cores unless in the OFF power mode.
4. Drive the INPUTDOMAINPACTIVE[10] signal or the OUTPUTDOMAINPACTIVE[10] signal HIGH (depending on what interface you are using) to request DBG\_RECOV power mode for the cluster and cores. This ensures any outstanding power or clock gating transactions are terminated before requesting the cores and cluster are placed in the DBG\_RECOV power mode.
5. Wait until the signal CLUSTERPPUHWSTAT[10] is driven HIGH. This indicates that the cluster and cores have been placed in the DBG\_RECOV power mode.

   > ### Note
   >
   > Optionally, keeping the
   > INPUTDOMAINPACTIVE[10] or
   > OUTPUTDOMAINPACTIVE[10] driven HIGH, after the
   > CLUSTERPPUHWSTAT[10] indicates HIGH, holds the
   > cores and the cluster in Cold reset.
6. When required to exit from WARM\_RST power mode, drive either the INPUTDOMAINPACTIVE[10] signal or OUTPUTDOMAINPACTIVE[10] signal LOW depending on what interface you are using.

   Once the reset is applied, the hardware automatically places the cluster and cores to the ON power mode. If the PPUs are in dynamic mode, as recommended, then the cluster operating mode is also preserved and so no programming of the PPUs is required.
