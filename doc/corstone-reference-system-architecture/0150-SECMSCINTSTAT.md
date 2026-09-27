# SECMSCINTSTAT

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECMSCINTSTAT>

### SECMSCINTSTAT

When a security violation occurs at any Manager Security Controller (MSC) in the subsystem and in the expansion logic, an interrupt is raised through a combined interrupt to the CPUs. The Secure MSC Interrupt Status Register allows software to determine the source of the interrupt.

### Configurations

This register implementation depends on the configuration of individual fields.

### Attributes

Width
:   32-bit

Power domain
:   PD\_SYS

Reset
:   This register is reset by
    nWARMRESETSYS.

### Usage constraints

This register is Secure Privileged access only and supports 32-bit RW accesses. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SECMSCINTSTAT bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d43998e107" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43998e111" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43998e115" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43998e119" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d43998e123" rowspan="1">
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
     31:16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCEXP_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt Status for Expansion MSC. Each bit i shows the interrupt status of MSC connected to the input signal
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPSTATUS[i]
      </span>
     </span>
     The configuration option MSCEXPDIS defines if each bit within this register is actually implemented such that if MSCEXPDIS[i] = 1&rsquo;b1 then SMSCEXP_STATUS[i] is disabled and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15:12
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
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
     11
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU3M1_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU3 M1 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU3M0_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU3 M0 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     9
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU2M1_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU2 M1 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     8
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU2M0_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU2 M0 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU1M1_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU1 M1 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU1M0_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU1 M0 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU0M1_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU0 M1 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCNPU0M0_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for NPU0 M0 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMNPU &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCDMAM1_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for DMA M1 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMDMA &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SMSCDMAM0_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt status for DMA M0 MSC
    </p>
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
     If NUMDMA &lt; 1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     1:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
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
