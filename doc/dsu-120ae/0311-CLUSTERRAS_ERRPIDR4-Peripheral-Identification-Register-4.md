# CLUSTERRAS_ERRPIDR4, Peripheral Identification Register 4

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR4--Peripheral-Identification-Register-4>

### CLUSTERRAS\_ERRPIDR4, Peripheral Identification Register 4

Provides discovery information about the component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERRAS

Register offset
:   0xFD0

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0100
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_errpidr4 bit assignments

![ext_clusterras_errpidr4 bit assignments](images/0311-CLUSTERRAS_ERRPIDR4-Peripheral-Identification-Register-4-img01.svg)

<table id="vgb1733414950779__aclusterras_errpidr4-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRPIDR4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d21332e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21332e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21332e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d21332e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="vgb1733414950779__31-8-reset" rowspan="1">
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
    SIZE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Size of the component. The distance from the start of the address space used by this component to the end of the component identification registers.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       The component uses a single 4KB block.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgb1733414950779__id-7-4-reset" rowspan="1">
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
    DES_2
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Designer, JEP106 continuation code. This is the JEDEC-assigned JEP106 bank identifier for the designer of the component, minus 1.
    </p>
    <p>
     The code identifies the designer of the component, which might not be not the same as the implementer of the device containing the component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       Arm Limited. Number of 0x7F bytes in full JEP106 code 0x7F 0x7F 0x7F 0x7F 0x3B.
      </p>
     </dd>
    </dl>
    <div class="documents-p">
     <blockquote title="Note info">
      <h3 class="documents-underline">
       Note
      </h3>
      For a component designed by Arm Limited, the JEP106 bank is 5, meaning this field has the value
      <span class="documents-g.number.hex">
       0x4
      </span>
      .
     </blockquote>
    </div>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="vgb1733414950779__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0100
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
   <th class="documents-nocellnorowborder" colspan="1" id="d21332e279" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21332e282" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21332e285" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d21332e288" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFD0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRPIDR4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
