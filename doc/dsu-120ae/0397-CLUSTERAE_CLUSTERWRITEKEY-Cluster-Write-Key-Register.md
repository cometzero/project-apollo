# CLUSTERAE_CLUSTERWRITEKEY, Cluster Write Key Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERWRITEKEY--Cluster-Write-Key-Register>

### CLUSTERAE\_CLUSTERWRITEKEY, Cluster Write Key Register

Control register for setting the Cluster KEY to enable writing of AE and PPU registers.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERAE

Register offset
:   0x0060

Access type
:   RESERVEDW

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx 0000 0000
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterae\_clusterwritekey bit assignments

![ext_clusterae_clusterwritekey bit assignments](images/0397-CLUSTERAE_CLUSTERWRITEKEY-Cluster-Write-Key-Register-img01.svg)

<table id="kkj1733415041879__aclusterae_clusterwritekey-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAE_CLUSTERWRITEKEY bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d282179e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d282179e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d282179e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d282179e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="kkj1733415041879__63-8-reset" rowspan="1">
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
    KEY
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Write protection key. The value 8'hBA must be written to the field to enable subsequent write to other registers in this page or any PPU registers.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="kkj1733415041879__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

WO
