# Controlling PD_SYS Power States

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-SYS-power-modes/Controlling-PD-SYS-Power-States>

### Controlling PD\_SYS Power States

Other than WARM\_RST state, the BR\_SYS bounded region provides the ability for the PD\_CPU0EPU to enter a lower power state independently as long as the PD\_SYS is ON. To control if the PD\_CPU0EPU can remain ON or be allowed to enter the Retention (RET) or OFF state, software can use the register CPDLPSTATE.ELPSTATE in conjunction with the CPPWR.SU10 in the CPU as follows:

RET
:   To allow the PD\_CPU0EPU to enter Retention (RET) state where BR\_SYS never enters EPU\_OFF, LOGIC\_RET EPU\_OFF\_NOCACHE, LOGIC\_RET\_NOCACHE, MEM\_RET, MEM\_RET\_NOCACHE and OFF states, set either:

    - CPDLPSTATE.ELPSTATE to RET, 0b10, or
    - CPDLPSTATE.ELPSTATE to OFF, 0b11 and CPPWR.SU10 to 0b0.

    Retention is only entered when CPU<n> is sleeping using WFI or WFE.

OFF
:   To allow the PD\_CPU0EPU to enter OFF state where BR\_SYS never requests FUNC\_RET, FUNC\_RET\_NOCACHE, FULL\_RET\_NOCACHE, and FULL\_RET states set:

    - CPDLPSTATE.ELPSTATE to OFF, 0b11, CPPWR.SU10 to 0b1.

ON
:   To keep the PD\_CPU0EPU in ON or context retained state where BR\_SYS never requests EPU\_OFF, LOGIC\_RET EPU\_OFF\_NOCACHE, LOGIC\_RET\_NOCACHE, MEM\_RET, MEM\_RET\_NOCACHE, FUNC\_RET, FUNC\_RET\_NOCACHE and OFF states, set:

    - CPDLPSTATE.ELPSTATE to ON, which is 0b00 or 0b01.

> ### Note
>
> Depending on the processor core and the system implementation, other conditions may be required to reach the desired state. For more information on these conditions see the power control of the processors in, Arm® Cortex®-M55 Processor Technical Reference Manual, Arm® Cortex®-M55 Processor Integration and Implementation Manual, and Arm® Cortex®-M85 Processor Integration and Implementation Manual. For more information on CPPWR, see Arm®v8-M Architecture Reference Manual.

For the system to then enter a lower power state, the CPU must enter WFI DeepSleep state. In CRSAS Ma1, DeepSleep always uses a WIC. EWIC of the CPU always exists and resides in the PD\_AON domain. Depending on HASCPU0IWIC:

- If HASCPU0IWIC is set to 0b0, then Internal WIC does not exist and the EWIC is always used for CPU<n>.
- If HASCPU0IWIC is set to 0b1, then Internal WIC also exists, and the choice of which WIC to use is a software choice through CPUPWRCFG.USEIWIC. See [CPUPWRCFG](/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block/CPUPWRCFG?lang=en "The CPUPWRCFG register provides the local CPU software control registers for power control.").

Any Internal WIC that exists resides in the PD\_SYS power domain.

The following shows the types of power states that the system and therefore the CPU in CRSAS Ma1 supports from a programmer’s point of view, and how to enter each.

OFF - DeepSleep state
:   Allows PD\_SYS to turn off but utilizes interrupts through the external WIC to wake the system. To enter this state, the CPU must select to use the External WIC through the CPUPWRCFG.USEIWIC register, set the CPU0’s CPDLPSTATE.CLPSTATE to OFF and enable DeepSleep, before entering WFI. Note that if Internal WIC is selected PD\_CPU<n> is not able to turn oﬀ and remains ON.

RET - DeepSleep state
:   Allows PD\_SYS to enter retention state and utilizes interrupts through the external WIC to wake the system. To enter this state, the CPU must select to use the External WIC through the CPUPWRCFG.USEIWIC register, set CPDLPSTATE.CLPSTATE to RET and enable DeepSleep, before entering WFI. Note that if Internal WIC is selected instead, the PD\_SYS is not able to enter retention and remains ON.

ON - DeepSleep state
:   Allows the PD\_SYS to stay ON, with the CPU in a sleep that is only stopping the CPU clock internally, including to the NVIC. It can use either the External or Internal WIC to wake the CPU. To enter this state, the CPU must set CPDLPSTATE.CLPSTATE to
    0b01, ON, enable DeepSleep before entering WFI. Selection of External or Internal WIC can be performed using the CPUPWRCFG.USEIWIC register prior to entering WFI.

ON - Sleep state
:   Allows the PD\_SYS to stay ON, with the CPU in a sleep state that keeps its NVIC clocking and running, but with the rest of the CPU core clock turned off. To enter this state, the CPU must not enable DeepSleep or set CPDLPSTATE.CLPSTATE to ON,
    0b00 before entering WFI or WFE.

ON state
:   The PD\_SYS and the CPU’s normal running state. In this state, the EPU and the RAMs in the CPU have a degree of separate control as detailed in the previous sections.
