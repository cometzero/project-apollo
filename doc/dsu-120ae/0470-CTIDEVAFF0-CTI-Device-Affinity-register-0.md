# CTIDEVAFF0, CTI Device Affinity register 0

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVAFF0--CTI-Device-Affinity-register-0>

### CTIDEVAFF0, CTI Device Affinity register 0

Copy of the low half of the PE AArch64-MPIDR\_EL1 register that allows a debugger to determine which PE in a multiprocessor system the CTI component relates to.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xFA8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctidevaff0 bit assignments

![ext_ctidevaff0 bit assignments](images/0470-CTIDEVAFF0-CTI-Device-Affinity-register-0-img01.svg)

<table id="jry1733415125011__actidevaff0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIDEVAFF0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d336035e149" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336035e152" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336035e155" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d336035e158" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPIDR_EL1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     This field is a read-only copy of the low half of any of the cores' AArch64-MPIDR_EL1, as seen from the highest implemented Exception level, but with bits [15:8] set to
     <span class="documents-g.number.hex">
      0x80
     </span>
     .
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="jry1733415125011__id-31-0-reset" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      Cluster
     </dt>
     <dd>
      <code>
       32{x}
      </code>
     </dd>
     <dt class="documents-dlterm">
      Core
     </dt>
     <dd>
      See section
      <cite>
       CTI register identification values
      </cite>
      in chapter
      <cite>
       Debug
      </cite>
      in your core
      <cite>
       Technical Reference Manual
      </cite>
      for this value.
     </dd>
    </dl>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d336035e245" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336035e248" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336035e251" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d336035e254" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFA8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIDEVAFF0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
