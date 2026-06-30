# MBX_FCH_GRP<n>_INT_ST, Mailbox Fast Channel Group <n> Interrupt Status Register, n = 0 - 31

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCH-GRP-n--INT-ST--Mailbox-Fast-Channel-Group--n--Interrupt-Status-Register--n---0---31>

### MBX\_FCH\_GRP<n>\_INT\_ST, Mailbox Fast Channel Group <n> Interrupt Status Register, n = 0 - 31

Provides the status of each Fast Channel with the Fast Channel Transfer Group <n>

The number of MBX\_FCH\_GRP<n>\_INT\_ST; is set by the value of MBX\_FCH\_CFG0.NUM\_FCG, with any unused registers being RES0.

The number of fields within each register depends on the value of MBX\_FCH\_CFG0.NUM\_FCH\_PER\_FCG, with any additional fields being RES0.

With bit 0 representing the status of Fast Channel m in the Mailbox and bit NUM\_FCH\_PER\_FCG-1 representing the status of Fast Channel m+NUM\_FCH\_PER\_FCG in the Mailbox

Where m is calculated as n\*(NUM\_FCH\_PER\_FCG)

When all fields in the registers are RES0 the register is also treated as RES0

### Configurations

This register is present only when FCE is implemented and FCGI\_SPT. Otherwise, direct accesses to MBX\_FCH\_GRP<n>\_INT\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (4 \* n) + 0x0480

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_FCH\_GRP<n>\_INT\_ST bit assignments

![mhur.mbx_mbx_fch_grp_n__int_st bit assignments](images/0207-MBX_FCH_GRP-n-_INT_ST-Mailbox-Fast-Channel-Group-n-Interrupt-Status-Register-n-0-31-img01.svg)

<table id="mhur_mbx_mbx_fch_grp_n__int_st__ambx_fch_grpn_int_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_FCH_GRP&lt;n&gt;_INT_ST bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d83043e184" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83043e187" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83043e190" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d83043e193" rowspan="1">
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
    FCH_INT_ST&lt;m&gt;, bit[m], where m = 31 to 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates the status of each Fast Channel within the Fast Channel Group Transfer interrupt
    </p>
    <p>
     The Fast Channel the field indicates the interrupt status for is calculated using the following formula:
    </p>
    <p>
     NUM_FCH_PER_FCG * n + m
    </p>
    <p>
     where:
    </p>
    <p>
     n is the Fast Channel Group number
    </p>
    <p>
     m is the field offset
    </p>
    <p>
     If the calculated value is greater than the number of Fast Channels in the Mailbox the field is
     <span class="documents-archterm">
      RES0
     </span>
    </p>
    <p>
     To clear the interrupt software must acknowledge the last Transfer on the Fast Channel by reading the MFCW&lt;n&gt;_PAY register associated with the Channel.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel N has an outstanding interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel has an outstanding interrupt
      </p>
     </dd>
    </dl>
    <p>
     Only bits NUM_FCH_PER_FCG-1:0 are implemented, with all unused bits being
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
   <th class="documents-nocellnorowborder" colspan="1" id="d83043e291" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83043e294" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83043e297" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d83043e300" rowspan="1">
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
    (4 * n) + 0x0480
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_FCH_GRP&lt;n&gt;_INT_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
