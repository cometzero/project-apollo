# Ping mechanisms

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Ping-mechanisms>

### Ping mechanisms

The MHU-320AE uses a CRC ping mechanism to protect internal AXI5-Stream and ACE5-Lite connections.

The AXI5-Stream and ACE5-Lite protection supports a CRC and ping mechanism that software can enable independently.

The value of the `MSG_PROTECTION_TYPE` configuration parameter controls the protection type for these interfaces as follows:

- `none` - No protection
- `parity` - Parity protection. Only suitable for point-to-point connections.
- `crc` - CRC protection
- `parity_crc` - CRC and parity protection

If CRC protection is enabled, then a ping mechanism also runs in the background with minimal interference to “mission” traffic.

The ping mechanism is a regular check that the connection is working. Every mission packet is eventually followed by a ping packet. If a ping packet does not generate a ping acknowledge packet from the recipient, a timeout error is raised. Software can then program the ping timeout value in the FMU\_TIMEOUT register.

An 8-bit CRC checksum is used to protect against missing or extra packets, and data corruption. The MHU Sender or the MHU Receiver inserts the CRC packet into the stream.

CRC and ping packets try not to interfere with the mission traffic, so initially mission packets take higher priority. To prevent erroneous ping timeouts from occurring, then eventually the CRC and ping packets get a higher priority than a mission packet.

For more information about how to change MHU ping timeout values and how to determine the CRC error type, see the [FMU\_SMRDATA](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Page-Read-Data-Register?lang=en "Returns the Protection Mechanism page read data when FMU_SMRD or FMU_SMWR is written.") and [FMU\_SMWDATA](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Page-Write-Data-Register?lang=en "Provides the Protection Mechanism page write data when FMU_SMWR is written.") registers.

The CRC and ping mechanism adheres to the power state of the “mission” protocol, so when the bus is in low-power state, no CRC or ping packets are sent.
