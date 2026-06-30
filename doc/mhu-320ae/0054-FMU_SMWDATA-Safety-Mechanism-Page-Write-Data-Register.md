# FMU_SMWDATA, Safety Mechanism Page Write Data Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-SMWDATA--Safety-Mechanism-Page-Write-Data-Register>

### FMU\_SMWDATA, Safety Mechanism Page Write Data Register

Provides the Protection Mechanism page write data when FMU\_SMWR is written.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xF10

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_SMWDATA bit assignments

![mhu_fmu_register_block_fmu_smwdata bit assignments](images/0054-FMU_SMWDATA-Safety-Mechanism-Page-Write-Data-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_smwdata__afmu_smwdata-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_SMWDATA bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d47054e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47054e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47054e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d47054e160" rowspan="1">
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
    DATA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Protection Mechanism write data of the page indicated by FMU_SMWR.PAGEID.
    </p>
    <p>
     The write data contents depend on the page being accessed.
    </p>
    <p>
     For Page 0 accesses (available for all protection mechanisms):
    </p>
    <ul>
     <li>
      <p>
       bit [4]: Inserted. Inserts or clears an error for testing purposes.
      </p>
     </li>
     <li>
      <p>
       bit [2]: Critical. Sets the criticality of a protection mechanism.
      </p>
     </li>
     <li>
      <p>
       bit [1]: Enable. Enables or disables a protection mechanism.
      </p>
     </li>
    </ul>
    <p>
     For Page 1 accesses (available for AXI5-Stream or ACE5-Lite protection):
    </p>
    <ul>
     <li>
      <p>
       bits [31:16]: SendTime. Sets the duration when it becomes high priority for the block to send a ping or ping acknowledgement packet:
      </p>
     </li>
     <li>
      <p>
       4 x (SendTime +1) - 1 cycles.
      </p>
     </li>
     <li>
      <p>
       bits [15:0]: ErrTime. Sets the duration when the block detects a timeout error, because a ping or ping acknowledge packet is missing:
      </p>
     </li>
     <li>
      <p>
       64 x (ErrTime +1) - 1 cycles.
      </p>
     </li>
     <li>
      <p>
       Arm recommends that the time to error is at least 4 times longer than the time to send a ping or a ping acknowledgement packet. However, interconnect delays or the different frequencies of both domains might require this recommendation to be longer.
      </p>
     </li>
    </ul>
    <p>
     For Page 2 accesses (available for AXI5-Stream or ACE5-Lite protection):
    </p>
    <ul>
     <li>
      <p>
       bit [1]: crc_timeout_err. Set to 1, to clear a logged CRC timeout error.
      </p>
     </li>
     <li>
      <p>
       bit [1]: crc_checksum_err. Set to 1, to clear a logged CRC checksum error.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhu_fmu_register_block_fmu_smwdata__bits-31-0-reset-1">
     32{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Accessibility
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
   <th class="documents-nocellnorowborder" colspan="1" id="d47054e297" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47054e300" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47054e303" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d47054e306" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHU FMU Register Block
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xF10
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_SMWDATA
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
