# SOC_IDENTITY

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SOC-IDENTITY>

### SOC\_IDENTITY

The System-On-Chip (SoC) Identity Register provides an area where software can find out about the SoC’s part number, its implementor and revision number. These are defined by configuration options that are expected to be set by a SoC integrator to identify the SoC.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Type
:   This register is read-only and is accessible by accesses of any security attributes.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SOC_IDENTITY bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d84038e90" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84038e94" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84038e98" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84038e102" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d84038e106" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31:20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOC_PRODUCT_ID
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF value identifying the SoC.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     SOCPRTID
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     19:16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOC_VARIANT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF value variant or major revision of the SoC.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     SOCVAR
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15:12
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOC_REVISION
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF value used to distinguish minor revisions of the SoC.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     SOCREV
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     11:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SOC_IMPLEMENTATOR
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Contains the JEP106 code of the company that implemented the SoC:
    </p>
    <ul>
     <li>
      <p>
       [11:8] JEP106 continuation code of implementer.
      </p>
     </li>
     <li>
      <p>
       [7] Always 0.
      </p>
     </li>
     <li>
      <p>
       [6:0] JEP106 identity code of implementer.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     SOCIMPLID
    </p>
   </td>
  </tr>
 </tbody>
</table>

We recommend that the SoC Identity values are also used to identify the SoC or the complete subsystem to the debugger in one or both of the following ways:

1. If the system is a standalone system, the SoC Identity values can be used to generate the TARGETID of the SoC Debug Port in the expansion system, as follows:

   - TARGETID[31:28] uses SOCVAR,
   - TARGETID[27:16] uses SOCPRTID,
   - TARGETID[15:12] tied to 0x00
   - TARGETID[11:1] uses {SOCIMPLID[11:8], SOCIMPLID[6:0]}.
   - TARGETID[0] tied to 0b1.

   For more information on TARGETID, see Arm® Debug Interface Architecture Specification ADIv6.0.
2. The SoC Identity values can also be used in to define the PIDR values of the first Debug ROM in the expansion system that the debugger sees for this system, as follows:

   - REVISION uses SOCVAR,
   - {PART\_1, PART\_0} uses SOCPRTID,
   - {DES\_2, DES\_1, DES\_0} uses SOCIMPLID,
   - REVAND uses SOCREV,
   - CMOD set to 0x0.

   For more information on PIDR registers of CoreSight Debug ROM, see Arm® CoreSight™ Architecture Specification v3.0.
