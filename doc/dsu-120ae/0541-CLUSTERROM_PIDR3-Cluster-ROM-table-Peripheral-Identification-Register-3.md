# CLUSTERROM_PIDR3, Cluster ROM table Peripheral Identification Register 3

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-PIDR3--Cluster-ROM-table-Peripheral-Identification-Register-3>

### CLUSTERROM\_PIDR3, Cluster ROM table Peripheral Identification Register 3

Provides CoreSight discovery information.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERROM

Register offset
:   0xFEC

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterrom\_pidr3 bit assignments

![ext_clusterrom_pidr3 bit assignments](images/0541-CLUSTERROM_PIDR3-Cluster-ROM-table-Peripheral-Identification-Register-3-img01.svg)

<table id="xxx1733415230557__aclusterrom_pidr3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERROM_PIDR3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d330521e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d330521e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d330521e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d330521e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="xxx1733415230557__31-8-reset" rowspan="1">
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
    REVAND
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component minor revision.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Component minor revision 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xxx1733415230557__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CMOD
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Customer Modified.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       The component is not modified from the original design.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="xxx1733415230557__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
