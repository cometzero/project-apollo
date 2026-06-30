# SSC_PBX_SG<n>, Sender Postbox Security Group n Register, n = 0

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Security-Control-register-summary/SSC-PBX-SG-n---Sender-Postbox-Security-Group-n-Register--n---0>

### SSC\_PBX\_SG<n>, Sender Postbox Security Group n Register, n = 0

Returns security configuration information. The bit descriptions for this register depend on whether the RME or TZE are implemented for the MHU Sender.

### Configurations

This register is present only when TZE is implemented for the MHUS. Otherwise, direct accesses to SSC\_PBX\_SG<n> are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.SSC

Register offset
:   (4 \* n) + 0x0110

### Bit descriptions

When RME is implemented for the MHUS and sampled value of MHUS LEGACY\_TZ\_EN is 0b0, the bit assignments are as follows:

Figure 1. MHUS.SSC\_SSC\_PBX\_SG<n> bit assignments

![mhus.ssc_ssc_pbx_sg_n_ bit assignments](images/0084-SSC_PBX_SG-n-Sender-Postbox-Security-Group-n-Register-n-0-img01.svg)

<table id="mhus_ssc_ssc_pbx_sg_n__assc_pbx_sgn-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SSC_PBX_SG&lt;n&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e157" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e160" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e163" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d64357e166" rowspan="1">
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
    SG_PBX&lt;m&gt;, bit[m], where m = 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Security Group for Postbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Postbox is assigned to the Secure Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Postbox is assigned to the Non-secure Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Postbox is assigned to the Root Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Postbox is assigned to the Realm Security Group
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

When RME is not implemented for the MHUS or RME is implemented for the MHUS and sampled value of MHUS LEGACY\_TZ\_EN is 0b1, the bit assignments are as follows:

Figure 2. MHUS.SSC\_SSC\_PBX\_SG<n> bit assignments

![mhus.ssc_ssc_pbx_sg_n_ bit assignments](images/0084-SSC_PBX_SG-n-Sender-Postbox-Security-Group-n-Register-n-0-img02.svg)

<table id="mhus_ssc_ssc_pbx_sg_n__assc_pbx_sgn-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   SSC_PBX_SG&lt;n&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e317" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e320" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e323" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d64357e326" rowspan="1">
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
    SG_PBX&lt;m&gt;, bit[m], where m = 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Security Group for Postbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Postbox is assigned to the Secure Security Group
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Postbox is assigned to the Non-secure Security Group
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
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e437" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e440" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64357e443" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d64357e446" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.SSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (4 * n) + 0x0110
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SSC_PBX_SG&lt;n&gt;
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
