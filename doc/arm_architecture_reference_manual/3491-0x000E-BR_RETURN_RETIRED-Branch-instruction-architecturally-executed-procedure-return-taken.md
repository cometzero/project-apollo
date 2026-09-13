# ​0x000E, BR_RETURN_RETIRED, Branch instruction architecturally executed, procedure return, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000E--BR-RETURN-RETIRED--Branch-instruction-architecturally-executed--procedure-return--taken>

##### `0x000E`, BR\_RETURN\_RETIRED, Branch instruction architecturally executed, procedure return, taken

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) procedure return instruction.

The following instructions are counted as procedure return instructions:

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

PMCEID0\_EL0[14] reads as 1 if this event is implemented and 0 otherwise.
