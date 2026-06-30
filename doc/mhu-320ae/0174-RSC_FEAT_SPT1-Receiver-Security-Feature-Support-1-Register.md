# RSC_FEAT_SPT1, Receiver Security Feature Support 1 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Security-Control-register-summary/RSC-FEAT-SPT1--Receiver-Security-Feature-Support-1-Register>

### RSC\_FEAT\_SPT1, Receiver Security Feature Support 1 Register

Returns information on supported MHU features

### Configurations

This register is present only when TZE is implemented for the MHUR. Otherwise, direct accesses to RSC\_FEAT\_SPT1 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.RSC

Register offset
:   0x0014

### Bit descriptions

Figure 1. MHUR.RSC\_RSC\_FEAT\_SPT1 bit assignments

![mhur.rsc_rsc_feat_spt1 bit assignments](images/0174-RSC_FEAT_SPT1-Receiver-Security-Feature-Support-1-Register-img01.svg)

<table id="mhur_rsc_rsc_feat_spt1__arsc_feat_spt1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RSC_FEAT_SPT1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d61817e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61817e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61817e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d61817e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:4]
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
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    AUTO_OP_SPT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Auto Op Protocol support
    </p>
    <p>
     For more information about the Auto Op protocol, see the
     <a href="https://developer.arm.com/documentation/aes0072" target="_blank">
      <span>
       <cite>
        Message Handling Unit Architecture version 3.0
       </cite>
      </span>
     </a>
     .
    </p>
    <p>
     The value of this field is set for MHU-320AE:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Auto Op(Full) is implemented
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
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
   <th class="documents-nocellnorowborder" colspan="1" id="d61817e259" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61817e262" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61817e265" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d61817e268" rowspan="1">
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
    0x0014
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RSC_FEAT_SPT1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
