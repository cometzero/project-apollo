# Clock Control Q-Channel Control interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Clock-Control-Q-Channel-Control-interfaces>

### Clock Control Q-Channel Control interfaces

Each Q-Channel Control interface in this section is single bit per signal on the Q-Channel interface and independently allows the system to request for the availability of a clock source. Each Q-Channel Control interface allows an external clock controller to handshake with the system to safely turn the clock source OFF.

Each of the clock control Q-Channel interfaces can be either asynchronous or synchronous to the clock that each of the Q-Channel interfaces control. The choice is IMPLEMENTATION DEFINED.

CRSAS Ma1 has the following clock control Q-Channel Control interfaces:

- AONCLK Q-Channel Control interface for AONCLK.
- SYSCLK Q-Channel Control interface for SYSCLK.
- CPU<n>CLK Q-Channel Control interface for CPU<n>CLK.
- NPU<m>CLK Q-Channel Control interface for NPU<m>CLK.
- DEBUGCLK Q-Channel Control interface for DEBUGCLK. This interface must exist if HASCSS = 1.

If an input clock source is always running, and there is no clock controller associated with this clock input, then you can tie its associated clock control Q-Channel Control interface by tying QREQn input to HIGH. These interfaces are in the PD\_AON domain.
