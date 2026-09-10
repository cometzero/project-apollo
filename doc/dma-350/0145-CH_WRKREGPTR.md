# CH_WRKREGPTR

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGPTR>

### CH\_WRKREGPTR

The Channel Working Register Pointer register can be used to select an internal work register of the DMA channel that is visible in the CH\_WRKREGVAL register.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x088

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
   CH_WRKREGPTR register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16716e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16716e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16716e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16716e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16716e142" rowspan="1">
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
     WRKREGPTR
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Internal Working Register Pointer. L- -
    </p>
    <p>
     This pointer refers to the following:
    </p>
    <ul>
     <li>
      <p>
       0: Reserved
      </p>
     </li>
     <li>
      <p>
       1: SRCADDR_INITIAL
      </p>
     </li>
     <li>
      <p>
       2: SRCADDRHI_INITIAL
      </p>
     </li>
     <li>
      <p>
       3: DESADDR_INITIAL
      </p>
     </li>
     <li>
      <p>
       4: DESADDRHI_INITIAL
      </p>
     </li>
     <li>
      <p>
       5: SRCXSIZEHI_INITIAL, SRCXSIZE_INITIAL
      </p>
     </li>
     <li>
      <p>
       6: DESXSIZEHI_INITIAL, DESXSIZE_INITIAL
      </p>
     </li>
     <li>
      <p>
       7: SRCADDR_LINEINITIAL
      </p>
     </li>
     <li>
      <p>
       8: SRCADDRHI_LINEINITIAL
      </p>
     </li>
     <li>
      <p>
       9: DESADDR_LINEINITIAL
      </p>
     </li>
     <li>
      <p>
       10: DESADDRHI_LINEINITIAL
      </p>
     </li>
     <li>
      <p>
       11: SRCYSIZE_INITIAL (HAS_2D only)
      </p>
     </li>
     <li>
      <p>
       12: DESYSIZE_INITIAL (HAS_2D only)
      </p>
     </li>
     <li>
      <p>
       Others: Reserved.
      </p>
     </li>
    </ul>
    <p>
     Note: When the selected register is not supported by the DMA then it is read as 0 in the CH_WRKREGVAL register. For 1D modes the INITIAL and LINEINITIAL registers contain the same values.
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
