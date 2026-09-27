# Clock control Q-Channel device interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Clock-control-Q-Channel-device-interfaces>

### Clock control Q-Channel device interfaces

CRSAS Ma1 defines a Q-Channel Device interface for each of the output clocks to allow expansion logic to control the availability of each clock output. These are used to support high-level clock gating. Each interface can either be single bit or a vector, and is IMPLEMENTATION DEFINED.

The following Q-Channels are provided:

- MGMTSYSCLK Q-Channel Device interface for MGMTSYSCLK. This interface resides in the PD\_MGMT power domain when PILEVEL = 2, or in the PD\_AON domain when PILEVEL < 2.
- SYSSYSCLK Q-Channel Device interface for SYSSYSCLK. This interface resides in the PD\_SYS power domain.
- DEBUGDEBUGCLK Q-Channel Device interface for DEBUGDEBUGCLK. This interface must exist when HASCSS = 1. This interface resides in the PD\_DEBUG power domain.
- CPUCPU<n>CLK Q-Channel Device interface for CPUCPU<n>CLK. This interface resides in the PD\_CPU<n> power domain when PILEVEL > 0, or in the PD\_SYS power domain when PILEVEL = 0.
- DEBUGCPU<n>CLK Q-Channel Device interface for DEBUGCPU<n>CLK. This interface must exist when HASCSS = 0. This interface resides in the PD\_DEBUG power domain.
- CRYPTOSYSCLK Q-Channel Device interface for CRYPTOSYSCLK. This interface must exist when HASCRYPTO = 1. This interface resides in the PD\_CRYPTO power domain.

All clock Q-Channel Device interfaces are for clock control only and do not support waking the system from hibernation.

Each of the Clock Control Device Q-Channel interfaces can be multi-bit and are either an asynchronous interface or synchronous to the clock that each of the Q-Channel interfaces control. The choice is IMPLEMENTATION DEFINED.
