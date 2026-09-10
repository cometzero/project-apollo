# Trigger Interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Trigger-Interface>

### Trigger Interface

The Trigger Interfaces can be used to control the interaction of the DMA channel operation with other peripherals.

An external peripheral or device can control the execution of DMA commands through the trigger input interface. The DMAC can also control external peripherals through its trigger output interface.

The trigger input and trigger output interfaces are compatible with each other. Because of this compatibility, it is also possible to connect two DMA channels together internally, inside the DMAC or by chaining multiple DMA controllers together.

In addition to the hardware Trigger Interfaces, software Trigger Interfaces are provided through channel control registers that enable the software to interact with triggering.

- **[Trigger input interface](/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-input-interface?lang=en)**
   The trigger input interface can synchronize the operation of a DMA command and a peripheral. The peripheral can signal the DMA-350 when a command or part of a command can be started.
- **[Trigger input interface signals](/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-input-interface-signals?lang=en)**
   When the req signal is pulled HIGH by the peripheral, it signals that the DMAC can start its command or part of its command. The DMAC acknowledges the receipt of the req by asserting the ack HIGH.
- **[Trigger output interface](/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-output-interface?lang=en)**
   The trigger output interface can signal a connected peripheral that DMA-350 finished a command.
- **[Trigger output interface signals](/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-output-interface-signals?lang=en)**
   The DMA-350 signals to the external peripheral that a command reached its final state by pulling req signal HIGH. The peripheral must acknowledge receiving this information by pulling the ack signal HIGH. The execution of the DMA command is not completed until this acknowledge is received, which gives a synchronization point between the DMA-350 and the peripheral.
