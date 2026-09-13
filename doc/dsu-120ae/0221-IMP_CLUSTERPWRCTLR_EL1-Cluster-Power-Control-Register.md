# IMP_CLUSTERPWRCTLR_EL1, Cluster Power Control Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRCTLR-EL1--Cluster-Power-Control-Register>

### IMP\_CLUSTERPWRCTLR\_EL1, Cluster Power Control Register

This register controls power features of the cluster.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Functional group
:   Generic System Control

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 1010 0100 0000 0001 0111 0000

### Bit descriptions

Figure 1. AArch64\_imp\_clusterpwrctlr\_el1 bit assignments

![AArch64_imp_clusterpwrctlr_el1 bit assignments](images/0221-IMP_CLUSTERPWRCTLR_EL1-Cluster-Power-Control-Register-img01.svg)

<table id="fwh1733414848590__aimp_clusterpwrctlr_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERPWRCTLR_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e138" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e141" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e144" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d328521e147" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:62]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__63-62-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [61:48]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HSLCMASK
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Half slice core mask. This contains one bit per core, and if that bit is set then the core is included in the count that is compared with the HSLCCNT field. Bits above the number of cores implemented are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-61-48-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00000000000000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [47:46]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__47-46-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [45:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OSLCMASK
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     One slice core mask. This contains one bit per core, and if that bit is set then the core is included in the count that is compared with the OSLCCNT field. Bits above the number of cores implemented are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-45-32-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00000000000000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HSLCCNT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Half slice core count. When AUTOSLC is non-zero, if the number of cores powered on in the group selected by the HSLCMASK field is greater than this field then it will prevent the transition from ALL SLICE to HALF SLICE mode, or cause a transition from HALF SLICE to ALL SLICE. Note that a core that is off but has the IMP_CLUSTERPWRDN_EL1.SHORTSLP bit set will be treated as if it was on for this count.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-31-28-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OSLCCNT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     One slice core count. When AUTOSLC is non-zero, if the number of cores powered on in the group selected by the OSLCMASK field is greater than this field then it will prevent the transition from ALL SLICE or HALF SLICE to ONE SLICE mode, or cause a transition from ONE SLICE to HALF SLICE. Note that a core that is off but has the IMP_CLUSTERPWRDN_EL1.SHORTSLP bit set will be treated as if it was on for this count.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-27-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLCSF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Include snoop filter capacity in the AUTOSLC decision. If powering down slices would reduce the amount of snoop filter below the amount needed for the currently powered on cores then this will prevent the slice powerdown. Note that a core that is off but has the IMP_CLUSTERPWRDN_EL1.SHORTSLP bit set will be treated as if it was on for this calculation.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Ignore the snoop filter in AUTOSLC decisions
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       AUTOSLC will ensure enough slices are powered on for the currently powered on cores
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-23-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [22:21]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLCBW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Include slice bandwidth in the AUTOSLC decision. Prevent the slice powerdown if powering down slices would reduce the available bandwidth below the currently used bandwidth. Power up more slices if the slice bandwidth is close to saturating with the current number of slices.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Ignore the slice bandwidth in AUTOSLC decisions
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       AUTOSLC decisions are affected by high slice bandwidth that lasts for at least 3% of the AUTOSLC time period
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       AUTOSLC decisions are affected by high slice bandwidth that lasts for at least 12% of the AUTOSLC time period
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-22-21-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [20:18]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    QNAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Control L3 data RAM quick nap enable time
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Quick nap disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 8 cycle timeout
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 12 cycle timeout
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 16 cycle timeout
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 24 cycle timeout
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 32 cycle timeout
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 64 cycle timeout
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       Enabled with 128 cycle timeout
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-20-18-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b001
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [17:15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AUTOSLC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable automatic slice power down and configure evaluation time period. Note that a shorter time period allows better responsiveness to changing workloads, however if it is too short then the cost of frequent resizing can be too high.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       524,288 architectural timer ticks, time period of 524us
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       1,048,576 architectural timer ticks, time period of 1ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       2,097,152 architectural timer ticks, time period of 2.1ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       4,194,304 architectural timer ticks, time period of 4.2ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       8,388,608 architectural timer ticks, time period of 8.4ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       16,777,216 architectural timer ticks, time period of 16.8ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       33,554,432 architectural timer ticks, time period of 33.6ms
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-17-15-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AUTOPRTN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable automatic RAM power down and configure evaluation time period. Note that a shorter time period allows better responsiveness to changing workloads, however if it is too short then the cost of frequent resizing can be too high.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       524,288 architectural timer ticks, time period of 524us
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       1,048,576 architectural timer ticks, time period of 1ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       2,097,152 architectural timer ticks, time period of 2.1ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       4,194,304 architectural timer ticks, time period of 4.2ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       8,388,608 architectural timer ticks, time period of 8.4ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       16,777,216 architectural timer ticks, time period of 16.8ms
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       33,554,432 architectural timer ticks, time period of 33.6ms
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-14-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FULLRET
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable the FULL_RET slice powerdown mode and time period. Note that while this would typically be a longer period than the FUNCRET field, to allow entry into FUNC_RET first, but if it is shorter then FULL_RET will be entered directly rather than via FUNC_RET.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       128 architectural timer ticks, time period of 128ns
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       512 architectural timer ticks, time period of 512ns
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       2,048 architectural timer ticks, time period of 2us
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       4,096 architectural timer ticks, time period of 4.1us
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       8,192 architectural timer ticks, time period of 8.2us
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       16,384 architectural timer ticks, time period of 16.4us
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       32,768 architectural timer ticks, time period of 32.8us
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-11-9-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLCPRTN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The AUTOSLC logic should make slice operating mode decisions considering the AUTOPRTN status. If enabled, AUTOSLC will not power down more slices if AUTOPRTN is keeping all the L3 cache portions powered on. The AUTOPRTN mechanism can also request to power up more slices if it determines that more cache is needed and all the L3 cache portions are powered on
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       AUTOSLC decisions should ignore the AUTOPRTN status
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       AUTOSLC decisions should include the AUTOPRTN status
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLCRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cache slice power request. These bits are passed to the PPU as an advisory request for which slices to power. Note that when the AUTOSLC field is not
     <span class="documents-g.number.bin">
      0b000
     </span>
     , higher modes might be requested by the AUTOSLC mechanism and this field acts as a minimum operating mode.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Request that one L3 cache slice is powered on
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Request that all L3 cache slices are powered on
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Request that half the L3 cache slices are powered on
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-7-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PRTNRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cache portion power request. These bits are passed to the PPU as an advisory request for which portions to power. Note that these bits are only used when AUTOPRTN bits are 3'b000.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Request that none of the L3 cache portions in each slice is powered on
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Request that half of the L3 cache portions in each slice are powered on
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Request that both of the L3 cache portions in each slice are powered on
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-5-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OPRES
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Restore previous operating mode after cluster power off
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Operating mode defaults to ALL RAM ALL SLICE when powering on the cluster
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Enable restoring of previous operating mode
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="fwh1733414848590__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [2:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FUNCRET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     L3 Data RAM retention control.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Disable the retention circuit.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       128 architectural timer ticks, time period of 128ns minimum delay before retention
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       512 architectural timer ticks, time period of 512ns minimum delay before retention
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       2,048 architectural timer ticks, time period of 2us minimum delay before retention
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       4,096 architectural timer ticks, time period of 4.1us minimum delay before retention
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       8,192 architectural timer ticks, time period of 8.2us minimum delay before retention
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       16,384 architectural timer ticks, time period of 16.4us minimum delay before retention
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       32,768 architectural timer ticks, time period of 32.8us minimum delay before retention
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="fwh1733414848590__id-2-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C3\_5

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1417" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1420" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1423" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1426" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d328521e1429" rowspan="1">
    op2
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1111
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b101
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C3\_5, <Xt>

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1494" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1497" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1500" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d328521e1503" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d328521e1506" rowspan="1">
    op2
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1111
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b101
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C3\_5

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERPWRCTLR_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERPWRCTLR_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERPWRCTLR_EL1;
```

MSR S3\_0\_C15\_C3\_5, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.PWREN == '0' then
        UNDEFINED;
    elsif EL2Enabled() && ACTLR_EL2.PWREN == '0' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif ACTLR_EL3.PWREN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERPWRCTLR_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.PWREN == '0' then
        UNDEFINED;
    elsif ACTLR_EL3.PWREN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERPWRCTLR_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERPWRCTLR_EL1 = X[t];
```
