# Distributor ACE5-Lite subordinate interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-subordinate-interface>

### Distributor ACE5-Lite subordinate interface

The AMBA® ACE5-Lite subordinate port on the GIC-720AE Distributor provides access to the entire register map except for the GITS\_TRANSLATER register. The interface supports 64-bit, 128-bit, 256-bit, or 512-bit data widths.

The GIC-720AE only accepts single beat accesses of the sizes for each register that are shown in the programmers model, see [Programmers model for GIC-720AE](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE?lang=en "All the GIC-720AE registers have names that are constructed of mnemonics that indicate the logical block that the register belongs to and the register function.").

When the GIC-720AE is a monolithic configuration without MSI-64 support, the Distributor and ITS both share an ACE5-Lite subordinate port, and the DeviceID for the ITS translation is taken from the awuser\_s[did\_width−1:0] signal. The value of the `did_width` parameter is set during silicon integration. For more information about the ITS, see [Interrupt Translation Service](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service?lang=en "The Interrupt Translation Service (ITS) provides a software mechanism for translating message-based interrupts into LPIs or vLPIs.").

The following table shows the acceptance capabilities of the Distributor ACE5-Lite subordinate interface. These acceptance capabilities also apply to the cross-chip ACE5-Lite subordinate interface.



<table id="aba1440083606115__table.distributor_ace_lite_subordinate_acceptance_capabilities">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>Distributor <span>ACE5-Lite</span> subordinate interface acceptance capabilities</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d10958e139" rowspan="1">Attribute</th>
<th class="documents-cell-norowborder" colspan="1" id="d10958e142" rowspan="1">Capability</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Combined acceptance capability</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read acceptance capability</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">2</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read data reorder depth</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Write acceptance capability</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">2</td>
</tr>
</tbody>
</table>



The GIC-720AE uses awatop\_s, a<x>cache\_s, a<x>domain\_s, and a<x>snoop\_s signals to detect cache maintenance operations that are responded to in a protocol-compliant manner but are otherwise ignored. The GIC-720AE also ignores other Cacheability, Shareability, and protection settings, except for the a<x>prot\_s[1] security signal.

If you are connecting to an AXI3 or AXI4 port, then awatop\_s, a<x>domain>\_s, a<x>snoop\_s, and, for AXI3, a<x>len[7:4] signals must all be tied LOW.

The GIC-720AE uses the wstrb signal to determine the size of a transaction. The GIC rejects transactions where the strobes do not form a continuous block that is address aligned with the resultant size of the transaction.

The GIC-720AE has a separate awakeup\_s signal to force the GIC to wakeup when it is hierarchically clock gated through the Q-Channel. The awakeup\_s signal must be connected to a cleanly registered version of (awvalid\_s | arvalid\_s signal) to ensure that the GIC does not request to be woken up due to incoming signal glitches.

The GIC-720AE address map has multiple pages. The number of pages and the address aliasing depends on your configuration. See [Register map pages](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Register-map-pages?lang=en "The GIC-720AE address map has multiple pages. The number of pages and the address aliasing depends on the GIC configuration.").

You must set up the system address map so that each core accesses the GICD page on its local chip at the same address. All other pages must be globally accessible, although access of pages on a remote chip by a core is expected to be rare.
