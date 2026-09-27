# Document-specific conventions

Source: <https://developer.arm.com/documentation/102803/latest/Overview/Document-specific-conventions>

### Document-specific conventions

In addition to the Typographic Conventions section, there are document-specific conventions that apply.

### Text

Text between < and > is a label to be replaced with the actual name or value of the item. For example, CPU<n> where “n” is an instance number of either 0 or 1.

- Mathematical expressions are allowed within <> to offset the variable. For example, <NUMCPU+1>.
- <n> always denotes {0-<NUMCPU>}
- <m> always denotes {1-<NUMNPU-1>}

Text between { and } indicates a range to be replaced with the actual legal values. The allowed values can be:

- A range indicate by a start and end with a “-” or in-between. For example, {0-3} allows the any value between 0 and 3. One of the numbers can also be a variable. For example, {0-<NUMCPU>} where NUMCPU is a configuration value between 0 to 3.
- A list of discrete values indicated by a comma separate list. For example, {0,1,2,3} allows the value to be any one of those values. One of the discrete values can also be a range. For example, {0, 3-6, 9} is the same as writing {0, 3, 4, 5, 6, 9}.
- A variable which has constraints. For example, <x> where x is {0-3} or <x> where x is between 0 and 3. Allows x to take any value between 0 and 3.

In this specification the terms subsystem implementor and integrator are used. The definition of these terms are:

- Subsystem Implementer
  :   Person implementing a subsystem according to this specification. This does not include the physical implementation of an existing frontend implementation of a subsystem implementation.
- Subsystem Integrator
  :   Person integrating this implementation of the subsystem, into a wider SoC, for example, by adding expansion components to the expansion ports.

### Numbers

Numbers are normally written in decimal. Binary numbers are preceded by 0b, and hexadecimal numbers by 0x.

For both binary and hexadecimal numbers, where a bit is represented by the letter “x”, the value is irrelevant. For example, a value expressed as 0b1x can be either 0b11 or 0b10. To improve readability, long numbers can be written with an underscore separator between every four characters, for example, 0xFFFF\_0000\_0000\_0000.

### Signals

The level of a single bit asserted signal depends on whether the signal is active-HIGH or active-LOW. Asserted means:

- HIGH for active-HIGH
- LOW for active-LOW

A lowercase ‘n’ at the start or end of a signal name denotes an active-LOW signal.

The value of a multi-bit signal is defined using hexadecimal numbers.

When referring to bits within of a multi-bit signal, the following custom is used:

- <SIGNAL\_NAME>[BIT\_RANGE]

Where:

- SIGNAL\_NAME is the name of the signal being referred to.
- BIT\_RANGE is the bit range being referred to. If BIT\_RANGE is omitted, then the text is referring to the whole signal.

For example, when referring to the bit range 31:2 of Debug Access Interface address signal, the text would read:

- DEBUGPADDR[31:2]

### Registers

When referring to registers and fields, the following convention is used:

- <REGISTER\_NAME>.<FIELD\_NAME>[BIT\_RANGE]

Where:

- REGISTER\_NAME is the short name of the register being referred to.
- FIELD\_NAME is the name of the field within the register being referred to. If the FIELD\_NAME is omitted, then the text is referring to the whole register.
- BIT\_RANGE is the bit range, within the field, being referred to. If the BIT\_RANGE is omitted, then the text is referring to the whole field or to the whole register if FIELD\_NAME is omitted as well. When referring to the bit ranges of a field, the field starts at 0.

For example, when referring to the DESIGNER\_ID field of the SYSVERSION register, bits 1:0, the text would read:

- SYSVERSION.DESIGNER\_ID[1:0]

In register bit field description tables, the following abbreviations are used to describe the accessibility of each bit field:

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Register bit field abbreviations
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d111382e249" rowspan="1">
    <p>
     Abbreviation
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111382e253" rowspan="1">
    <p>
     Accessibility
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d111382e257" rowspan="1">
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
     R
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read Accessible
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Unless stated, these bit fields retain the value written to them until reset or powering down.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read and Write Accessible
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Unless stated, these bit fields retain the value written to them until reset or powering down.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read only
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These can only be read. Unless stated, any writes to these bit fields are ignored. This is similar to WI.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RAZ
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read as Zero
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These always return Zeros for reads. Unless stated, writes proceed as normal.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RAO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read as One
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These always return Ones for reads. Unless stated, writes proceed as normal.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read as Zero Write Ignores
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These always return Zeros for read and ignores writes.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RAZ/WO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Read as Zero Write Only
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These can only be written. These always return Zeros for reads.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Write Accessible
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Unless stated, these bit fields retain the value written to them until reset or powering down.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     WO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Write only
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These can only be written. Unless stated, any read from these bit fields returns zeros.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     WI
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Write Ignore
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These ignore writes. Unless stated, reads proceed as normal. This is similar to RO.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Write 1 to Set
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Each bit when written with one is set to one. Writing zeros to these are ignored.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1C
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Write 1 to Clear
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Each bit when written with one is cleared to zero. Writing zeros to these are ignored.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W0S
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Write 0 to Set
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Each bit when written with zero is set to one. Writing ones to these are ignored.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     W0C
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Write 0 to Clear
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Each bit when written with zero is cleared to zero. Writing ones to these are ignored.
    </p>
   </td>
  </tr>
 </tbody>
</table>

Unless stated otherwise, after a register bit field is modified by a register access, it retains its values until a reset is applied or power is lost.

In this specification areas of the design, register values or behaviours, that are described as IMPLEMENTATION DEFINED (IMPL\_DEF). It is up to the Subsystem Implementer what the value or behaviour is, but in certain situations the specification requires an implementation to select from a list of options. Each implementation must specify the behaviour or register values as part of its own specification.

In this specification areas of the design, register values or behaviours, are described as CONFIGURATION DEFINED (CFG\_DEF). The value or behaviour is dependent upon the configuration of the component.

Register values are defined using actual values that are written in or read from the registers. They are expressed as numbers, either as binary numbers or hexadecimal numbers. Alternatively, for single-bit values, they can be expressed as either 1 or 0, representing 0b1 and 0b0 respectively.
