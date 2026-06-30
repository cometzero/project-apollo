# GICD_ISERRRn, Interrupt Set Error Registers

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary/GICD-ISERRRn--Interrupt-Set-Error-Registers>

### GICD\_ISERRRn, Interrupt Set Error Registers

These registers can set the error status of an SPI or return the error status of an SPI. Each register monitors 32 SPIs and the GIC-720AE has 30 registers, GICD\_ISERRR1-GICD\_ISERRR30. Software can use these registers to test the operation of its interrupt error clear function.

When multi view support is enabled, the error that is set depends on the view:

- Accesses to view 0 set the View Error, Group Error, and Error bits.
- Accesses to view 1, 2, or 3 set the Group Error and Error bits.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Functional group
:   See
    [Distributor registers (GICD/GICDA) summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Distributor-registers--GICD-GICDA--summary?lang=en "The GIC-720AE Distributor functions are controlled through the Distributor registers identified with the prefix GICD. The Distributor Alias registers are identified with the prefix GICDA.") for the address offset, type, and reset value of this register.

### Usage constraints

The Distributor provides up to 30 registers to support 960 SPIs. If you configure the GIC-720AE to use fewer than 960 SPIs, it reduces the number of registers accordingly. For locations where interrupts are not implemented, the register is RAZ/WI.

### Bit descriptions

Figure 1. GICD\_ISERRRn bit assignments

![GICD_ISERRRn bit assignments](images/0106-GICD_ISERRRn-Interrupt-Set-Error-Registers-img01.svg)



<table id="zhk1489160994927__tbl.gicd_iserrr_n">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GICD_ISERRRn bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d2152e152" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d2152e155" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d2152e158" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[31:0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Status</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Indicates whether an SPI is in an error state:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             If read, the SPI is not in an error state and programming is valid. Writing 0 has no effect.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             If read, the SPI is in an error state and programming is not valid. Writing 1 sets the error and contains the SPI.

           </dd>
</dl> <p>The SPI that a bit refers to, depends on its bit position and the base address offset of the GICD_ISERRR<code class="documents-option">n</code>, that is, SPI = 32×<code class="documents-option">n</code> + bit[number].</p> </td>
</tr>
</tbody>
</table>



### Accessibility

GICD\_ISERRRn is accessible only by Secure accesses.
