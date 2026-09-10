# Interworking with 1D and 2D types

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes/Interworking-with-1D-and-2D-types>

### Interworking with 1D and 2D types

The 1D and 2D modes the XTYPE and YTYPE settings are constrained when using stream interface. This constriction is because the stream interface cannot use wrap modes and fill in some cases. The following table summarizes the allowed configuration settings:

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Stream interface for 1D and 2D types
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d12691e74" rowspan="1">
    <p>
     Mode
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12691e78" rowspan="1">
    <p>
     XTYPE
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12691e82" rowspan="1">
    <p>
     YTYPE
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12691e86" rowspan="1">
    <p>
     Stream allowed
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d12691e90" rowspan="1">
    <p>
     Comment
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disabled
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disabled
    </p>
    <p>
     Continue
    </p>
    <p>
     Wrap
    </p>
    <p>
     Fill
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     N/A
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     No data transfers occur regardless of stream interface enable.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disabled
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     All stream types can be used for simple 1D transfers. When only stream output is used DESXSIZE is ignored, when only stream input is used SRCXSIZE is ignored.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fill
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disabled
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     When the destination line has more space after
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       tlast
      </span>
     </span>
     is received, the remaining area is filled with FILLVAL.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disabled
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     No
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The stream input data cannot be fetched again so it results in a configuration error.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     All stream types can be used for simple 2D transfers. When only stream output is used, DESXSIZE and DESYSIZE are ignored. When only stream input is used, SRCXSIZE and SRCYSIZE are ignored. If the stream input sends an early
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       tlast
      </span>
     </span>
     the destination transfer can be stopped in the middle of the line.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fill
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     When the destination area has more space after
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       tlast
      </span>
     </span>
     is received, the remaining area is filled with FILLVAL.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     No
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The stream input data cannot be fetched again so it results in a configuration error.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2D
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
    <p>
     Wrap
    </p>
    <p>
     Fill
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     No
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The stream input data cannot be fetched again so it results in a configuration error.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2D
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Fill
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Continue
    </p>
    <p>
     Wrap
    </p>
    <p>
     Fill
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     No
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The stream input data does not indicate the end of the line so the DMAC cannot fill the remaining part of the line with data and it results in a configuration error.
    </p>
   </td>
  </tr>
 </tbody>
</table>
