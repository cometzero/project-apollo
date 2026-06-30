# GITS_TYPER, ITS Type Register

Source: <https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-TYPER--ITS-Type-Register>

### GITS\_TYPER, ITS Type Register

This register returns information about the features that this ITS supports.

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

Figure 1. GITS\_TYPER bit assignments

![GITS_TYPER bit assignments](images/0153-GITS_TYPER-ITS-Type-Register-img01.svg)



<table id="gam1489161020344__tbl.gits_typer">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>GITS_TYPER bit descriptions</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d40312e139" rowspan="1">Bits</th>
<th class="documents-nocellnorowborder" colspan="1" id="d40312e142" rowspan="1">Name</th>
<th class="documents-cell-norowborder" colspan="1" id="d40312e145" rowspan="1">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[63:47]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[46]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">INV</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 1, to indicate that:

          <ul>
<li>The Device cache and Event cache are invalidated when writing to GITS_BASER0.</li>
<li>The Collection cache is invalidated when writing to GITS_BASER1.</li>
</ul> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[45:44]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, RAZ</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[43]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">nID</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether <span class="documents-keyword">GIC-720AE</span> supports individual doorbells:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             Individual doorbell is not supported.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[42:41]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SVPET</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b00</span>
</dt>
<dd>
             vPE table is not shared with Redistributors. This bit value occurs when the GIC does not support GICv4.1.

           </dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b01</span>
</dt>
<dd>
             vPE table is shared with the groups of Redistributors that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" title="This register returns the ITS affinity when the vPE table is shared with Redistributors.">GITS_MPIDR</a>.Aff3 indicates.

            <span> This bit value occurs for all configurations of the GIC except for a multichip configuration with <code class="documents-parmname">chip_affinity_select_level</code> == 2.</span>
</dd>
<dt class="documents-dlterm">
<span class="documents-g.number.bin">0b10</span>
</dt>
<dd>
             vPE table is shared with the groups of Redistributors that

            <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/ITS-control-register-summary/GITS-MPIDR--ITS-Affinity-Register?lang=en" title="This register returns the ITS affinity when the vPE table is shared with Redistributors.">GITS_MPIDR</a>.[Aff3, Aff2] indicate. This bit value occurs for a GIC multichip configuration with

            <code class="documents-parmname">chip_affinity_select_level</code> == 2.

           </dd>
</dl> <p>When this field is not 0, it reports the same value as the <a class="document-topic" document-topic-path="/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" href="https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-TYPER--Redistributor-Type-Register?lang=en" title="This register returns information about the features that this Redistributor supports.">GICR_TYPER</a>.CommonLPIAff field of the Redistributors it shares the table with.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[40]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VMAPP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Returns 1, to indicate a GICv4.1 <code>VMAPP</code> command layout.</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[39]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VSGI</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether the ITS supports direct injection of SGIs:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The ITS does not support direct injection of SGIs. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The ITS supports direct injection of SGIs. This value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[38]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">MPAM</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether the ITS supports Memory Partitioning and Monitoring (MPAM):

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             MPAM is not supported. This value occurs when

            <code class="documents-parmname">lpi_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             MPAM is supported. This value occurs when

            <code class="documents-parmname">lpi_support</code> == 1.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[37]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">VMOVP</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates the form of the <code>VMOVP</code> command:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             This bit value occurs when

            <code class="documents-parmname">gicv41_support</code> == 0.

           </dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             When software moves a vPE, then

            <span> it need only issue a <code>VMOVP</code> on one of the ITSs that has a mapping for that vPE. The</span> ITSList and Sequence Number fields in the

            <code>VMOVP</code> command are

            <span class="documents-archterm">RES0</span>. This bit value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[36]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CIL</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Collection ID limit:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The size of the Collection ID is set by the CIDBits field.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[35:32]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CIDBits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of Collection ID bits, minus 1.<p>Set by the <code class="documents-parmname">col_width</code> configuration parameter.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[31:24]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">HCC</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Hardware collection count:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Interrupt collections are held in external memory only.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[23:20]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved, returns 0</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[19]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">PTA</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Physical target addresses:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not support physical target addresses.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[18]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">SEIS</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">System error interrupts:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> does not support locally generated System Error interrupts.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[17:13]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">DevBits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of device identifier bits implemented, minus 1.<p>Set by the <code class="documents-parmname">did_width</code> configuration parameter.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[12:8]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">IDBits</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of interrupt identifier bits implemented, minus 1.<p>Set by the <code class="documents-parmname">vid_width</code> configuration parameter.</p> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[7:4]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">ITTEntrySize</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">The number of bytes for each entry, minus 1:

          <dl>
<dt class="documents-dlterm">
<span class="documents-g.number.hex">0x3</span>
</dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> supports a 4-byte ITT entry size.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[3]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">-</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Reserved</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[2]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">CCT</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Cumulative Collection tables:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             Total number of supported collections is determined by the number of collections that are held in memory only.

           </dd>
</dl> </td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">[1]</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Virtual</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">Indicates whether the ITS supports virtual LPIs and direct injection of virtual LPIs:

          <dl>
<dt class="documents-dlterm">
             0

           </dt>
<dd>
             The ITS does not support virtual LPIs or direct injection of virtual LPIs.

            <span> This bit value occurs when <code class="documents-parmname">gicv41_support</code> == 0.</span>
</dd>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The ITS supports virtual LPIs and direct injection of virtual LPIs. This bit value occurs when

            <code class="documents-parmname">gicv41_support</code> == 1.

           </dd>
</dl> <p>See the <a href="https://developer.arm.com/documentation/107627/latest" target="_blank"><span><cite>Learn the architecture - Generic Interrupt Controller v3 and v4, Virtualization</cite></span></a>.</p> </td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">[0]</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Physical</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">Physical LPIs:

          <dl>
<dt class="documents-dlterm">
             1

           </dt>
<dd>
             The

            <span class="documents-keyword">GIC-720AE</span> supports physical LPIs.

           </dd>
</dl> </td>
</tr>
</tbody>
</table>
