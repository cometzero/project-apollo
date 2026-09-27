# Controlling PD_CPU<n>EPU power states

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/BR-CPU-n--power-modes/Controlling-PD-CPU-n-EPU-power-states>

### Controlling PD\_CPU<n>EPU power states

Other than WARM\_RST state, the BR\_CPU<n> bounded region provides the ability for the PD\_CPU<n>EPU to enter a lower power state independently as long as the PD\_CPU<n> is ON. To control if the PD\_CPU<n>EPU can remain ON or be allowed to enter the Retention (RET) or OFF state, software can use the register CPDLPSTATE.ELPSTATE in conjunction with the CPPWR.SU10 in the CPU as follows:

RET
:   To allow the PD\_CPU<n>EPU to enter Retention (RET) state where BR\_CPU<n> never enters EPU\_OFF, LOGIC\_RET EPU\_OFF\_NOCACHE, LOGIC\_RET\_NOCACHE, MEM\_RET, MEM\_RET\_NOCACHE and OFF states, set either:

    - CPDLPSTATE.ELPSTATE to RET, 0b10, or
    - CPDLPSTATE.ELPSTATE to OFF, 0b11 and CPPWR.SU10 to 0b0.

    Retention is only entered when CPU<n> is sleeping using WFI or WFE.

OFF
:   To allow the PD\_CPU<n>EPU to enter OFF state where BR\_CPU<n> never requests FUNC\_RET, FUNC\_RET\_NOCACHE, FULL\_RET\_NOCACHE, and FULL\_RET states set:

    - CPDLPSTATE.ELPSTATE to OFF, 0b11, CPPWR.SU10 to 0b1.

ON
:   To keep the PD\_CPU<n>EPU in ON or context retained state where BR\_CPU<n> never requests EPU\_OFF, LOGIC\_RET EPU\_OFF\_NOCACHE, LOGIC\_RET\_NOCACHE, MEM\_RET, MEM\_RET\_NOCACHE, FUNC\_RET, FUNC\_RET\_NOCACHE and OFF states, set:

    - CPDLPSTATE.ELPSTATE to ON, which is 0b00 or 0b01.

> ### Note
>
> Depending on the processor core and the system implementation, other conditions may be required to reach the desired state. For more information on these conditions see the power control of the processors in, Arm® Cortex®-M55 Processor Technical Reference Manual, Arm® Cortex®-M55 Processor Integration and Implementation Manual, and Arm® Cortex®-M85 Processor Integration and Implementation Manual. For more information on CPPWR, see Arm®v8-M Architecture Reference Manual.
