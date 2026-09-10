# SEC_STATUSVAL

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-STATUSVAL>

### SEC\_STATUSVAL

The Secure Unit Status Value register shows the current value of a status register on Secure channels selected by the pointer in SEC\_STATUSPTR.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMASECCTRL

Offset
:   0x0F4

Type
:   RO

Default
:   0x00000000

### Usage constraints

There are no usage constraints apart from what is described for the block as a whole.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SEC_STATUSVAL register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d46969e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46969e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46969e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46969e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d46969e142" rowspan="1">
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
     SECSTATUSVAL
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Secure DMA Unit status value. Can be used for reading internal status values of the DMA Unit for debug purposes. Values shown here are dependent on STATUSPTR. Note that inputs are masked by security mapping before being presented here. This means that only status values mapped to Secure world are visible as non-Zero values.
    </p>
    <p>
     All unimplemented bits are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: SECEXT_PRESENT
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
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
