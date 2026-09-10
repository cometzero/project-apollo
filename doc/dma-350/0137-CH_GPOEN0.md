# CH_GPOEN0

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOEN0>

### CH\_GPOEN0

The Channel GPO Driving Enable register 0 enables which GPO ports are enabled to change at the beginning of current DMA command. GPO ports from bit 0 to 31 can be enabled by this register if the port is available to this channel.

The content of this register can be updated during command linking by setting bit[22] in the command link header.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x058

Type
:   RW

Default
:   0x00000000

### Usage constraints

Becomes read-only after ENABLECMD is set.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CH_GPOEN0 register bit descriptions
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d30041e129" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30041e133" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30041e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30041e141" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d30041e145" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [31:0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     GPOEN0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Channel General Purpose Output (GPO) bit 0 to 31 enable mask. If bit n is &lsquo;1&rsquo;, then GPO[n] is selected for driving by GPOVAL0[n]. If bit &lsquo;n&rsquo; is &lsquo;0&rsquo;, then GPO[n] keeps its previous value. Only [GPO_WIDTH-1:0] are implemented. All unimplemented bits are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: (CH_GPO_EN * GPO_WIDTH) &gt; 0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
