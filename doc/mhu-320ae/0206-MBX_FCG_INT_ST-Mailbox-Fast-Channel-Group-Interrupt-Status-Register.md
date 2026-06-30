# MBX_FCG_INT_ST, Mailbox Fast Channel Group Interrupt Status Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCG-INT-ST--Mailbox-Fast-Channel-Group-Interrupt-Status-Register>

### MBX\_FCG\_INT\_ST, Mailbox Fast Channel Group Interrupt Status Register

Provides the status of each Fast Channel Group Transfer interrupt

### Configurations

This register is present only when FCE is implemented and FCGI\_SPT. Otherwise, direct accesses to MBX\_FCG\_INT\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   0x0470

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_FCG\_INT\_ST bit assignments

![mhur.mbx_mbx_fcg_int_st bit assignments](images/0206-MBX_FCG_INT_ST-Mailbox-Fast-Channel-Group-Interrupt-Status-Register-img01.svg)

<table id="mhur_mbx_mbx_fcg_int_st__ambx_fcg_int_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_FCG_INT_ST bit descriptions
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d77483e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d77483e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d77483e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d77483e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FCH_GRP&lt;m&gt;_INT_ST, bit[m], where m = 31 to 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates the status of each Fast Channel Group Transfer interrupt
    </p>
    <p>
     The Fast Channels which are part of each Fast Channel Group are calculated by the following formulas.
    </p>
    <p>
     Lowest Channel in the Group = NUM_FCH/NUM_FCH_PER_FCG * m
    </p>
    <p>
     Highest Channel in the Group = (NUM_FCH/NUM_FCH_PER_FCG * m) + NUM_FCH_PER_FCG
    </p>
    <p>
     where:
    </p>
    <ul>
     <li>
      <p>
       NUM_FCH - Number of Fast Channels in the Mailbox
      </p>
     </li>
     <li>
      <p>
       NUM_FCH_PER_FCG - Number of Fast Channels per group
      </p>
     </li>
    </ul>
    <p>
     m is the Fast Channel Group number
    </p>
    <p>
     To clear the interrupt, software must clear the underlying source of the interrupt in the MBX_FCH_GRP&lt;n&gt;_INT_ST register by acknowledging the last Transfer on the FCHs of the Fast Channel Group which indicate there is an unacknowledged Transfer.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No Fast Channel Group Transfer interrupt for Fast Channel Group &lt;m&gt; or Fast Channel Group &lt;m&gt; is configured not to factor into the Mailbox Combined interrupt.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel Group Transfer interrupt for Fast Channel Group &lt;m&gt; and Fast Channel Group &lt;m&gt; is configured to factor into the Mailbox Combined interrupt.
      </p>
     </dd>
    </dl>
    <p>
     Only bits NUM_FCG-1:0 are implemented, with all unused bits being
     <span class="documents-archterm">
      RES0
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Accessibility
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d77483e271" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d77483e274" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d77483e277" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d77483e280" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.MBX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0470
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_FCG_INT_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
