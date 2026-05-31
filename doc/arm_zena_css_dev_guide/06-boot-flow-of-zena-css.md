<a id="boot-flow-of-zena-css"></a>

# 6 Boot flow of Zena CSS

The Zena CSS boot flow describes the initial portion of boot operations and the boot block device interface.

The general boot flow is described in the [main boot sequence](06-boot-flow-of-zena-css.md#boot-flow-of-zena-css-main-boot-sequence). Each lifeline in the figures represents an abstract system consisting of hardware and software:

- The External Safety Manager and the Block Device Controller are not part of Zena CSS. The Runtime Security Engine, the Safety Island, and the Primary Compute are part of Zena CSS.
- The Runtime Security Engine system consists of the RSE Block and multiple software images.
- The Safety Island system consists of the Safety Island Block and multiple software images.
- The Primary Compute system consists of the Processor Block, the Interrupt Block, the I/O Block, the Interconnect Block, the Peripheral Block, and multiple software images.
- The Reset Generation Manager Block is a shared component that is part of the Runtime Security Engine system, the Safety Island system, and the Primary Compute system.

<a id="boot-flow-of-zena-css-main-boot-sequence"></a>

## 6.1 Main boot sequence

The main boot sequence includes the key stages of the boot process, ensuring a systematic and Secure initialization of Zena CSS.

> **Note**
>
> In the figures illustrating the main boot sequence, a ref element indicates a part of the sequence that a later section describes in more detail.
>
> Common procedures during the stages of the main sequence include [self tests](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__bist-rse-self-test), [image loading](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__secure-load-image-sequence), and [verification](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__verify-configuration-sequence).

<a id="md234-main-boot-sequence__system-boot-sequence"></a>

### System boot sequence

The following figure shows the Zena CSS system boot sequence, in which the Runtime Security Engine performs a self test before the rest of the boot flow proceeds.

<a id="md234-main-boot-sequence__fig_boot_scenario1"></a>

**Figure 6-1: System boot sequence**

![System boot sequence](assets/figure-6-1-system-boot-sequence.png)

For more information about the self test, see [BIST RSE sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__bist-rse-self-test).

<a id="md234-main-boot-sequence__compute-subsystem-css-boot-sequence"></a>

### Compute subsystem (CSS) boot sequence

The following figure shows the CSS boot sequence that was initiated during the preceding system boot sequence.

<a id="md234-main-boot-sequence__fig_boot_compute_subsystem_scenario1"></a>

**Figure 6-2: CSS boot sequence**

![CSS boot sequence](assets/figure-6-2-css-boot-sequence.png)

<a id="md234-main-boot-sequence__rse_prodname_long-rse_prodname_short-boot-sequence"></a>

### Runtime Security Engine (RSE) boot sequence

The RSE boot sequence takes place in three parts. The first figure shows the RSE phase 1 stage 1 boot sequence that was initiated during the preceding CSS boot sequence.

<a id="md234-main-boot-sequence__fig_boot_rse_1_1"></a>

**Figure 6-3: RSE phase 1 stage 1 boot sequence**

![RSE phase 1 stage 1 boot sequence](assets/figure-6-3-rse-phase-1-stage-1-boot-sequence.png)

RSE BL1_1 is a boot loader (stored in ROM) that is responsible for the first few steps of the RSE boot sequence:

1. Initialize critical RSE subsystems.
2. Check for a valid RSE BL1_2 image in a One-Time-Programmable (OTP) memory block. If valid:
    1. Load RSE BL1_2 from OTP memory to RSE SRAM.
    2. Jump to RSE BL1_2 in RSE SRAM.

For more information about the image load, see [Secure load image sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__secure-load-image-sequence).

The second figure shows the RSE phase 1 stage 2 boot sequence, which was initiated during the preceding boot sequence.

<a id="md234-main-boot-sequence__fig_boot_rse_1_2"></a>

**Figure 6-4: RSE phase 1 stage 2 boot sequence**

![RSE phase 1 stage 2 boot sequence](assets/figure-6-4-rse-phase-1-stage-2-boot-sequence.png)

RSE BL1_2 is a boot loader that is responsible for the next steps of the RSE boot sequence:

1. Initialize remaining RSE subsystems, and execute any patch code required.
2. Initialize the Block Device Controller.
3. Check for a valid RSE BL2 image in a block device. If valid:
    1. Load RSE BL2 from the block device to RSE SRAM.
    2. Jump to RSE BL2 in RSE SRAM.

For more information about the image load, see [Secure load image sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__secure-load-image-sequence).

The third figure shows the RSE phase 2 boot sequence, which was initiated during the preceding boot sequence.

<a id="md234-main-boot-sequence__fig_boot_rse_2"></a>

**Figure 6-5: RSE phase 2 boot sequence**

![RSE phase 2 boot sequence](assets/figure-6-5-rse-phase-2-boot-sequence.png)

RSE BL2 is a boot loader that is responsible for the final steps of the RSE boot sequence:

1. Initialize critical portions of the system management block.
2. Initiate a self test on the Safety Island.
3. Control the first part of the Safety Island boot sequence.

For more information about the self test, see [BIST Safety Island sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__bist-si-self-test).

<a id="md234-main-boot-sequence__safetyisland-boot-sequence"></a>

### Safety Island boot sequence

The following figure shows the Safety Island boot sequence that was initiated during the preceding RSE phase 2 boot sequence.

<a id="md234-main-boot-sequence__fig_boot_safety_island"></a>

**Figure 6-6: Safety Island boot sequence**

![Safety Island boot sequence](assets/figure-6-6-safety-island-boot-sequence.png)

The first part of the boot sequence is controlled by the RSE BL2 boot loader:

1. Load SI CL0BL1 from the block device to the Safety Island Cluster 0 Low-Latency RAM (LLRAM).
2. Release the Safety Island Cluster 0 from reset.

Control then passes to the SI CL0BL1 runtime for Safety Island Cluster 0, which boots the rest of the system and provides safety services:

1. Initiate a self test on the Primary Compute.
2. Program the Primary Compute subsystems:
    1. Arm® Neoverse® CMN S3(AE) Coherent Mesh Network
    2. Arm® CoreLink™ GIC-720AE Generic Interrupt Controller
    3. Peripheral Block devices

For more information about the self test, see [BIST Primary Compute sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__bist-primary-compute-sequence).

Control then returns to the RSE BL2 boot loader, which performs its remaining tasks:

1. Load Primary Compute BL2 from the block device to the Secure SRAM in the Peripheral Block in the Primary Compute.
2. Load the RSE runtime from the block device to the RSE SRAM.
3. Program access protection units in the Arm® CoreLink™ NI-710AE Network-on-Chip Interconnect.
4. Jump to RSE runtime in RSE SRAM.

The RSE runtime is stored in the block device and provides security services.

Finally, control passes once more to the SI CL0BL1 runtime, which completes the Safety Island boot sequence:

1. Release the primary Arm® Cortex®-A720AE from reset.
2. Initialize and perform Runtime Safety Services.

For more information about the image loads, see [Secure load image sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__secure-load-image-sequence).

At the end of the Safety Island boot sequence, the RSE and the Safety Island are both in runtime mode. Two further sequences are initiated: the [verify configuration sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__verify-configuration-sequence) and the [Primary Compute boot sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__primary-compute-boot-sequence).

<a id="md234-main-boot-sequence__primary-compute-boot-sequence"></a>

### Primary Compute boot sequence

The Primary Compute boot sequence takes place in three parts. The first figure shows the Primary Compute boot phase 1 sequence that was initiated during the preceding Safety Island boot sequence.

> **Note**
>
> The Block Device Controller in the following figures might be different from the one in previous figures that describe the boot flow.

<a id="md234-main-boot-sequence__fig_boot_primary_compute_1"></a>

**Figure 6-7: Primary Compute phase 1 boot sequence**

![Primary Compute phase 1 boot sequence](assets/figure-6-7-primary-compute-phase-1-boot-sequence.png)

Primary Compute BL2 is the first-stage trusted firmware for the primary Application Processor (AP). The boot sequence proceeds like this:

1. Set up the Secure DRAM.
2. Load Primary Compute BL3_1 from the block device to the Secure SRAM in the Peripheral Block in the Primary Compute.
3. Load Primary Compute BL3_2 from the block device to the Secure DRAM.
4. Load Primary Compute BL3_3 from the block device to the Non-secure DRAM.
5. Run Primary Compute BL3_1.

The second figure shows the Primary Compute phase 2 boot sequence, which was initiated during the preceding boot sequence.

<a id="md234-main-boot-sequence__fig_boot_primary_compute_2"></a>

**Figure 6-8: Primary Compute phase 2 boot sequence**

![Primary Compute phase 2 boot sequence](assets/figure-6-8-primary-compute-phase-2-boot-sequence.png)

Primary Compute BL3_1 is the second-stage trusted firmware for APs. This part of the boot sequence proceeds like this:

1. Initialize Trusted Firmware-A services.
2. Run Primary Compute BL3_2, which is a trusted execution environment for APs:
    1. Initialize the OP-TEE environment.
    2. Initialize Secure partitions.
    3. Return to Primary Compute BL3_1.
3. Run Primary Compute BL3_3.

The third figure shows the Primary Compute phase 3 boot sequence, which was initiated during the preceding boot sequence.

<a id="md234-main-boot-sequence__fig_boot_primary_compute_3"></a>

**Figure 6-9: Primary Compute phase 3 boot sequence**

![Primary Compute phase 3 boot sequence](assets/figure-6-9-primary-compute-phase-3-boot-sequence.png)

Primary Compute BL3_3 is a boot loader for APs. It controls the final stages of the main boot sequence:

1. Check for available capsule updates.
2. If a capsule update is available:
    1. Perform the capsule update.
    2. Reset the system.
3. Check for a valid Primary Compute boot manager. If valid:
    1. Load the Primary Compute boot manager from the block device to Non-secure DRAM.
    2. Jump to the Primary Compute boot manager in Non-secure DRAM.
4. Check for a valid Primary Compute runtime, such as an optional hypervisor, an Operating System (OS), or applications. If valid:
    1. Load the Primary Compute runtime from the block device to Non-secure DRAM.
    2. Jump to the Primary Compute runtime.

<a id="md234-main-boot-sequence__secure-load-image-sequence"></a>

### Secure load image sequence

Many phases of the main boot sequence contain steps for securely loading images that control or are required in later phases. The following figure represents the sequence through which these images are loaded.

<a id="md234-main-boot-sequence__fig_secure_load_image_scenario1"></a>

**Figure 6-10: Secure load image sequence**

![Secure load image sequence](assets/figure-6-10-secure-load-image-sequence.png)

<a id="md234-main-boot-sequence__bist-rse-self-test"></a>

### BIST RSE sequence

Many phases of the [main boot sequence](06-boot-flow-of-zena-css.md#boot-flow-of-zena-css-main-boot-sequence) initiate the Built-In Self Test (BIST) sequences of different parts of the system.

The following figure shows the BIST RSE sequence that was initiated during the Zena CSS system boot sequence in [System boot sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__fig_boot_scenario1).

<a id="md234-main-boot-sequence__fig_bist_rse_scenario1"></a>

**Figure 6-11: BIST RSE sequence**

![BIST RSE sequence](assets/figure-6-11-bist-rse-sequence.png)

<a id="md234-main-boot-sequence__bist-si-self-test"></a>

### BIST Safety Island sequence

Many phases of the [main boot sequence](06-boot-flow-of-zena-css.md#boot-flow-of-zena-css-main-boot-sequence) initiate the BIST sequences of different parts of the system.

The following figure shows the BIST Safety Island sequence that was initiated during the RSE phase 2 boot sequence in [RSE phase 2 boot sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__fig_boot_rse_2).

<a id="md234-main-boot-sequence__fig_bist_si_scenario1"></a>

**Figure 6-12: BIST Safety Island sequence**

![BIST Safety Island sequence](assets/figure-6-12-bist-safety-island-sequence.png)

<a id="md234-main-boot-sequence__bist-primary-compute-sequence"></a>

### BIST Primary Compute sequence

Many phases of the [main boot sequence](06-boot-flow-of-zena-css.md#boot-flow-of-zena-css-main-boot-sequence) initiate the BIST sequences of different parts of the system.

The following figure shows the BIST Primary Compute sequence that was initiated during the Safety Island boot sequence in [Safety Island boot sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__fig_boot_safety_island).

<a id="md234-main-boot-sequence__fig_bist_pc_scenario1"></a>

**Figure 6-13: BIST Primary Compute sequence**

![BIST Primary Compute sequence](assets/figure-6-13-bist-primary-compute-sequence.png)

<a id="md234-main-boot-sequence__verify-configuration-sequence"></a>

### Verify configuration sequence

At the end of the Safety Island boot sequence, the verify configuration sequence is initiated to ensure that the Safety Island is correctly configured and ready for operation.

The following figure shows the sequence that was started in [Safety Island boot sequence](06-boot-flow-of-zena-css.md#md234-main-boot-sequence__fig_boot_safety_island).

<a id="md234-main-boot-sequence__fig_verify_configuration"></a>

**Figure 6-14: Verify configuration sequence**

![Verify configuration sequence](assets/figure-6-14-verify-configuration-sequence.png)

<a id="boot-flow-of-zena-css-selecting-and-updating-firmware-images"></a>

## 6.2 Selecting and updating firmware images

The boot sequence expects an A+B model, where there are always two independent sets of firmware images available to the system. The `whichImageSet` variable stored in Secure, non-volatile memory determines which set to use.

If authentication for any image in the selected firmware image set fails, the system must indicate a non-critical fault and fall back to the alternate image set.

If authentication for any image in the alternate firmware image set also fails, the system must indicate a critical fault and not continue.

To update the firmware, leave the current set of images intact, but update every image in the alternate set. Then, update the `whichImageSet` variable atomically to point to the updated set of images. Finally, reset the system to trigger the use of the new images.

If anti-rollback measures are required, you must replace the remaining old set of images with the new set after successfully booting with the new images.
