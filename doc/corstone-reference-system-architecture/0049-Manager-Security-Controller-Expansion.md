# Manager Security Controller Expansion

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals/Manager-Security-Controller-Expansion>

### Manager Security Controller Expansion

CRSAS Ma1 supports up to 16 additional Manager Security Controllers (MSC) to be added to the expansion system. The following signals are provided to control each MSC<i> where i is {0-15}.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MSC Expansion interface
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
   <th class="documents-nocellnorowborder" colspan="1" id="d65075e61" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d65075e65" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d65075e69" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d65075e73" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     MSC Interrupt Status Input. Each bit SMSCEXPSTATUS[i] is to be connected to a single MSC&lt;i&gt;.
    </p>
    <p>
     These are associated with the SECMSCINTSTAT.SMSCEXP_STATUS register field.
    </p>
    <p>
     Individual bits of this interface can be unimplemented or disabled, which results in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPCLEAR
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     MSC Interrupt Clear Output. Each bit SMSCEXPCLEAR[i] is to be connected to a single MSC&lt;i&gt;.
    </p>
    <p>
     These are associated with the SECMSCINTCLR.SMSCEXP_CLR register field.
    </p>
    <p>
     Individual bits of this interface can be unimplemented or disabled, which results in the associated register bit field being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NSMSCEXP
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     MSC Non-secure Configuration. Each bit NSMSCEXP[i] is to be connected to a single MSC&lt;i&gt;. Set HIGH to configure a manager as Non-secure.
    </p>
    <p>
     These are associated with the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NSMSCEXP.NS_MSCEXP
      </span>
     </span>
     register field.
    </p>
    <p>
     Individual bits of this interface can be unimplemented or disabled. Any disabled bit of this interface that still exist must be tied HIGH.
    </p>
   </td>
  </tr>
 </tbody>
</table>
