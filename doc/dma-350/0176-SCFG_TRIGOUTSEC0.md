# SCFG_TRIGOUTSEC0

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMASECCFG-description/SCFG-TRIGOUTSEC0>

### SCFG\_TRIGOUTSEC0

The Secure Configuration Trigger Output Security Mapping register 0 is used to define the security attribute of each trigger output.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMASECCFG

Offset
:   0x028

Type
:   RW

Default
:   0x00000000

### Usage constraints

Becomes read-only after SEC\_CFG\_LCK is set.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SCFG_TRIGOUTSEC0 register bit descriptions
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d61246e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61246e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61246e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61246e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d61246e142" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [31:0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SCFGTRIGOUTSEC0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Secure Configuration Trigger Output Security Mapping. When [i] set to &lsquo;1&rsquo;, Trigger Output &lt;i&gt; is Non-secure world, else Secure world. The NUM_TRIGGER_OUT parameter limits this field, unused bits are RAZWI. Value for bit[i] can only be changed if the trigger output port is not in use, so reading back the register content is needed to check the success of the change. The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: SECEXT_PRESENT &amp; (1) &amp; (NUM_TRIGGER_OUT &gt; 0)
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
