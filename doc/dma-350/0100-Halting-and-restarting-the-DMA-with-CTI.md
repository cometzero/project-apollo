# Halting and restarting the DMA with CTI

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Halting-and-restarting-the-DMA-with-CTI>

### Halting and restarting the DMA with CTI

The DMA-350 can be halted for debug purposes using the CTI interface.

When a HIGH is received on the CTI halt\_req signal, pausing of both the Secure and Non-secure channels is initiated.

When all the channels reach either paused or not enabled state after a halt request, a pulse on the halted CTI signal is sent. After the DMAC reaches the paused state, it waits for a HIGH on the restart\_req CTI signal. When it is received, the DMA channels return to their state before the halt request.

The CTI halt request and restart request are ignored in certain cases:

- The halt\_req is ignored after a previous halt request and before the DMAC returns to normal operation.
- The restart request is ignored before a halt request is received. After a valid HIGH is received on the restart\_req, further level changes are ignored.

The halt request from the CTI is combined with the hardware pause, allch\_pause\_req, and the software initiated allchpause. The DMA channels can be paused using any of the three methods.
