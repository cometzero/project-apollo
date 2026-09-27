# System timer programmers model

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-timer-programmers-model>

### System timer programmers model

The registers of the System Timer are grouped into a single 4KB block that is called the CNTBase frame. The base address of the CNTBase frame is not defined here and is IMPLEMENTATION DEFINED.

- **[CNTBase Registers Summary](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTBase-Registers-Summary?lang=en)**
   This section provides a summary of the CNTBase Registers.
- **[Register descriptions](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/Register-descriptions?lang=en)**
   This section describes each of the System Timer registers.
- **[CNTPCT, Counter-timer Physical Count register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTPCT--Counter-timer-Physical-Count-register?lang=en)**
   The CNTPCT register holds the 64‑bit physical count value. The following table shows the bit assignments.
- **[CNTFRQ, Counter-timer Frequency register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTFRQ--Counter-timer-Frequency-register?lang=en)**
   The CNTFRQ register is provided so that software can discover the frequency of the system counter. The instance of this register in the CNTCTLBase frame must be programmed with this value as part of system initialization. Hardware does not interpret the value of the register.
- **[CNTP\_CVAL, Counter-timer Physical Timer CompareValue register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CVAL--Counter-timer-Physical-Timer-CompareValue-register?lang=en)**
   The CNTP\_CVAL register holds the 64‑bit compare value for the timer. The following table shows the bit assignments.
- **[CNTP\_TVAL, Counter-timer Physical Timer TimerValue register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-TVAL--Counter-timer-Physical-Timer-TimerValue-register?lang=en)**
   The CNTP\_TVAL register holds the timer value for the timer. The following table shows the bit assignments.
- **[CNTP\_CTL, Counter-timer Physical Timer Control register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CTL--Counter-timer-Physical-Timer-Control-register?lang=en)**
   The CNTP\_CTL register is a control register for the timer. The following table shows the bit assignments.
- **[CNTP\_AIVAL, AutoIncrValue register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL--AutoIncrValue-register?lang=en)**
   The CNTP\_AIVAL register holds the 64‑bit Automatic Increment value for the timer. The following table shows the bit assignments.
- **[CNTP\_AIVAL\_RELOAD, AutoIncrValue Reload register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL-RELOAD--AutoIncrValue-Reload-register?lang=en)**
   Holds the programmable offset value for the Automatic Increment timer view. The following table shows the bit assignments.
- **[CNTP\_AIVAL\_CTL, AutoIncrValue Control register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL-CTL--AutoIncrValue-Control-register?lang=en)**
   Control register for the Automatic Increment timer view. The following table shows the bit assignments.
- **[CNTP\_CFG, Configuration register](/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CFG--Configuration-register?lang=en)**
   Provides timer configuration information.
