# CLUSTERAE_CLUSTERRECOV, Cluster Recovery Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERRECOV--Cluster-Recovery-Control-Register>

### CLUSTERAE\_CLUSTERRECOV, Cluster Recovery Control Register

Debug recovery and warm reset request register.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERAE

Register offset
:   0x0050

Access type
:   RW

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

Figure 1. ext\_clusterae\_clusterrecov bit assignments

![ext_clusterae_clusterrecov bit assignments](images/0396-CLUSTERAE_CLUSTERRECOV-Cluster-Recovery-Control-Register-img01.svg)

<table id="qex1733415040962__aclusterae_clusterrecov-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAE_CLUSTERRECOV bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d278300e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d278300e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d278300e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d278300e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="qex1733415040962__63-8-reset" rowspan="1">
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
    WARMRST
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     This mode is used for resetting during debugging, after an unrecoverable RAS error, or after a watchdog timeout.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster in normal operation. When written requests a return to normal operation (or remain if already operating normally)
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster entering WARM_RST. When written requests the Cluster to enter WARM_RST. Once the whole Cluster has entered, it automatically returns to normal operation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster entering WARM_RST, ready to remain there. When written requests the Cluster to enter WARM_RST and keep the Cores and Cluster held in reset.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster leaving WARM_RST. Writes of this value are unsupported.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0111
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster all in WARM_RST (or OFF/OFF_EMU). Writes of this value are unsupported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qex1733415040962__id-7-4-reset" rowspan="1">
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
    DBGRECOV
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     This mode is used for recovering state for use in debugging, after a reset which could typically be from some kind of watchdog timeout. It is similar to WARM_RST, but additionally preserves the RAM contents.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster in normal operation. When written requests a return to normal operation (or remain if already operating normally)
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster entering DBG_RECOV. When written requests the Cluster to enter DBG_RECOV. Once the whole Cluster has entered, it automatically returns to normal operation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster entering DBG_RECOV, ready to remain there. When written requests the Cluster to enter DBG_RECOV and keep the Cores and Cluster held in reset.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster leaving DBG_RECOV. Writes of this value are unsupported.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0111
      </span>
     </dt>
     <dd>
      <p>
       When read, returns the current status of Cores and Cluster all in DBG_RECOV (or OFF/OFF_EMU). Writes of this value are unsupported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="qex1733415040962__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RW
