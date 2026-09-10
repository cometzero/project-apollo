# DMASECCTRL description

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description>

### DMASECCTRL description

DMA Unit Secure Control Register Frame.

For an overview of the frame, and a list of constraints that apply to this block, see [DMASECCTRL summary](/documentation/102482/0000/Programmers-model/Register-summary/DMASECCTRL-summary?lang=en "DMA Unit Secure Control Register Frame.").

- **[SEC\_CHINTRSTATUS0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHINTRSTATUS0?lang=en)**
   The Secure Channel Interrupt Status register 0 shows the overall interrupt status of every Secure channel from Channel 0 to NUM\_CHANNELS - 1.
- **[SEC\_STATUS](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUS?lang=en)**
   The Secure Status register provides information about the overall status of the Secure channels.
- **[SEC\_CTRL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CTRL?lang=en)**
   The Secure Control registers can be used to adjust the interrupt generation and general behavior of the Secure channels.
- **[SEC\_CHPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHPTR?lang=en)**
   The Secure Channel Pointer register is used to select one channel that needs to be configured through the following registers that have SEC\_CH prefix.
- **[SEC\_CHCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHCFG?lang=en)**
   The Secure Channel Configuration register provides configuration fields for channel attributes.
- **[SEC\_STATUSPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSPTR?lang=en)**
   The Secure Unit Status Pointer register can set a pointer to an internal status register that can show the global state of the Secure channels.
- **[SEC\_STATUSVAL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSVAL?lang=en)**
   The Secure Unit Status Value register shows the current value of a status register on Secure channels selected by the pointer in SEC\_STATUSPTR.
- **[SEC\_SIGNALPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALPTR?lang=en)**
   The Secure Unit Signal Pointer register can set a pointer to an internal register that shows the state of the Secure interfaces attached to the DMAC.
- **[SEC\_SIGNALVAL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALVAL?lang=en)**
   The Secure Unit Signal Value register shows the current value of the Secure interfaces selected by the pointer in SEC\_SIGNALPTR.
