# Memory Protection Controller Expansion

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals/Memory-Protection-Controller-Expansion>

### Memory Protection Controller Expansion

CRSAS Ma1 supports up to 16 MPCs to be added to the expansion system.

The SMPCEXPSTATUS signal allows the interrupts of the MPCs to be internally merged to the single MPC Combined interrupt.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPC Expansion Interrupt Status input
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
   <th class="documents-nocellnorowborder" colspan="1" id="d27649e67" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d27649e71" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d27649e75" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d27649e79" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMPCEXPSTATUS
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
     Input
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Interrupt Status inputs from all Expansion Memory Protection Controller. These are programmed through the SECMPCINTSTAT.SMPCEXP_STATUS register fields in the Secure Access Configuration Register Block and are used to raise an interrupt using the MPC Combined Interrupt.
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
