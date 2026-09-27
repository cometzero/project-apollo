# Bridge Buffer Error Expansion

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals/Bridge-Buffer-Error-Expansion>

### Bridge Buffer Error Expansion

CRSAS Ma1 supports up to 16 additional bridges with buffer error signalling to be added to the expansion system.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Bridge Error Interrupt Expansion interface
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
   <th class="documents-nocellnorowborder" colspan="1" id="d74824e61" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d74824e65" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d74824e69" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d74824e73" rowspan="1">
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
       BRGEXPSTATUS
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
     Bridge Error Interrupt Status Input. Each bit BRGEXPSTATUS[i] is to be connected to a single bridge &lt;i&gt; where i is 0 to 15.
    </p>
    <p>
     These are associated with the BRGINTSTAT.BRGEXP_STATUS register field.
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
       BRGEXPCLEAR
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
     Bridge Error Interrupt Clear Output. Each bit BRGEXPCLEAR[i] is to be connected to a single bridge &lt;i&gt; where i is 0 to 15.
    </p>
    <p>
     These are associated with the BRGINTCLR.BRGEXP_CLR register field.
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
 </tbody>
</table>
