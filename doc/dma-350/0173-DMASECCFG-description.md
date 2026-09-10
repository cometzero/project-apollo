# DMASECCFG description

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description>

### DMASECCFG description

DMA Unit Security Configuration Register Frame.

For an overview of the frame, and a list of constraints that apply to this block, see [DMASECCFG summary](/documentation/102482/0000/Programmers-model/Register-summary/DMASECCFG-summary?lang=en "DMA Unit Security Configuration Register Frame.").

- **[SCFG\_CHSEC0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CHSEC0?lang=en)**
   The Secure Configuration Channel Security Mapping register is used to define the security attribute of each channel from Channel 0 to NUM\_CHANNELS - 1.
- **[SCFG\_TRIGINSEC0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGINSEC0?lang=en)**
   The Secure Configuration Trigger Input Security Mapping register 0 is used to define the security attribute of each trigger input.
- **[SCFG\_TRIGOUTSEC0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGOUTSEC0?lang=en)**
   The Secure Configuration Trigger Output Security Mapping register 0 is used to define the security attribute of each trigger output.
- **[SCFG\_CTRL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CTRL?lang=en)**
   The Secure Configuration Control register defines the behavior of the DMAC when security violation occurs and also allows the security configuration to be locked until the next reset.
- **[SCFG\_INTRSTATUS](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-INTRSTATUS?lang=en)**
   The Secure Configuration Interrupt Status register shows the interrupt status for security access violations.
