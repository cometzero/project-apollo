# DMASECCTRL summary

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-summary/DMASECCTRL-summary>

### DMASECCTRL summary

DMA Unit Secure Control Register Frame.

This block contains the configuration registers for all Secure channels and other Secure resources of the DMAC. The Secure software can control and monitor the status of the channels before and during the execution of the DMA commands. Some of the registers become read-only when the ENABLECMD bit is set for the selected channel. This register frame can be accessed by Secure privileged accesses only.

The following global constraints apply to all registers in this block:

- Unprivileged accesses result in RAZ/WI response.
- Non-secure accesses result in RAZ/WI or error response depending on the security configuration of the DMAC.
- Base address: 0x0100
- Size: 0x0100
- Instances: 1

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DMASECCTRL register summary
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d70280e116" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d70280e120" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d70280e124" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d70280e128" rowspan="1">
    <p>
     Default
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d70280e132" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d70280e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_CHINTRSTATUS0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHINTRSTATUS0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHINTRSTATUS0?lang=en" title="The Secure Channel Interrupt Status register 0 shows the overall interrupt status of every Secure channel from Channel 0 to NUM_CHANNELS - 1.">
      SEC_CHINTRSTATUS0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x08
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUS?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUS?lang=en" title="The Secure Status register provides information about the overall status of the Secure channels.">
      SEC_STATUS
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_CTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CTRL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CTRL?lang=en" title="The Secure Control registers can be used to adjust the interrupt generation and general behavior of the Secure channels.">
      SEC_CTRL
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x14
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_CHPTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHPTR?lang=en" title="The Secure Channel Pointer register is used to select one channel that needs to be configured through the following registers that have SEC_CH prefix.">
      SEC_CHPTR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x18
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_CHCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-CHCFG?lang=en" title="The Secure Channel Configuration register provides configuration fields for channel attributes.">
      SEC_CHCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_STATUSPTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSPTR?lang=en" title="The Secure Unit Status Pointer register can set a pointer to an internal status register that can show the global state of the Secure channels.">
      SEC_STATUSPTR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_STATUSVAL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSVAL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSVAL?lang=en" title="The Secure Unit Status Value register shows the current value of a status register on Secure channels selected by the pointer in SEC_STATUSPTR.">
      SEC_STATUSVAL
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SEC_SIGNALPTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALPTR?lang=en" title="The Secure Unit Signal Pointer register can set a pointer to an internal register that shows the state of the Secure interfaces attached to the DMAC.">
      SEC_SIGNALPTR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFC
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SEC_SIGNALVAL
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALVAL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALVAL?lang=en" title="The Secure Unit Signal Value register shows the current value of the Secure interfaces selected by the pointer in SEC_SIGNALPTR.">
      SEC_SIGNALVAL
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
