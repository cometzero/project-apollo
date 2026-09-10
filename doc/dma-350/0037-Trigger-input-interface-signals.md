# Trigger input interface signals

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-input-interface-signals>

### Trigger input interface signals

When the req signal is pulled HIGH by the peripheral, it signals that the DMAC can start its command or part of its command. The DMAC acknowledges the receipt of the req by asserting the ack HIGH.

There are additional qualifier signals accompanying both the req and ack signals. These signals give additional information to the receiving entity.

Using the reqtype[1:0] signals, the peripheral can supply more detailed information to the DMA-350. The DMAC uses the acktype[1:0] signals to give the peripheral more information along with the ack.
