# APB4 PWAKEUP

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/APB4-subordinate-interface/APB4-PWAKEUP>

### APB4 PWAKEUP

The APB4 interface is extended with a clock wakeup signaling through the pwakeup port. This allows faster clock request mechanism when the pwakeup is generated from a registered source.

This signal is used to indicate that there is ongoing activity that is associated with the APB4 interface. If the signal is not part of the APB4 interface, the psel signal can be registered to generate the pwakeup signal.
