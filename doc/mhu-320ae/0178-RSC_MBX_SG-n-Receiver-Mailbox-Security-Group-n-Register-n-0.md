# RSC_MBX_SG<n>, Receiver Mailbox Security Group <n> Register, n = 0

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Security-Control-register-summary/RSC-MBX-SG-n---Receiver-Mailbox-Security-Group--n--Register--n---0>

### RSC\_MBX\_SG<n>, Receiver Mailbox Security Group <n> Register, n = 0

Returns security configuration information. The bit description for this register depends on the value of the MHUR LEGACY\_TZ\_EN register and whether RME is implemented for the MHU

### Configurations

This register is present only when TZE is implemented for the MHUR. Otherwise, direct accesses to RSC\_MBX\_SG<n> are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.RSC

Register offset
:   (4 \* n) + 0x0110

### Bit descriptions

When RME is implemented for the MHUR and the sampled value of MHUR LEGACY\_TZ\_EN is 0b0, the RSC\_MBX\_SG<n> register has the following bit assignments.

Figure 1. MHUR.RSC\_RSC\_MBX\_SG<n> bit assignments

![mhur.rsc_rsc_mbx_sg_n_ bit assignments](images/0178-RSC_MBX_SG-n-Receiver-Mailbox-Security-Group-n-Register-n-0-img01.svg)

<table id="mhur_rsc_rsc_mbx_sg_n__arsc_mbx_sgn-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RSC_MBX_SG&lt;n&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e157" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e160" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e163" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d136446e166" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SG_MBX&lt;m&gt;, bit[m], where m = 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Security Group for Mailbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Mailbox is assigned to the Secure Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Mailbox is assigned to the Non-secure Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Mailbox is assigned to the Root Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Mailbox is assigned to the Realm Security Group
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
  </tr>
 </tbody>
</table>

When RME is not implemented for the MHUR or RME is implemented for the MHUR and sampled value of MHUR LEGACY\_TZ\_EN is 0b1, the RSC\_MBX\_SG<n> register has the following bit assignments.

Figure 2. MHUR.RSC\_RSC\_MBX\_SG<n> bit assignments

![mhur.rsc_rsc_mbx_sg_n_ bit assignments](images/0178-RSC_MBX_SG-n-Receiver-Mailbox-Security-Group-n-Register-n-0-img02.svg)

<table id="mhur_rsc_rsc_mbx_sg_n__arsc_mbx_sgn-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   RSC_MBX_SG&lt;n&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e317" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e320" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e323" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d136446e326" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SG_MBX&lt;m&gt;, bit[m], where m = 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Security Group for Mailbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Mailbox is assigned to the Secure Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Mailbox is assigned to the Non-secure Security Group
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
    Table 3.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e437" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e440" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d136446e443" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d136446e446" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (4 * n) + 0x0110
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RSC_MBX_SG&lt;n&gt;
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
