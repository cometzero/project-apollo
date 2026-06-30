# MBX_FCG_INT_EN, Mailbox Fast Channel Group Interrupt Enable Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCG-INT-EN--Mailbox-Fast-Channel-Group-Interrupt-Enable-Register>

### MBX\_FCG\_INT\_EN, Mailbox Fast Channel Group Interrupt Enable Register

Controls whether a Fast Channel Group contributes to the Mailbox Combined interrupt

### Configurations

This register is present only when FCE is implemented and FCGI\_SPT. Otherwise, direct accesses to MBX\_FCG\_INT\_EN are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   0x0144

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_FCG\_INT\_EN bit assignments

![mhur.mbx_mbx_fcg_int_en bit assignments](images/0203-MBX_FCG_INT_EN-Mailbox-Fast-Channel-Group-Interrupt-Enable-Register-img01.svg)

<table id="mhur_mbx_mbx_fcg_int_en__ambx_fcg_int_en-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_FCG_INT_EN bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d15973e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15973e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15973e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d15973e163" rowspan="1">
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
    MBX_COMB_EN&lt;m&gt;, bit[m], where m = 31 to 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel Group &lt;m&gt; does not contribute to the Mailbox Combined interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel Group &lt;m&gt; contributes to the Mailbox Combined interrupt
      </p>
     </dd>
    </dl>
    <p>
     The field is only implemented, if the associated Fast Channel Group is implemented. Fields which are not implemented are
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xFFFFFFFF
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
   <th class="documents-nocellnorowborder" colspan="1" id="d15973e256" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15973e259" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15973e262" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d15973e265" rowspan="1">
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
    0x0144
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_FCG_INT_EN
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
