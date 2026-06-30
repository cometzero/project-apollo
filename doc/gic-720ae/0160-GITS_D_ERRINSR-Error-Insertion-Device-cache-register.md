# GITS_D_ERRINSR, Error Insertion Device cache register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-D-ERRINSR--Error-Insertion-Device-cache-register>

### GITS\_D\_ERRINSR, Error Insertion Device cache register

This register can insert errors into the ITS Device cache RAM. You can use this register to test your error recovery software.

### Configurations

This register is available in all configurations that have one or more ITS blocks.

### Attributes

Width
:   64-bit

Functional group
:   See
    [ITS control register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary?lang=en "The GIC-720AE Interrupt Translation Service (ITS) functions are controlled through registers that are identified with the prefix GITS.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

The bit assignments within this register depend on whether a write access or read access occurs.

The following table shows the bit assignments for write accesses.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_D_ERRINSR bit assignments for writes</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d49830e131" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d49830e134" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d49830e137" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Set to 1, to start the error injection process. The GIC sets this bit to 0 when it completes the process.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62:61]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DisableWriteCheck</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Controls whether to include an encoding check:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Include an encoder check.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Disable an encoder check.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59:48]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[47:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ADDR</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Address</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ERRINS2VALID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Controls whether the second error is valid:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The ERRINS2LOC field is not valid.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The ERRINS2LOC field is valid.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[30:25]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[24:16]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ERRINS2LOC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Sets the address location of the second error.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[15]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ERRINS1VALID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Controls whether the first error is valid:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The ERRINS1LOC field is not valid.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The ERRINS1LOC field is valid.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[14:9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[8:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">ERRINS1LOC</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Sets the address location of the first error.</td>
</tr>
</tbody>
</table>



The following table shows the bit assignments for read accesses.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 2. </span>GITS_D_ERRINSR bit assignments for reads</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d49830e362" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d49830e365" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d49830e368" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Valid</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the error injection process is complete:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Error injection process is complete.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Error injection process is in progress.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[62:61]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Status</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates if the error injection process was successful, and is valid only when Valid == 0:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The GIC performed the error injection process.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             An out-of-range error occurred. To fix this error, check that the RAM ID and the error locations are correct.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             A coincident error occurred.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             An encoder or decoder mismatch occurred.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[60]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RAM_Present</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether a RAM with ECC is present:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             RAM with ECC is present.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[59:48]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[47:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">RAM_MAX</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns the maximum address of the RAM.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:9]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1"><span class="documents-archterm">RES0</span></td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[8:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">RAM WIDTH</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Returns the highest maximum bit width of the RAM. For example, a value of 15 indicates a 16-bit wide RAM.</td>
</tr>
</tbody>
</table>



### Accessibility

If [GICD\_SAC](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-SAC--Secure-Access-Control-register?lang=en "This register allows Secure software to grant Non-secure software with access to some GIC-720AE Secure features. It also controls whether Secure PMU events are visible to Non-secure software. For configurations that support multi view, it controls which view can access the GICP registers.").GICTNS == 0, then GITS\_D\_ERRINSR is accessible only by Secure accesses.

For GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1, GITS\_D\_ERRINSR is accessible only for view 0.
