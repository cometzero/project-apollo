# DMASECCFG summary

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-summary/DMASECCFG-summary>

### DMASECCFG summary

DMA Unit Security Configuration Register Frame.

This block contains the configuration registers for the security related behavior of the DMAC. The security configuration is recommended to be defined before the operation of the DMAC and caution must be taken if the configuration is changed during runtime. This register frame can be accessed by Secure privileged accesses only.

The following global constraints apply to all registers in this block:

- Unprivileged accesses result in RAZ/WI response.
- Non-secure accesses result in RAZ/WI or error response depending on the security configuration of the DMAC.
- Base address: 0x0000
- Size: 0x0100
- Instances: 1

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DMASECCFG register summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d69161e116" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69161e120" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69161e124" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69161e128" rowspan="1">
    <p>
     Default
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69161e132" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d69161e137" rowspan="1">
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
     SCFG_CHSEC0
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CHSEC0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CHSEC0?lang=en" title="The Secure Configuration Channel Security Mapping register is used to define the security attribute of each channel from Channel 0 to NUM_CHANNELS - 1.">
      SCFG_CHSEC0
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
     SCFG_TRIGINSEC0
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGINSEC0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGINSEC0?lang=en" title="The Secure Configuration Trigger Input Security Mapping register 0 is used to define the security attribute of each trigger input.">
      SCFG_TRIGINSEC0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x28
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SCFG_TRIGOUTSEC0
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGOUTSEC0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGOUTSEC0?lang=en" title="The Secure Configuration Trigger Output Security Mapping register 0 is used to define the security attribute of each trigger output.">
      SCFG_TRIGOUTSEC0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SCFG_CTRL
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CTRL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-CTRL?lang=en" title="The Secure Configuration Control register defines the behavior of the DMAC when security violation occurs and also allows the security configuration to be locked until the next reset.">
      SCFG_CTRL
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x44
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SCFG_INTRSTATUS
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
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-INTRSTATUS?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-INTRSTATUS?lang=en" title="The Secure Configuration Interrupt Status register shows the interrupt status for security access violations.">
      SCFG_INTRSTATUS
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
