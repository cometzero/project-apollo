# CNTBase Registers Summary

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-timer-programmers-model/CNTBase-Registers-Summary>

### CNTBase Registers Summary

This section provides a summary of the CNTBase Registers.

The following table shows a summary of the CNTBase Registers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTBase Frame Registers summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d45180e68" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d45180e72" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d45180e76" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d45180e80" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d45180e84" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTPCT[31:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Physical Count Register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTPCT--Counter-timer-Physical-Count-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTPCT--Counter-timer-Physical-Count-register?lang=en" title="The CNTPCT register holds the 64‑bit physical count value. The following table shows the bit assignments.">
      CNTPCT, Counter-timer Physical Count register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x004
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTPCT[63:32]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
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
     <span class="documents-g.number.hex">
      0x008
     </span>
     -
     <span class="documents-g.number.hex">
      0x00C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x010
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTFRQ
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Counter Frequency register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTFRQ--Counter-timer-Frequency-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTFRQ--Counter-timer-Frequency-register?lang=en" title="The CNTFRQ register is provided so that software can discover the frequency of the system counter. The instance of this register in the CNTCTLBase frame must be programmed with this value as part of system initialization. Hardware does not interpret the value of the register.">
      CNTFRQ, Counter-timer Frequency register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x014
     </span>
     -
     <span class="documents-g.number.hex">
      0x01C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x020
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CVAL[31:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer CompareValue register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CVAL--Counter-timer-Physical-Timer-CompareValue-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CVAL--Counter-timer-Physical-Timer-CompareValue-register?lang=en" title="The CNTP_CVAL register holds the 64‑bit compare value for the timer. The following table shows the bit assignments.">
      CNTP_CVAL, Counter-timer Physical Timer CompareValue register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x024
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CVAL[63:32]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
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
     <span class="documents-g.number.hex">
      0x028
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_TVAL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     TimerValue register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-TVAL--Counter-timer-Physical-Timer-TimerValue-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-TVAL--Counter-timer-Physical-Timer-TimerValue-register?lang=en" title="The CNTP_TVAL register holds the timer value for the timer. The following table shows the bit assignments.">
      CNTP_TVAL, Counter-timer Physical Timer TimerValue register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x02C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CTL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_000X
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer Control register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CTL--Counter-timer-Physical-Timer-Control-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CTL--Counter-timer-Physical-Timer-Control-register?lang=en" title="The CNTP_CTL register is a control register for the timer. The following table shows the bit assignments.">
      CNTP_CTL, Counter-timer Physical Timer Control register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x030
     </span>
     -
     <span class="documents-g.number.hex">
      0x03C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x040
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_AIVAL[31:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AutoIncrValue register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL--AutoIncrValue-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL--AutoIncrValue-register?lang=en" title="The CNTP_AIVAL register holds the 64‑bit Automatic Increment value for the timer. The following table shows the bit assignments.">
      CNTP_AIVAL, AutoIncrValue register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x044
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_AIVAL[63:32]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
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
     <span class="documents-g.number.hex">
      0x048
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_AIVAL_RELOAD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AutoIncrValue Reload register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL-RELOAD--AutoIncrValue-Reload-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL-RELOAD--AutoIncrValue-Reload-register?lang=en" title="Holds the programmable offset value for the Automatic Increment timer view. The following table shows the bit assignments.">
      CNTP_AIVAL_RELOAD, AutoIncrValue Reload register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x04C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_AIVAL_CTL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xXXXX_XXXX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AutoIncrValue Control register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL-CTL--AutoIncrValue-Control-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-AIVAL-CTL--AutoIncrValue-Control-register?lang=en" title="Control register for the Automatic Increment timer view. The following table shows the bit assignments.">
      CNTP_AIVAL_CTL, AutoIncrValue Control register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x050
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0001
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer Configuration register. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CFG--Configuration-register?lang=en" href="/documentation/102803/0000/System-timer-components/System-timer-programmers-model/CNTP-CFG--Configuration-register?lang=en" title="Provides timer configuration information.">
      CNTP_CFG, Configuration register
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x054
     </span>
     -
     <span class="documents-g.number.hex">
      0xFCC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFD0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_PID4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0004
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID4.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFD4
     </span>
     -
     <span class="documents-g.number.hex">
      0xFDC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_PID0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B7
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID0.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_PID1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_PID2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_000B
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID2.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFEC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_PID3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID3.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CID0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_000D
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID0.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CID1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00F0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTP_CID2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0005
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID2.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFFC
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CNTP_CID3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B1
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Component ID3.
    </p>
   </td>
  </tr>
 </tbody>
</table>
