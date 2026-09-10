# CH_DESTMPLT

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTMPLT>

### CH\_DESTMPLT

The Channel Destination Template Pattern register sets the template pattern used for writing the destination memory area.

The content of this register can be updated during command linking by setting bit[18] in the command link header.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x048

Type
:   RW

Default
:   0x00000001

### Usage constraints

Becomes read-only after ENABLECMD is set.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CH_DESTMPLT register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d4296e129" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d4296e133" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d4296e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d4296e141" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d4296e145" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [31:1]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DESTMPLT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Destination Packing Template. Bit[0] is read only and always set to 1 as template patterns can only start from the base address of the transfer. Not present when HAS_TMPLT is 0. The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: CH_EXT_FEAT_EN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     DESTMPLTLSB
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Destination Packing Template Least Significant Bit. This bit of the template is read only and always set to 1 as template patterns can only start from the base address of the transfer. Not present when HAS_TMPLT is 0. The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: CH_EXT_FEAT_EN
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     CH_EXT_FEAT_EN
    </p>
   </td>
  </tr>
 </tbody>
</table>
