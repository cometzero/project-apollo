# ​0x811F, BRB_FILTRATE, Branch Record captured

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811F--BRB-FILTRATE--Branch-Record-captured>

##### `0x811F`, BRB\_FILTRATE, Branch Record captured

The counter counts each valid Branch record captured in the branch record buffer.

Branch records that are not captured because they are removed by filtering are not counted.

When [BRB\_FILTRATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811F--BRB-FILTRATE--Branch-Record-captured?lang=en#event_brb_filtrate) is generated for an exception or an exception return, it is an Exception-related event.

It is CONSTRAINED UNPREDICTABLE whether the counter counts Branch records injected by a BRB INJ instruction.

If counting this event causes unsigned overflow of the event counter counting the event and this in turn causes a BRBE freeze event then:

- The Branch record for the operation that generated the event will be generated and captured in the Branch record buffer.
- It is CONSTRAINED UNPREDICTABLE whether the Branch Record Buffer Extension generates Branch records for other operations in program order after the operation that generated the event that would otherwise be generated when generation of Branch records is not Paused.

Arm recommends that implementations minimize capture of additional branches.
