# Setting a PMU counter

Source: <https://developer.arm.com/documentation/102666/0201/Getting-started-with-GIC-720AE/Setting-a-PMU-counter>

### Setting a PMU counter

Use the following procedure to configure a counter.

### About this task

> ### Note
>
> PMU registers, other than enables, do not have defined reset values and must be programmed before use.

### Procedure

1. Program the counter [GICP\_EVCNTRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVCNTRn--Event-Counter-Registers?lang=en "These registers contain the values of event counter n. The GIC-720AE supports five counters, n = 0-4.") to a known value. This value could be 0 to count events, or a higher number to trigger an overflow after a known number of events.
2. Program the associated [GICP\_EVTYPERn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-EVTYPERn--Event-Type-Configuration-Registers?lang=en "These registers configure which events that event counter n counts. The GIC-720AE supports five counters, n = 0-4.") to count the required event.
3. Program the required filter type for the event by programming [GICP\_FRn](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-FRn--Filter-Registers?lang=en "These registers configure the filtering of event counter n. The GIC-720AE supports five counters, n = 0-4.").
4. Enable the counter by programming the corresponding bit in [GICP\_CNTENSET0](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CNTENSET0--Counter-Enable-Set-Register-0?lang=en "These registers contain the counter enables for each event counter. The GIC-720AE supports five event counters.").
5. Repeat the previous steps for all counters that are required.
6. Enable the global count enable in [GICP\_CR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/GICP-register-summary/GICP-CR--Control-Register?lang=en "This register controls whether all counters are enabled or disabled.").E.
