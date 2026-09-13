# MPAMF_SIDR, MPAM Features Secure Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-SIDR--MPAM-Features-Secure-Identification-Register>

### MPAMF\_SIDR, MPAM Features Secure Identification Register

The MPAMF\_SIDR is a 32-bit read-only register that indicates the maximum Secure PARTID and Secure PMG on this MSC.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offset
:   0x0008

Access type
:   RO

Reset value
:   ```
    xxxx xxxx 0000 0001 0000 0000 0000 0111
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamf\_sidr bit assignments

![ext_mpamf_sidr bit assignments](images/0282-MPAMF_SIDR-MPAM-Features-Secure-Identification-Register-img01.svg)

<table id="qze1733414930758__ampamf_sidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMF_SIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d161950e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d161950e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d161950e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d161950e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qze1733414930758__31-24-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    S_PMG_MAX
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Maximum value of Secure PMG supported by this component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000001
      </span>
     </dt>
     <dd>
      <p>
       Supports 2 Secure PMGs.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qze1733414930758__id-23-16-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [15:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    S_PARTID_MAX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Maximum value of Secure PARTID supported by this component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000000000000111
      </span>
     </dt>
     <dd>
      <p>
       Supports 8 Secure PARTIDs.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="qze1733414930758__id-15-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0007
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
   <th class="documents-nocellnorowborder" colspan="1" id="d161950e282" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d161950e285" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d161950e288" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d161950e291" rowspan="1">
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
    0x0008
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_SIDR_s
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
