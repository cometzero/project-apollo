# System counter Programmers model

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-counter-Programmers-model>

### System counter Programmers model

This section describes programmers model for the System Counter. Registers in the System Counter provide the following functions:

- Enabling and disabling the counter.
- Setting the counter value.
- Changing the operating mode, to change the frequency and increment value.
- Enabling Halt‑on‑debug, that a debugger can then use to suspend counting.
- Providing status of the Counter value in addition to the operating mode.

These registers are grouped into two 4KB frames:

- A control frame, CNTControlBase.
- A status frame, CNTReadBase.

The base addresses of these frames are IMPLEMENTATION DEFINED. Similarly, the security level of each frame is also IMPLEMENTATION DEFINED, however, in a system that supports both, Secure and Non-secure memory maps, CNTControlBase is only accessible by Secure memory accesses.

- **[CNTControlBase registers summary](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTControlBase-registers-summary?lang=en)**
   This section provides a summary of the CNTControlBase Frame Registers (System Counter).
- **[CNTReadBase registers summary](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTReadBase-registers-summary?lang=en)**
   This section provides a summary of the CNTReadBase registers.
- **[Register descriptions](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/Register-descriptions?lang=en)**
   This section describes each System Counter register.
- **[CNTCR, Counter Control register](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTCR--Counter-Control-register?lang=en)**
   The CNTCR register enables the counter, controls the counter frequency setting, and controls counter behavior during debug.
- **[CNTSR, Counter Status register](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTSR--Counter-Status-register?lang=en)**
   The CNTSR register provides Counter frequency status information. The following table shows the bit assignments.
- **[CNTCV, Counter Count Value register](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTCV--Counter-Count-Value-register?lang=en)**
   The CNTCV register indicates the current count value. The following table shows the bit assignments.
- **[CNTSCR, Counter Scale register](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTSCR--Counter-Scale-register?lang=en)**
   The CNTSCR registers store the Counter Scaling value. The following table shows the bit assignments.
- **[CNTID, Counter ID register](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTID--Counter-ID-register?lang=en)**
   The CNTID register indicates additional information about Counter Scaling implementation. The following table shows the bit assignments.
- **[CNTSCR0, CNTSCR1, Counter Scaling registers](/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTSCR0--CNTSCR1--Counter-Scaling-registers?lang=en)**
   The CNTSCR0 and CNTSCR1 registers have the same field definitions as the CNTSCR register. These two extra registers are used to preprogram the scaling values so that when hardware‑based clock switching is implemented there is no need to program the scaling increment value each time when clock is switched.
