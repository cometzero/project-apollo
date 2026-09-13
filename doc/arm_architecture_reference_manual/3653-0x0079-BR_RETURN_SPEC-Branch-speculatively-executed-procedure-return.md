# ​0x0079, BR_RETURN_SPEC, Branch speculatively executed, procedure return

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0079--BR-RETURN-SPEC--Branch-speculatively-executed--procedure-return>

##### `0x0079`, BR\_RETURN\_SPEC, Branch speculatively executed, procedure return

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) procedure return instruction.

Operations due to the following instructions are counted as [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) procedure return instructions:

- For AArch32 state, the following instructions:
  - `BX R14`.
  - `MOV PC, LR`.
  - `POP {..., PC}`.
  - `LDR PC, [SP], #offset`.
- For AArch64 state, the following instructions:
  - `RET`.
  - If FEAT\_PAuth is implemented, `RETAA` and `RETAB`.
  - If FEAT\_PAuth\_LR is implemented, `RETAASPPC`, `RETABSPPC`, `RETAASPPCR`, and `RETABSPPCR`.

> #### Note
>
> The counter counts only the listed instructions as procedure returns. For example, it does not count the following AArch32 instructions as procedure return instructions:
>
> - `BX R0`, because Rm != R14.
> - `MOV PC, R0`, because Rm != R14.
> - `LDM SP, {..., PC}`, because writeback is not specified.
> - `LDR PC, [SP, #offset]`, because this specifies the wrong addressing mode.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
