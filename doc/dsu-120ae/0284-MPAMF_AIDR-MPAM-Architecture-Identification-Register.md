# MPAMF_AIDR, MPAM Architecture Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-AIDR--MPAM-Architecture-Identification-Register>

### MPAMF\_AIDR, MPAM Architecture Identification Register

Identifies the version of the MPAM architecture that this MSC implements.

Note: The following values are defined for bits [7:0]:

- 0x01 == MPAM architecture v0.1
- 0x10 == MPAM architecture v1.0
- 0x11 == MPAM architecture v1.1

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offsets (2)
:   0x0020,0x0020

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0001 0001
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamf\_aidr bit assignments

![ext_mpamf_aidr bit assignments](images/0284-MPAMF_AIDR-MPAM-Architecture-Identification-Register-img01.svg)

<table id="nob1733414932546__ampamf_aidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMF_AIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e169" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e172" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e175" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d43917e178" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nob1733414932546__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ArchMajorRev
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Major revision of the MPAM architecture implemented by the MSC.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MPAM major version 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nob1733414932546__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ArchMinorRev
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Minor revision of the MPAM architecture implemented by the MSC.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       MPAM minor version 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="nob1733414932546__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e310" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e313" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e316" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d43917e319" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_AIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e367" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e370" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43917e373" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d43917e376" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_AIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
