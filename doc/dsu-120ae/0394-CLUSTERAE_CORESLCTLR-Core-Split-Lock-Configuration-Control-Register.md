# CLUSTERAE_CORESLCTLR, Core Split/Lock Configuration Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLCTLR--Core-Split-Lock-Configuration-Control-Register>

### CLUSTERAE\_CORESLCTLR, Core Split/Lock Configuration Control Register

Control register for setting the Split/Lock mode of each core.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERAE

Register offset
:   0x0030

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

Indicates request settings for core N Split/Lock

Figure 1. ext\_clusterae\_coreslctlr bit assignments

![ext_clusterae_coreslctlr bit assignments](images/0394-CLUSTERAE_CORESLCTLR-Core-Split-Lock-Configuration-Control-Register-img01.svg)

<table id="xym1733415037792__aclusterae_coreslctlr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAE_CORESLCTLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d286635e144" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d286635e147" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d286635e150" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d286635e153" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:56]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__63-56-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [55:52]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE13
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-55-52-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [51:48]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE12
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-51-48-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [47:44]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE11
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-47-44-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [43:40]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-43-40-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [39:36]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE9
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-39-36-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [35:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-35-32-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-31-28-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-27-24-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-23-20-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-19-16-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-15-12-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-11-8-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CORE1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xym1733415037792__id-7-4-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CORE0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates core N support for Split/Lock.
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
     The reset value when DCLS_MODE is configured to mixed is the relevant bit of CORESLDEFAULT pin.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in SPLIT mode.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Core is to be used in LOCKED mode (includes HYBRID mode).
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="xym1733415037792__id-3-0-reset" rowspan="1">
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
