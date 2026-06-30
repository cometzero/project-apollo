# GICD_ICLARn, Interrupt Class Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARn--Interrupt-Class-Registers>

### GICD\_ICLARn, Interrupt Class Registers

These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 60 registers, GICD\_ICLAR2-GICD\_ICLAR61.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

The Distributor provides up to 60 registers to support the first 960 SPIs. If you configure the GIC-720AE to use fewer than 960 SPIs, then it reduces the number of registers accordingly. For locations where interrupts are not implemented, the register is RAZ/WI. See also [GICD\_ICLARnE](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ICLARnE--Interrupt-Class-Registers-Extended?lang=en "These registers control whether a 1 of N SPI can target a core that is assigned to class 0 or class 1 group. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD_ICLAR0E-GICD_ICLAR63E.").

### Bit descriptions

Figure 1. GICD\_ICLARn bit assignments

![GICD_ICLARn bit assignments](images/0103-GICD_ICLARn-Interrupt-Class-Registers-img01.svg)



<table id="col1468508145817__tbl.gicd_iclar_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_ICLARn bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d154302e147" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d154302e150" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d154302e153" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]<p>Bits[2<code class="documents-option">x</code>+1:2<code class="documents-option">x</code>], for <code class="documents-option">x</code> = 0 to 15</p> </td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Class&lt;x&gt;</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Controls whether the 1 of N SPI can target a core, depending on the class group that the core is assigned to:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The SPI can target a core that is assigned to class 0 or class 1.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             The SPI can target a core that is assigned to class 1.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             The SPI can target a core that is assigned to class 0.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             The SPI cannot target a core that is assigned to class 0 or class 1.

           </dd>
</dl> <p>The SPI that a bit refers to, depends on its bit position and the base address offset of the GICD_ICLAR<code class="documents-option">n</code>, that is, SPI = 16×<code class="documents-option">n</code> + bit[number]/2.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_ICLARn is accessible only when the corresponding GICD\_IROUTERn.Interrupt\_Routing\_Mode == 1.
