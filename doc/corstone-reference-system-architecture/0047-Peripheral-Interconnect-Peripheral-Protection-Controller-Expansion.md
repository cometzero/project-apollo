# Peripheral Interconnect Peripheral Protection Controller Expansion

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals/Peripheral-Interconnect-Peripheral-Protection-Controller-Expansion>

### Peripheral Interconnect Peripheral Protection Controller Expansion

CRSAS Ma1 supports up to four additional PPCs to be added to the Peripheral Interconnect in the expansion system. The following signals are provided to control the PPC <i> where i is {0-3}.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Peripheral Interconnect PPC Expansion interface
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
   <th class="documents-nocellnorowborder" colspan="1" id="d75030e61" rowspan="1">
    <p>
     Signal Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d75030e65" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d75030e69" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d75030e73" rowspan="1">
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
       SPERIPHPPCEXPSTATUS
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
     Peripheral Interconnect PPC Interrupt Status Input. Each bit SPERIPHPPCEXPSTATUS[i] is to be connected to a single PPC &lt;i&gt;.
    </p>
    <p>
     The SPERIPHPPCEXPSTATUS[i] bit is associated to the SECPPCINTSTAT.SPERIPHPPCEXP_STATUS[i] register field.
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
       SPERIPHPPCEXPCLEAR
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
     Peripheral Interconnect PPC Interrupt Clear Output. Each bit SPERIPHPPCEXPCLEAR[i] is to be connected to a single PPC &lt;i&gt;.
    </p>
    <p>
     The SPERIPHPPCEXPCLEAR[i] bit is associated to the SECPPCINTCLR.SPERIPHPPCEXP_CLR[i] register field.
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHNSPPCEXP&lt;i&gt;
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
     Peripheral Interconnect PPC Non-secure Gating Control. These are a set of multiple bit interfaces, and each interface connects to PPC &lt;i&gt;. When each bit &lsquo;j&rsquo; of an interface is HIGH, it defines a specific &lt;j&gt; interface that the target PPC controls as Non-secure access only.
    </p>
    <p>
     Each bit
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHNSPPCEXP&lt;i&gt;[j]
      </span>
     </span>
     is driven by the PERIPHNSPPCEXP&lt;i&gt;[j] register.
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
       PERIPHPPPCEXP&lt;i&gt;
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
     Peripheral Interconnect PPC Privilege Gating Control. These are a set of multiple bit interfaces and each interface connects to PPC &lt;i&gt;. When each bit PERIPHPPPCEXP&lt;i&gt;[j] of an interface is HIGH, it defines the &lt;j&gt; interface that the target PPC &lt;i&gt; controls as both privileged and unprivileged access. Else, it is privileged access only.
    </p>
    <p>
     Each bit
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHPPPCEXP&lt;i&gt;[j]
      </span>
     </span>
     is selected from either PERIPHSPPPCEXP&lt;i&gt;[j] if PERIPHNSPPCEXP&lt;i&gt;[j] is &lsquo;0&rsquo; or PERIPHNSPPPCEXP&lt;i&gt;[j] otherwise.
    </p>
    <p>
     Individual bits of this interface can be unimplemented or disabled, which results in the associated register bit fields that contributes to this control signal being
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
  </tr>
 </tbody>
</table>
