# GICD_IVIEWRnE, Interrupt View Registers Extended

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-IVIEWRnE--Interrupt-View-Registers-Extended>

### GICD\_IVIEWRnE, Interrupt View Registers Extended

These registers control whether an SPI is assigned to view 0, view 1, view 2, or view 3. Each register controls 16 SPIs and the GIC-720AE has 64 registers, GICD\_IVIEWR0E-GICD\_IVIEWR63E.

### Configurations

These registers are available only in configurations that support all of the following features:

- > 960 SPIs.
- Multi view, that is, when [GICD\_CFGID](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-CFGID--Configuration-ID-Register?lang=en "This register contains information that enables test software to determine if the GIC-720AE system is compatible.").VIEW == 1.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

The Distributor provides up to 64 registers to support the extended SPIs, 961-1984. If you configure the GIC-720AE to use fewer than 1984 SPIs, then it reduces the number of registers accordingly. For locations where interrupts are not implemented, the register is RAZ/WI.

### Bit descriptions

Figure 1. GICD\_IVIEWRnE bit assignments

![GICD_IVIEWRnE bit assignments](images/0116-GICD_IVIEWRnE-Interrupt-View-Registers-Extended-img01.svg)



<table id="zmo1516198299312__tbl.gicd_iviewr_n_e">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_IVIEWRnE bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d71310e154" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d71310e157" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d71310e160" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]<p>Bits[2<code class="documents-option">x</code>+1:2<code class="documents-option">x</code>], for <code class="documents-option">x</code> = 0 to 15</p> </td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">View&lt;x&gt;</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Controls the allocation of SPIs to a view:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             The SPI is assigned to view 0.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             The SPI is assigned to view 1.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             The SPI is assigned to view 2.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b11</span>
</dt>
<dd>
             The SPI is assigned to view 3.

           </dd>
</dl> <p>The SPI that a bit refers to, depends on its bit position and the base address offset of the GICD_IVIEWR<code class="documents-option">n</code>E, that is, SPI = 960 + 16×<code class="documents-option">n</code> + bit[number]/2.</p> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_IVIEWRnE is accessible only for view 0.
