# Arbitration requests

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Arbitration/Arbitration-requests>

### Arbitration requests

The channels can generate requests for arbitration when the following conditions occur.

If there are arbitration requests for read:

- Channel FSM prepared the next address to read with all control information.
- The data FIFO has enough room to store the complete read response.

If there are arbitration requests for write:

- Channel FSM prepared the next address to write with all control information.
- The data FIFO has a complete write burst to be sent out.

This means that channel writes can only start when a full burst is read into the FIFO first. This avoids having circular dependency between reads and writes because writes do not have to wait for any incoming read data.
