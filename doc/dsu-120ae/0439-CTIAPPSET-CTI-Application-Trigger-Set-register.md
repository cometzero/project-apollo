# CTIAPPSET, CTI Application Trigger Set register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIAPPSET--CTI-Application-Trigger-Set-register>

### CTIAPPSET, CTI Application Trigger Set register

Sets bits of the Application Trigger register.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0x014

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_ctiappset bit assignments

![ext_ctiappset bit assignments](images/0439-CTIAPPSET-CTI-Application-Trigger-Set-register-img01.svg)

<table id="mpw1733415084280__actiappset-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIAPPSET bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d5963e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d5963e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d5963e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d5963e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mpw1733415084280__31-4-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    APPSET3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Application trigger3 enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is inactive. Writing this has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is active. Writing this sets the corresponding bit in CTIAPPTRIG to 1 and generates a channel event.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mpw1733415084280__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    APPSET2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Application trigger2 enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is inactive. Writing this has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is active. Writing this sets the corresponding bit in CTIAPPTRIG to 1 and generates a channel event.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mpw1733415084280__id-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    APPSET1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Application trigger1 enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is inactive. Writing this has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is active. Writing this sets the corresponding bit in CTIAPPTRIG to 1 and generates a channel event.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mpw1733415084280__id-1-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    APPSET0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Application trigger0 enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is inactive. Writing this has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reading this means the application trigger is active. Writing this sets the corresponding bit in CTIAPPTRIG to 1 and generates a channel event.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="mpw1733415084280__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d5963e348" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d5963e351" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d5963e354" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d5963e357" rowspan="1">
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
    0x014
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIAPPSET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

When SoftwareLockStatus()
:   RO

When !SoftwareLockStatus()
:   RW
