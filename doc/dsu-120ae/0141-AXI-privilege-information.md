# AXI privilege information

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/AXI-privilege-information>

### AXI privilege information

AXI provides information about the privilege level of accesses on the ARPROTM<p>[0] and AWPROTM<p>[0] signals, where <p> is the manager port interface number. This information is not available from cores within the cluster. Therefore these signals are always driven HIGH indicating that the access could be a privileged access.
