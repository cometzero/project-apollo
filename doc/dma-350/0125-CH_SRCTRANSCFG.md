# CH_SRCTRANSCFG

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRANSCFG>

### CH\_SRCTRANSCFG

The Channel Source Transfer Configuration register provides transfer attribute settings in the read direction of the DMA command.

The content of this register can be updated during command linking by setting bit[10] in the command link header.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x028

Type
:   RW

Default
:   0x000F0400

### Usage constraints

Becomes read-only after ENABLECMD is set.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CH_SRCTRANSCFG register bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d61501e129" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61501e133" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61501e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d61501e141" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d61501e145" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [31:20]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [19:16]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCMAXBURSTLEN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source Max Burst Length. Hint for the DMA on what is the maximum allowed burst size it can use for read transfers. The maximum number of beats sent by the DMA for a read burst is equal to SRCMAXBURSTLEN + 1. Default value is 16 beats, which allows the DMA to set all burst sizes. Note: Limited by the DATA_BUFF_SIZE so larger settings may not always result in larger bursts.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xf
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [15:12]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [11]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCPRIVATTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source Transfer Privilege Attribute.
    </p>
    <ul>
     <li>
      <p>
       0: Unprivileged
      </p>
     </li>
     <li>
      <p>
       1: Privileged
      </p>
     </li>
    </ul>
    <p>
     When a channel is unprivileged this bit is tied to 0.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [10]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCNONSECATTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source Transfer Non-secure Attribute.
    </p>
    <ul>
     <li>
      <p>
       0: Secure
      </p>
     </li>
     <li>
      <p>
       1: Non-secure
      </p>
     </li>
    </ul>
    <p>
     When a channel is Non-secure this bit is tied to 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [9:8]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCSHAREATTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source Transfer Shareability Attribute.
    </p>
    <ul>
     <li>
      <p>
       00: Non-shareable
      </p>
     </li>
     <li>
      <p>
       01: Reserved
      </p>
     </li>
     <li>
      <p>
       10: Outer shareable
      </p>
     </li>
     <li>
      <p>
       11: Inner shareable
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [7:4]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCMEMATTRHI
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Source Transfer Memory Attribute field [7:4].
    </p>
    <ul>
     <li>
      <p>
       0000: Device memory
      </p>
     </li>
     <li>
      <p>
       0001: Normal memory, Outer Write allocate, Outer Write -through transient
      </p>
     </li>
     <li>
      <p>
       0010: Normal memory, Outer Read allocate, Outer Write-through transient
      </p>
     </li>
     <li>
      <p>
       0011: Normal memory, Outer Read/Write allocate, Outer Write-through transient
      </p>
     </li>
     <li>
      <p>
       0100: Normal memory, Outer non-cacheable
      </p>
     </li>
     <li>
      <p>
       0101: Normal memory, Outer Write allocate, Outer Write-back transient
      </p>
     </li>
     <li>
      <p>
       0110: Normal memory, Outer Read allocate, Outer Write-back transient
      </p>
     </li>
     <li>
      <p>
       0111: Normal memory, Outer Read/Write allocate, Outer Write-back transient
      </p>
     </li>
     <li>
      <p>
       1000: Normal memory, Outer Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1001: Normal memory, Outer Write allocate, Outer Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1010: Normal memory, Outer Read allocate, Outer Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1011: Normal memory, Outer Read/Write allocate, Outer Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1100: Normal memory, Outer Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1100: Normal memory, Outer Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1101: Normal memory, Outer Write allocate, Outer Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1110: Normal memory, Outer Read allocate, Outer Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1111: Normal memory, Outer Read/Write allocate, Outer Write-back non-transient
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [3:0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SRCMEMATTRLO
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Source Transfer Memory Attribute field [3:0].
    </p>
    <p>
     When SRCMEMATTRHI is Device type (0000) then this field means:
    </p>
    <ul>
     <li>
      <p>
       0000: Device-nGnRnE
      </p>
     </li>
     <li>
      <p>
       0100: Device-nGnRE
      </p>
     </li>
     <li>
      <p>
       1000: Device-nGRE
      </p>
     </li>
     <li>
      <p>
       1100: Device-GRE
      </p>
     </li>
     <li>
      <p>
       Others: Invalid resulting in UNPREDICTABLE behavior.
      </p>
     </li>
    </ul>
    <p>
     When SRCMEMATTRHI is Normal memory type (other than 0000) then this field means:
    </p>
    <ul>
     <li>
      <p>
       0000: Reserved
      </p>
     </li>
     <li>
      <p>
       0001: Normal memory, Inner Write allocate, Inner Write-through transient
      </p>
     </li>
     <li>
      <p>
       0010: Normal memory, Inner Read allocate, Inner Write-through transient
      </p>
     </li>
     <li>
      <p>
       0011: Normal memory, Inner Read/Write allocate, Inner Write-through transient
      </p>
     </li>
     <li>
      <p>
       0100: Normal memory, Inner non-cacheable
      </p>
     </li>
     <li>
      <p>
       0101: Normal memory, Inner Write allocate, Inner Write-back transient
      </p>
     </li>
     <li>
      <p>
       0110: Normal memory, Inner Read allocate, Inner Write-back transient
      </p>
     </li>
     <li>
      <p>
       0111: Normal memory, Inner Read/Write allocate, Inner Write-back transient
      </p>
     </li>
     <li>
      <p>
       1000: Normal memory, Inner Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1001: Normal memory, Inner Write allocate, Inner Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1010: Normal memory, Inner Read allocate, Inner Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1011: Normal memory, Inner Read/Write allocate, Inner Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1011: Normal memory, Inner Read/Write allocate, Inner Write-through non-transient
      </p>
     </li>
     <li>
      <p>
       1100: Normal memory, Inner Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1101: Normal memory, Inner Write allocate, Inner Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1110: Normal memory, Inner Read allocate, Inner Write-back non-transient
      </p>
     </li>
     <li>
      <p>
       1111: Normal memory, Inner Read/Write allocate, Inner Write-back non-transient
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
