# AXI privilege information for the AXI-configured peripheral port

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/AXI-privilege-information-for-the-AXI-configured-peripheral-port>

### AXI privilege information for the AXI-configured peripheral port

AXI provides information about the privilege level of accesses on the ARPROTMP0[0] and AWPROTMP0[0] signals. This information is not available from cores within the cluster. Therefore these signals are always driven HIGH indicating that the access could be a privileged access.
