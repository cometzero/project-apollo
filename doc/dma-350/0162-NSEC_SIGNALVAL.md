# NSEC_SIGNALVAL

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMANSECCTRL-description/NSEC-SIGNALVAL>

### NSEC\_SIGNALVAL

The Non-secure Unit Signal Value register shows the current value of the Non-secure interfaces selected by the pointer in NSEC\_SIGNALPTR.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMANSECCTRL

Offset
:   0x0FC

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
   NSEC_SIGNALVAL register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16288e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16288e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16288e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16288e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16288e142" rowspan="1">
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
     NSECSIGNALVAL
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Non-secure DMA Unit signal status. Can be used for reading signal values of triggers and GPOs for debug. Values shown here are dependent on SIGNALPTR.
    </p>
    <p>
     Note that inputs are masked by security mapping before being presented here. This means that only signals mapped to Non-secure world are visible as non-zero values. Writing to this register has the following effect:
    </p>
    <ul>
     <li>
      <p>
       Writing &lsquo;1&rsquo; to a Non-secure Trigger Input Request that are not selected by any DMA channel causes a deny response for it. This can attempt to clear an unwanted trigger input.
      </p>
     </li>
     <li>
      <p>
       Writing &lsquo;1&rsquo; to any Trigger Output Acknowledges status, GPO status and all Trigger Input Request already selected by any DMA channel is ignored.
      </p>
     </li>
    </ul>
    <p>
     All unimplemented bits are
     <span class="documents-archterm">
      RAZWI
     </span>
     .
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     W1C
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
