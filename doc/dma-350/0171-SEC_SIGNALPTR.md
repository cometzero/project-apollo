# SEC_SIGNALPTR

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCTRL-description/SEC-SIGNALPTR>

### SEC\_SIGNALPTR

The Secure Unit Signal Pointer register can set a pointer to an internal register that shows the state of the Secure interfaces attached to the DMAC.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMASECCTRL

Offset
:   0x0F8

Type
:   RW

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
   SEC_SIGNALPTR register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d40613e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d40613e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d40613e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d40613e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d40613e142" rowspan="1">
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
     [31:4]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [3:0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SECSIGNALPTR
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Secure DMA Unit signal pointer used to select which inputs to view using SIGNALVAL register.
    </p>
    <p>
     Pointer values, x, are:
    </p>
    <ul>
     <li>
      <p>
       0 to 7: Trigger Input Requests [31+32x : 32x]
      </p>
     </li>
     <li>
      <p>
       8 to 9: Trigger output Acknowledges [31+32(x-8) : 32(x-8)]
      </p>
     </li>
     <li>
      <p>
       10 to 11: GPO output value [31+32(x-10) : 32(x-10)], only present when HAS_GPOSEL is set.
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
    <p>
     The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: SECEXT_PRESENT
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
