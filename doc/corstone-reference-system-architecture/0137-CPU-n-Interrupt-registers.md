# CPU <n> Interrupt registers

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Message-Handling-Unit-register-map/CPU--n--Interrupt-registers>

### CPU <n> Interrupt registers

The CPU <n> Interrupt registers, CPU<n>INTR\_STAT, CPU<n>INTR\_SET, and CPU<n>INTR\_CLR, allow software to raise an interrupt, clear an interrupt and check the value written that is used to raise the interrupt to CPU <n>. Separate Set and Clear registers allow individual bit of the interrupt status to be set and cleared, therefore it supports SW using each bit to represent an event that can be independently set and cleared. One set of these registers exist per CPU<n>.

- **[CPU<n>INTR\_STAT](/documentation/102803/0000/Programmers-model/Peripheral-Region/Message-Handling-Unit-register-map/CPU--n--Interrupt-registers/CPU-n-INTR-STAT?lang=en)**
   CPU <n> Interrupt Status register.
- **[CPU<n>INTR\_SET](/documentation/102803/0000/Programmers-model/Peripheral-Region/Message-Handling-Unit-register-map/CPU--n--Interrupt-registers/CPU-n-INTR-SET?lang=en)**
   The CPU <n> Interrupt Set register.
- **[CPU<n>INTR\_CLR](/documentation/102803/0000/Programmers-model/Peripheral-Region/Message-Handling-Unit-register-map/CPU--n--Interrupt-registers/CPU-n-INTR-CLR?lang=en)**
   The CPU <n> Interrupt Clear register.
