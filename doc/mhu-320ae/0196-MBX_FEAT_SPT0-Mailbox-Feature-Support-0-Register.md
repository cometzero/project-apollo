# MBX_FEAT_SPT0, Mailbox Feature Support 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FEAT-SPT0--Mailbox-Feature-Support-0-Register>

### MBX\_FEAT\_SPT0, Mailbox Feature Support 0 Register

Returns information on supported MHU features

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   0x0010

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_FEAT\_SPT0 bit assignments

![mhur.mbx_mbx_feat_spt0 bit assignments](images/0196-MBX_FEAT_SPT0-Mailbox-Feature-Support-0-Register-img01.svg)

<table id="mhur_mbx_mbx_feat_spt0__ambx_feat_spt0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_FEAT_SPT0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d89000e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d89000e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d89000e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d89000e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:24]
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RASE_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reliability, Availability and Serviceability Extension Support
    </p>
    <p>
     The value of this field depends on the implementation of the MHU and can take one of the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       MHU implements the RAS extension and follows the recommendations in the RAS section of the
       <a href="https://developer.arm.com/documentation/aes0072" target="_blank">
        <span>
         <cite>
          Message Handling Unit Architecture version 3.0
         </cite>
        </span>
       </a>
       .
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0011
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RME_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Realm Management Extension Support
    </p>
    <p>
     The value of this field depends on the implementation of the MHU and an optional reset time sampled input LEGACY_TZ_EN. The field can take one of the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       MHU does not implement the Realm Management extension
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MHU implements Realm Management extension
      </p>
     </dd>
    </dl>
    <p>
     The value of this field only applies to the MHU component which the register is associated with.
    </p>
    <p>
     It is valid for the different MHU components to implement different values for this field.
    </p>
    <p>
     For fields in the PBX_FEAT_SPT0 or SSC_FEAT_SPT0 registers the value applies to the MHUS only.
    </p>
    <p>
     For fields in the MBX_FEAT_SPT0 or RSC_FEAT_SPT0 registers the value applies to the MHUR only.
    </p>
    <p>
     When RME is implemented, for the MHU component, there can be a LEGACY_TZ_EN tie-off signal present on this MHU component.
    </p>
    <p>
     The value of the LEGACY_TZ_EN tie-off signal is sampled at reset of the MHU component which the tie-off signal is associated with.
    </p>
    <p>
     When the sampled value of the tie-off signal is
     <span class="documents-g.number.bin">
      0b1
     </span>
     the value of this field is always
     <span class="documents-g.number.hex">
      0x0
     </span>
     , otherwise the value of this field is dependent on whether RME is implemented for this MHU component.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_mbx_mbx_feat_spt0__id-19-16-reset-2" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0000
    </span>
    ,
    <span class="documents-g.number.bin">
     0b0001
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TZE_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     TrustZone Extension Support
    </p>
    <p>
     The value of this field depends on the implementation of the MHU and can take one of the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       MHU does not implement the TrustZone extension
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MHU implements TrustZone extension
      </p>
     </dd>
    </dl>
    <p>
     The value of this field only applies to the MHU component which the register is associated with.
    </p>
    <p>
     It is valid for the different MHU components to implement different values for this field.
    </p>
    <p>
     For fields in the PBX_FEAT_SPT0 or SSC_FEAT_SPT0 registers the value applies to the MHUS only.
    </p>
    <p>
     For fields in the MBX_FEAT_SPT0 or RSC_FEAT_SPT0 registers the value applies to the MHUR only.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_mbx_mbx_feat_spt0__id-15-12-reset-2" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0000
    </span>
    ,
    <span class="documents-g.number.bin">
     0b0001
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FCE_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fast Channel Extension Support
    </p>
    <p>
     The value of this field depends on the implementation of the MHU and can take one of the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       MHU does not implement the Fast Channel extension
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MHU implements Fast Channel extension
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_mbx_mbx_feat_spt0__id-11-8-reset-1" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0000
    </span>
    ,
    <span class="documents-g.number.bin">
     0b0001
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FE_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     FIFO Extension Support
    </p>
    <p>
     The value of this field depends on the implementation of the MHU and can take one of the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       MHU does not implement the FIFO extension
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MHU implements FIFO extension
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_mbx_mbx_feat_spt0__id-7-4-reset-7" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0000
    </span>
    ,
    <span class="documents-g.number.bin">
     0b0001
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DBE_SPT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Doorbell Extension Support
    </p>
    <p>
     The value of this field depends on the implementation of the MHU and can take one of the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       MHU does not implement the Doorbell extension
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MHU implements Doorbell extension
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="mhur_mbx_mbx_feat_spt0__id-3-0-reset-9" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0000
    </span>
    ,
    <span class="documents-g.number.bin">
     0b0001
    </span>
    , respective to the value.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d89000e492" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d89000e495" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d89000e498" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d89000e501" rowspan="1">
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
    0x0010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_FEAT_SPT0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
