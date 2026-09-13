# CTICLAIMCLR, CTI Claim Tag Clear register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register>

### CTICLAIMCLR, CTI Claim Tag Clear register

Used by software to read the values of the CLAIM bits, and to clear these bits to 0.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xFA4

Access type
:   See bit descriptions

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

Figure 1. ext\_cticlaimclr bit assignments

![ext_cticlaimclr bit assignments](images/0469-CTICLAIMCLR-CTI-Claim-Tag-Clear-register-img01.svg)

<table id="qst1733415123994__acticlaimclr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTICLAIMCLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d338283e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d338283e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d338283e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d338283e150" rowspan="1">
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
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qst1733415123994__31-4-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLAIM3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLAIM tag clear bit.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No action.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Indirectly clear claim bit to 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qst1733415123994__id-3-reset" rowspan="1">
    <p>
     <span>
      x
     </span>
     <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_1" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_1" id="fnsrc_1">
      <sup>
       1
      </sup>
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLAIM2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLAIM tag clear bit.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No action.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Indirectly clear claim bit to 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qst1733415123994__id-2-reset" rowspan="1">
    <p>
     <span>
      x
     </span>
     <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_2" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_2" id="fnsrc_2">
      <sup>
       2
      </sup>
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLAIM1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLAIM tag clear bit.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No action.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Indirectly clear claim bit to 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qst1733415123994__id-1-reset" rowspan="1">
    <p>
     <span>
      x
     </span>
     <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_3" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_3" id="fnsrc_3">
      <sup>
       3
      </sup>
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLAIM0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CLAIM tag clear bit.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No action.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Indirectly clear claim bit to 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="qst1733415123994__id-0-reset" rowspan="1">
    <p>
     <span>
      x
     </span>
     <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_4" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fntarg_4" id="fnsrc_4">
      <sup>
       4
      </sup>
     </a>
    </p>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d338283e444" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d338283e447" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d338283e450" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d338283e453" rowspan="1">
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
    0xFA4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTICLAIMCLR
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

[1](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fnsrc_1) An External Debug reset clears the CLAIM tag bits to 0.

[2](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fnsrc_2) An External Debug reset clears the CLAIM tag bits to 0.

[3](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fnsrc_3) An External Debug reset clears the CLAIM tag bits to 0.

[4](/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICLAIMCLR--CTI-Claim-Tag-Clear-register?lang=en#fnsrc_4) An External Debug reset clears the CLAIM tag bits to 0.
