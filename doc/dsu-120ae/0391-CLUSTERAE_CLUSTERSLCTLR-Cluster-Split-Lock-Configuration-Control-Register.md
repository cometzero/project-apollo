# CLUSTERAE_CLUSTERSLCTLR, Cluster Split/Lock Configuration Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLCTLR--Cluster-Split-Lock-Configuration-Control-Register>

### CLUSTERAE\_CLUSTERSLCTLR, Cluster Split/Lock Configuration Control Register

Control register for setting the Split/Lock mode of the Cluster.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERAE

Register offset
:   0x0008

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterae\_clusterslctlr bit assignments

![ext_clusterae_clusterslctlr bit assignments](images/0391-CLUSTERAE_CLUSTERSLCTLR-Cluster-Split-Lock-Configuration-Control-Register-img01.svg)

<table id="yrd1733415033302__aclusterae_clusterslctlr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAE_CLUSTERSLCTLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d256651e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d256651e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d256651e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d256651e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="yrd1733415033302__63-4-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLSTR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates cluster support for Split/Lock.
    </p>
    <p>
     The reset value is
     <span class="documents-g.number.bin">
      0b0000
     </span>
     when DCLS_MODE is configured to split.
    </p>
    <p>
     The reset value is
     <span class="documents-g.number.bin">
      0b0001
     </span>
     when DCLS_MODE is configured to locked.
    </p>
    <p>
     The reset value when DCLS_MODE is configured to mixed is the value of the CLUSTERSLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Cluster is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Cluster is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="yrd1733415033302__id-3-0-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
