# Main Interconnect Peripheral Protection Controller Expansion

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals/Main-Interconnect-Peripheral-Protection-Controller-Expansion>

### Main Interconnect Peripheral Protection Controller Expansion

CRSAS Ma1 supports up to four additional PPCs to be added to the Main Interconnect in the expansion system. The following signals are provided to control each PPC<i> where i is {0-3}.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Main Interconnect PPC Expansion interface
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
   <th class="documents-nocellnorowborder" colspan="1" id="d12246e61" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12246e65" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12246e69" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d12246e73" rowspan="1">
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
       SMAINPPCEXPSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Main Interconnect PPC Interrupt Status Input. Each bit SMAINPPCEXPSTATUS[i] is to be connected to a single PPC&lt;i&gt;
    </p>
    <p>
     The SMAINPPCEXPSTATUS[i] bit is associated to the SECPPCINTSTAT.SMAINPPCEXP_STATUS[i] register field.
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
       SMAINPPCEXPCLEAR
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Main Interconnect PPC Interrupt Clear Output. Each bit SMAINPPCEXPCLEAR[i] is to be connected to a single PPC&lt;i&gt;.
    </p>
    <p>
     The SMAINPPCEXPCLEAR[i] bit is associated to the SECPPCINTCLR.SMAINPPCEXP_CLR[i] register field.
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
       MAINNSPPCEXP0&lt;i&gt;
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
     Main Interconnect PPC Non-secure Gating Control. These are a set of multiple bit interfaces, and each interface connects to PPC&lt;i&gt;. When each bit MAINNSPPCEXP&lt;i&gt;[j] of an interface is HIGH, it defines the &lt;j&gt; interface that the target PPC&lt;i&gt; controls as Non-secure access only.
    </p>
    <p>
     Each bit
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINNSPPCEXP&lt;i&gt;[j]
      </span>
     </span>
     is driven by the MAINNSPPCEXP&lt;i&gt;[j] register.
    </p>
    <p>
     Individual bits of this interface can be unimplemented or disabled which results in the associated register bit field being
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
       MAINPPPCEXP&lt;i&gt;
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
     Main Interconnect PPC Privilege Gating Control. These are a set of multiple interfaces and each interface connects to PPC&lt;i&gt;. When each bit MAINPPPCEXP&lt;i&gt;[j] of an interface is HIGH it defines the &lt;j&gt; interface that the target PPC&lt;i&gt; controls as both privileged and unprivileged access. Else, it is privileged access only.
    </p>
    <p>
     Each bit
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINPPPCEXP&lt;i&gt;[j]
      </span>
     </span>
     is selected from either MAINSPPPCEXP&lt;i&gt;[j] if MAINNSPPCEXP&lt;i&gt;[j] is &lsquo;0&rsquo; or MAINNSPPPCEXP&lt;i&gt;[j] otherwise.
    </p>
    <p>
     Individual bits of this interface can be unimplemented or disabled which results in the associated register bit fields that contributes to this control signal being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
 </tbody>
</table>
