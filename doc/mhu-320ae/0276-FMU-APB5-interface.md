# FMU APB5 interface

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/FMU-APB5-interface>

### FMU APB5 interface

The programmer view registers inside the FMU are accessible through an APB5 interface that is protected with AMBA parity extensions.

The APB5 completer interface width is 32 bits. Some of the FMU registers are 64 bits wide, so two 32-bit APB accesses, in any order, are necessary for reads or writes of those registers.

The APB5 port allows only Secure access to the FMU. To implement this access restriction, the pprot[1] signal is checked during an access. If the access fails the security check, the MHU-320AE does not use the pslverr signal to indicate this error condition, the pslverr signal remains LOW.
