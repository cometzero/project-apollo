# DMANSECCTRL description

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description>

### DMANSECCTRL description

DMA Unit Non-secure Control Register Frame.

For an overview of the frame, and a list of constraints that apply to this block, see [DMANSECCTRL summary](/documentation/102482/0000/Programmers-model/Register-summary/DMANSECCTRL-summary?lang=en "DMA Unit Non-secure Control Register Frame.").

- **[NSEC\_CHINTRSTATUS0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHINTRSTATUS0?lang=en)**
   The Non-Secure Channel Interrupt Status register 0 shows the overall interrupt status of every Non-secure channel from Channel 0 to NUM\_CHANNELS - 1.
- **[NSEC\_STATUS](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUS?lang=en)**
   The Non-secure Status register provides information about the overall status of the Non-secure channels.
- **[NSEC\_CTRL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CTRL?lang=en)**
   The Non-secure Control registers can be used to adjust the interrupt generation and general behavior of the Non-secure channels.
- **[NSEC\_CHPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHPTR?lang=en)**
   The Non-secure Channel Pointer register is used to select one channel that needs to be configured through the following registers through the NSEC\_CHCFG.
- **[NSEC\_CHCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHCFG?lang=en)**
   The Non-secure Channel Configuration register provides configuration fields for channel attributes for the channel selected by NSEC\_CHPTR.
- **[NSEC\_STATUSPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSPTR?lang=en)**
   The Non-secure Unit Status Pointer register can set a pointer to an internal status register that can show the global state of the Non-secure channels.
- **[NSEC\_STATUSVAL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSVAL?lang=en)**
   The Non-secure Unit Status Value register shows the current value of a status register on Non-secure channels selected by the pointer in NSEC\_STATUSPTR.
- **[NSEC\_SIGNALPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALPTR?lang=en)**
   The Non-secure Unit Signal Pointer register can set a pointer to an internal register that shows the state of the Non-secure interfaces attached to the DMAC.
- **[NSEC\_SIGNALVAL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALVAL?lang=en)**
   The Non-secure Unit Signal Value register shows the current value of the Non-secure interfaces selected by the pointer in NSEC\_SIGNALPTR.
