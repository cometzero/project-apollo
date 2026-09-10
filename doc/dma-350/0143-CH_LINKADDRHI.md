# CH_LINKADDRHI

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDRHI>

### CH\_LINKADDRHI

The Channel Link Address Register, High Bits [63:32] sets the upper address bits of the next element in a command link.

The content of this register can be updated during command linking by setting bit[31] in the command link header.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x07C

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
   CH_LINKADDRHI register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d32956e129" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32956e133" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32956e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32956e141" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d32956e145" rowspan="1">
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
     LINKADDRHI
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Link Address Pointer [63:32]. Allows 64-bit addressing but the system might need less address bits. Limited by ADDR_WIDTH and the not implemented bits remain reserved. The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: ADDR_WIDTH &gt; 32
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
