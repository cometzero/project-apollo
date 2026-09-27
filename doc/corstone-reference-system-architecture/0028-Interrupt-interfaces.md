# Interrupt interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Interrupt-interfaces>

### Interrupt interfaces

CRSAS Ma1 includes interrupt signals for use by the subsystem expansion. These connect to the interrupt controller of each CPU within the system and optionally to an External Wakeup Controller (EWIC) associated with the CPU or the Internal Wakeup Interrupt Controller (IWIC) of the CPU.

Signal name
:   CPU<n>EXPIRQ[CPU<n>EXPNUMIRQ-1:0]

Width
:   CPU<n>EXPNUMIRQ

Direction
:   Input

Description
:   These are Interrupt inputs from the subsystem expansion to the CPU<n> interrupt controller within the subsystem.

    Each CPU in the subsystem implements a configurable number of external interrupt lines and of these, 32 are reserved for internal use and the rest are made available here.

    CPU<n>EXPNUMIRQ defines the number of interrupts made available as expansion interrupts for CPU<n>.

> ### Note
>
> Each bit CPU<n>EXPIRQ[i] is ultimately connected to IRQ[32+i] of the CPU<n>’s NVIC.

Signal name
:   CPU<n>EXPNMI

Width
:   1

Direction
:   Input

Description
:   This provides a non-maskable interrupt input from the subsystem expansion to the interrupt controller of CPU<n> within the subsystem.

    This input is merged with other non-maskable interrupt sources within the subsystem before it is seen by the NVIC of the CPU core.
