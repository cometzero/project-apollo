# Trigger output interface signals

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-output-interface-signals>

### Trigger output interface signals

The DMA-350 signals to the external peripheral that a command reached its final state by pulling req signal HIGH. The peripheral must acknowledge receiving this information by pulling the ack signal HIGH. The execution of the DMA command is not completed until this acknowledge is received, which gives a synchronization point between the DMA-350 and the peripheral.
