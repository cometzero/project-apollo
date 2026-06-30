# GICD_TYPER2, Interrupt Controller Type Register 2

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER2--Interrupt-Controller-Type-Register-2>

### GICD\_TYPER2, Interrupt Controller Type Register 2

This register returns the number of bits that GIC-720AE uses for a vPEID.

### Configurations

This register is available when `gicv41_support` == 1.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

There are no usage constraints.

### Bit descriptions

Figure 1. GICD\_TYPER2 bit assignments

![GICD_TYPER2 bit assignments](images/0087-GICD_TYPER2-Interrupt-Controller-Type-Register-2-img01.svg)

In the following table, the View column is applicable only for GIC configurations that support multi view, that is when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1.



<table>
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_TYPER2 bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d181701e150" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d181701e153" rowspan="1">Name</th>
<th class="documents-nocellnorowborder" colspan="1" id="d181701e156" rowspan="1">Description</th>
<th class="documents-cell-norowborder" colspan="1" id="d181701e159" rowspan="1">View</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VIL</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Returns the number of bits that <span class="documents-keyword">GIC-720AE</span> can use for a vPEID:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
<span class="documents-keyword">GIC-720AE</span> supports 16 bits of vPEID.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
<span class="documents-keyword">GIC-720AE</span> supports GICD_TYPER2.VID + 1 bit of vPEID.

           </dd>
</dl> <p>If <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a>.DVIS == 0, then this bit returns zero.</p> </td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">0 and 1 only. Returns zero for views 2 and 3.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[6:5]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Reserved, <span class="documents-archterm">RES0</span>.</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">-</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[4:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">VID</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Returns the value of the <code class="documents-parmname">vpe_width</code> configuration parameter. Values above <span class="documents-g.number.hex">0xF</span> are reserved.<p>If <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-TYPER--Interrupt-Controller-Type-Register?lang=en" title="This register returns information about the configuration of the GIC-720AE. You can use this register to determine the number of Security states, the number of INTIDs, and the number of processor cores that the GIC supports.">GICD_TYPER</a>.DVIS == 0, then this field returns zero.</p> </td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">0 and 1 only. Returns zero for views 2 and 3.</td>
</tr>
</tbody>
</table>
