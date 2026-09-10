# DMANSECCTRL summary

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-summary/DMANSECCTRL-summary>

### DMANSECCTRL summary

DMA Unit Non-secure Control Register Frame.

This block contains the configuration registers for all non-secure channels and other Non-secure resources of the DMAC. The Non-secure SW can control and monitor the status of the channels before and during the execution of the DMA commands. Some of the registers become read-only when the ENABLECMD bit is set for the selected channel. This register frame can be accessed by both secure privileged and Non-secure privileged accesses.

The following global constraints apply to all registers in this block:

- Unprivileged accesses result in RAZ/WI response.
- Base address: 0x0200
- Size: 0x0100
- Instances: 1

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DMANSECCTRL register summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d67152e109" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67152e113" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67152e117" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67152e121" rowspan="1">
    <p>
     Default
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67152e125" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d67152e130" rowspan="1">
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
     NSEC_CHINTRSTATUS0
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHINTRSTATUS0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHINTRSTATUS0?lang=en" title="The Non-Secure Channel Interrupt Status register 0 shows the overall interrupt status of every Non-secure channel from Channel 0 to NUM_CHANNELS - 1.">
      NSEC_CHINTRSTATUS0
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
     NSEC_STATUS
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUS?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUS?lang=en" title="The Non-secure Status register provides information about the overall status of the Non-secure channels.">
      NSEC_STATUS
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
     NSEC_CTRL
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CTRL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CTRL?lang=en" title="The Non-secure Control registers can be used to adjust the interrupt generation and general behavior of the Non-secure channels.">
      NSEC_CTRL
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
     NSEC_CHPTR
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHPTR?lang=en" title="The Non-secure Channel Pointer register is used to select one channel that needs to be configured through the following registers through the NSEC_CHCFG.">
      NSEC_CHPTR
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
     NSEC_CHCFG
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-CHCFG?lang=en" title="The Non-secure Channel Configuration register provides configuration fields for channel attributes for the channel selected by NSEC_CHPTR.">
      NSEC_CHCFG
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
     NSEC_STATUSPTR
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSPTR?lang=en" title="The Non-secure Unit Status Pointer register can set a pointer to an internal status register that can show the global state of the Non-secure channels.">
      NSEC_STATUSPTR
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
     NSEC_STATUSVAL
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSVAL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSVAL?lang=en" title="The Non-secure Unit Status Value register shows the current value of a status register on Non-secure channels selected by the pointer in NSEC_STATUSPTR.">
      NSEC_STATUSVAL
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
     NSEC_SIGNALPTR
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALPTR?lang=en" title="The Non-secure Unit Signal Pointer register can set a pointer to an internal register that shows the state of the Non-secure interfaces attached to the DMAC.">
      NSEC_SIGNALPTR
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
     NSEC_SIGNALVAL
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALVAL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALVAL?lang=en" title="The Non-secure Unit Signal Value register shows the current value of the Non-secure interfaces selected by the pointer in NSEC_SIGNALPTR.">
      NSEC_SIGNALVAL
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
