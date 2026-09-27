# Controlling PD_CPU<n> power states

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes/Controlling-PD-CPU-n--power-states>

### Controlling PD\_CPU<n> power states

For the PD\_CPU<n> to enter a lower power state, software on the CPU<n> must first configure its CPDLPSTATE.CLPSTATE register to define what power state CPU<n> can enter when in a sleep state as follows:

- Set CPDLPSTATE.CLPSTATE to RET, to allow the PD\_CPU<n> to enter retention state only when in sleep state. When set to RET, BR\_CPU<n> never enters OFF, MEM\_RET\_NOCACHE, or MEM\_RET. Other modes can be entered depending on PD\_CPU<n>EPU and PD\_CPU<n>RAM domain power states.
- Set CPDLPSTATE.CLPSTATE to OFF, to allow the PD\_CPU<n> to enter OFF state only when in sleep state. When set to OFF, BR\_CPU<n> never requests LOGIC\_RET\_NOCACHE and LOGIC\_RET modes. Other modes can be entered depending on PD\_CPU<n>EPU and PD\_CPU<n>RAM domain power states, and if a coprocessor CP<i> that is included in the system is indicating that the state cannot be lost CPPWR.SU<i>=0b0.
- Set CPDLPSTATE.CLPSTATE to ON, that is, to 0b00 or 0b01 to keep PD\_CPU<n> ON even when it is in sleep mode, which in turn means that BR\_CPU<n> never enters LOGIC\_RET\_NOCACHE, LOGIC\_RET, FULL\_RET\_NOCACHE, FULL\_RET, OFF, MEM\_RET\_NOCACHE and MEM\_RET modes. Other modes can be entered depending on PD\_CPU<n>EPU and PD\_CPU<n>RAM domain power states.

> ### Note
>
> Depending on the processor core and the system implementation, other conditions may be required to reach the desired state. For more information on these conditions, see the power control of the processors in, Arm® Cortex®-M55 Processor Technical Reference Manual, Arm® Cortex®-M55 Processor Integration and Implementation Manual, and Arm® Cortex®-M85 Processor Integration and Implementation Manual. For more information on CPPWR, see Arm®v8-M Architecture Reference Manual.

For each CPU to then enter a lower power state, the CPU must enter WFI DeepSleep state. In CRSAS Ma1, DeepSleep always uses a WIC. External WIC for each CPU always exists, and all External WICs reside in the PD\_AON domain. Depending on HASCPU<n>IWIC:

- If HASCPU<n>IWIC is set to 0b0 for CPU<n>, then Internal WIC does not exist for CPU<n> and the External WIC is always used for CPU<n>.
- If HASCPU<n>IWIC is set to 0b1 for CPU<n>, then Internal WIC also exists, and the choice of which WIC to use is a software choice through CPUPWRCFG.USEIWIC. See [CPUPWRCFG](/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block/CPUPWRCFG?lang=en "The CPUPWRCFG register provides the local CPU software control registers for power control.").

Any Internal WIC that exist resides in associated PD\_CPU<n> power domain.

The following shows the types of power states that each CPU in CRSAS Ma1 supports from a programmers point of view, and how to enter each.

OFF - DeepSleep state
:   Allows the CPU to turn off but utilizes interrupts through the external WIC to wake the CPU. To enter this state, the CPU must select to use the External WIC through the CPUPWRCFG.USEIWIC register, set the CPU<n>’s CPDLPSTATE.CLPSTATE to OFF and enable DeepSleep, before entering WFI. If Internal WIC is selected PD\_CPU<n> is not able to turn oﬀ and remains ON.

RET - DeepSleep state
:   Allows the CPU to enter retention state and utilizes interrupts through the external WIC to wake the CPU. To enter this state, the CPU must select to use the External WIC through the CPUPWRCFG.USEIWIC register, set CPDLPSTATE.CLPSTATE to RET and enable DeepSleep, before entering WFI. If Internal WIC is selected instead, the PD\_CPU<n> is not able to enter retention and remains ON.

ON - DeepSleep state
:   Allows the CPU to enter a sleep state that only supports stopping the CPU clock internally, including to the NVIC. It can use either the External or Internal WIC to wake the CPU. To enter this state, the CPU must set CPDLPSTATE.CLPSTATE to
    0b01, ON, enable DeepSleep before entering WFI. Selection of External or Internal WIC can be performed using the CPUPWRCFG.USEIWIC register prior to entering WFI.

ON - Sleep state
:   Allows the CPU to enter a sleep state that still is ON, keeping its NVIC clocking and running with the rest of the core clock turned off. To enter this state, the CPU must not enable DeepSleep, or set CPDLPSTATE.CLPSTATE to ON,
    0b00, before entering WFI or WFE.

ON state
:   The CPU normal running state. Note that in this state, the EPU, and the RAMs in the CPU have a degree of separate control as detailed in
    [Controlling PD\_CPU<n>RAM power states](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes/Controlling-PD-CPU-n-RAM-power-states?lang=en "The BR_CPU<n> bounded region uses operating modes to support the ability to turn on or off the cache RAMs in modes other than the OFF mode. Power modes with cache RAMs disabled, called the NOCACHE operating modes, are suffixed with NOCACHE. Power modes with cache RAMs enabled, called the CACHE operating modes, are the modes without the NOCACHE suffix. To select the use of the NONCACHE operating modes, the following registers must be configured:") and
    [Controlling PD\_CPU<n>EPU power states](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes/Controlling-PD-CPU-n-EPU-power-states?lang=en "Other than WARM_RST state, the BR_CPU<n> bounded region provides the ability for the PD_CPU<n>EPU to enter a lower power state independently as long as the PD_CPU<n> is ON. To control if the PD_CPU<n>EPU can remain ON or be allowed to enter the Retention (RET) or OFF state, software can use the register CPDLPSTATE.ELPSTATE in conjunction with the CPPWR.SU10 in the CPU as follows:").
