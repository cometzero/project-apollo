<a id="zena-css-software-reference-stack"></a>

# 7 Zena CSS software reference stack

The Arm Automotive Solutions Software Reference Stack models typical compute subsystems based on Arm Reference Designs for automotive use.

When used with an automotive [Fixed Virtual Platform](08-fixed-virtual-platform.md#fixed-virtual-platform) (FVP), the Zena CSS software reference stack enables early bring-up of systems based on Zena CSS. It supports booting from bare metal through to Linux aiming to align with Arm SystemReady Devicetree.

By using TF-A, U-Boot, and systemd-boot, developers can prototype platforms, validate device trees, and develop or test software before hardware is available. Supported use cases include bare-metal workloads, virtualized environments, and Linux user-space development.

For more details on how to build and run images for Arm automotive reference designs, see the [Arm® Automotive Solutions documentation](https://arm-auto-solutions.docs.arm.com/en/latest/). To download the reference software, see [Arm Zena Compute Subsystem Reference Software](https://gitlab.arm.com/automotive-and-industrial/arm-auto-solutions/sw-ref-stack).

> **Note**
>
> Refer to the [Software Reference Stack Release Notes](https://arm-auto-solutions.docs.arm.com/en/latest/releasenotes.html) for details on compatibility between reference software and FVP versions.
