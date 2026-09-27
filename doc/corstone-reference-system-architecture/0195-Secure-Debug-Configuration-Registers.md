# Secure Debug Configuration Registers

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers>

###

The Secure Debug Configuration Registers are used to select the source value for the Secure Debug Authentication, DBGEN, NIDEN, SPIDEN, SPNIDEN, DAPACCEN, and Debug Access Controls, DAPDSSACCEN, SYSDSSACCENX, and SYSDSSACCEN<n>. For each signal and just one for all SYSDSSACCEN<n> and SYSDSSACCENX, a selector is provided to select between an internal register value and the value on the boundary of the subsystem.

Secure software can set or clear the internal register and selector values by setting the associated bit in the SECDBGSET register or in the SECDBGCLR register respectively. Secure software can read the output values used system wide by reading the associated SECDBGSTAT register bit. Secure software can read internal register values by reading SECDBGSET, see [SECDBGSET](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSET?lang=en "Secure Debug Configuration Set Register.").

For example, the source of DBGEN value used in the system is selected by the DBGEN\_SEL where:

- If DBGEN\_SEL is LOW, the input DBGENIN signal is used to define the system wide DBGEN value.
- If DBGEN\_SEL is HIGH, the internal register value DBGEN\_I is used to define the system wide DBGEN value.

Write 1 to the SECDBGSET.DBGEN\_I\_SET register to set DBGEN\_I value to HIGH. Write 1 to SECDBGSET.DBGEN\_SEL\_SET to set DBGEN\_SEL value to HIGH.

Write 1 to the SECDBGCLR.DBGEN\_I\_CLR register to set DBGEN\_I value to LOW. Write 1 to SECDBGCLR.DBGEN\_SEL\_CLR to set DBGEN\_SEL to LOW.

Read the SECDBGSTAT.DBGEN\_STATUS register to read the output value of DBGEN. Read SECDBGSET.DBGEN\_I\_SET register to read the value of DBGEN\_I.

The DBGEN value is also made available to external expansion logic through the DBGEN output signal of the subsystem.

Selector Disable Configuration options are provided to allow each of the selector to be forced to zero, forcing the associated SEL\_STATUS field to LOW, forcing each respective debug control output to use its external value:

- DBGENSELDIS for disabling DBGEN\_SEL,
- NIDENSELDIS for disabling NIDEN\_SEL,
- SPIDENSELDIS for disabling SPIDEN\_SEL,
- SPNIDENSELDIS for disabling SPNIDEN\_SEL,
- DAPACCENSELDIS for disabling DAPACCEN\_SEL,
- DAPDSSACCENSELDIS for disabling DAPDSSACCEN\_SEL,
- SYSDSSACCENSELDIS for disabling SYSDSSACCEN\_SEL.

These can be used to disable the ability for Secure firmware to modify or override the Debug Authentication and the Debug Access Controls values, especially when CryptoCell exists (HASCRYPTO = ‘1’) in the system and the intention is to use signals derived from CRYPTODCUEN to control debug instead.

These registers are reset by nCOLDRESETAON only.

These registers reside in the PD\_AON power domain but can also reside in PD\_MGMT power domain if its states are saved and restored when entering and then leaving the lower power state, respectively. This choice is IMPLEMENTATION DEFINED.

- **[SECDBGSTAT](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSTAT?lang=en)**
   Secure Debug Configuration Status Register.
- **[SECDBGSET](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSET?lang=en)**
   Secure Debug Configuration Set Register.
- **[SECDBGCLR](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGCLR?lang=en)**
   The Secure Debug Configuration Clear Register.
