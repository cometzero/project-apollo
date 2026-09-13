# Activity monitors access

Source: <https://developer.arm.com/documentation/107721/0001/Activity-Monitors-Extension-support/Activity-monitors-access>

### Activity monitors access

The DynamIQ™ Shared Unit-120AE supports memory-mapped access to activity monitors from the utility bus interface.

The base address for the cluster Activity Monitor Unit (AMU) registers on the utility bus interface is 0x040000. These registers are accessed from Secure state.

These registers are treated as RAZ/WI if either:

- The register is marked as Reserved.
- The register is accessed in the wrong Security state.
- The cluster is powered down.

See the [Arm® Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487/latest/) for information on the memory mapping of these registers.
