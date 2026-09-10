# NSEC_STATUSPTR

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-STATUSPTR>

### NSEC\_STATUSPTR

The Non-secure Unit Status Pointer register can set a pointer to an internal status register that can show the global state of the Non-secure channels.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMANSECCTRL

Offset
:   0x0F0

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
   NSEC_STATUSPTR register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d57838e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57838e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57838e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57838e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d57838e142" rowspan="1">
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
     NSECSTATUSPTR
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Non-secure DMA Unit status pointer used to select which status value to view using STATUSVALUE register.
    </p>
    <p>
     Pointer values are:
    </p>
    <ul>
     <li>
      <p>
       0: Channel Enabled Status for channel numbers [31:0].
      </p>
     </li>
     <li>
      <p>
       1: Reserved
      </p>
     </li>
     <li>
      <p>
       2: Channel Stopped Status for channel numbers [31:0].
      </p>
     </li>
     <li>
      <p>
       3: Reserved
      </p>
     </li>
     <li>
      <p>
       4: Channel Paused Status for channel numbers [31:0].
      </p>
     </li>
     <li>
      <p>
       Others: Reserved.
      </p>
     </li>
    </ul>
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
