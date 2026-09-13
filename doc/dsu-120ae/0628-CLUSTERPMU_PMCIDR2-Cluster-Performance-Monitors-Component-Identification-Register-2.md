# CLUSTERPMU_PMCIDR2, Cluster Performance Monitors Component Identification Register 2

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR2--Cluster-Performance-Monitors-Component-Identification-Register-2>

### CLUSTERPMU\_PMCIDR2, Cluster Performance Monitors Component Identification Register 2

Provides information to identify a Performance Monitor component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xFF8

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0101
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmcidr2 bit assignments

![ext_clusterpmu_pmcidr2 bit assignments](images/0628-CLUSTERPMU_PMCIDR2-Cluster-Performance-Monitors-Component-Identification-Register-2-img01.svg)

<table id="ipn1733415345274__aclusterpmu_pmcidr2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMCIDR2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d317006e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d317006e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d317006e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d317006e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="ipn1733415345274__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRMBL_2
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Preamble.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000101
      </span>
     </dt>
     <dd>
      <p>
       CoreSight component identification preamble.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="ipn1733415345274__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x05
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

When IsCorePowered()
:   RO

Otherwise
:   ERROR
