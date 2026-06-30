# ITS ACE5-Lite subordinate interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/ITS-ACE5-Lite-subordinate-interface>

### ITS ACE5-Lite subordinate interface

The ITS AMBA® ACE5-Lite subordinate interface has a configurable data width of 64 bits, 128 bits, 256 bits, 512 bits, or 1024 bits.

The ITS ACE5-Lite subordinate port contains only the GITS\_TRANSLATER register. See the [Arm® Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4](https://developer.arm.com/documentation/ihi0069/hb) for more information.

If the bypass switch configuration option is selected, the port accepts all ACE5-Lite traffic, and filters accesses to the ITS based on an address match set by the target\_address[ADDR\_WIDTH−17:0] ITS base address tie-off. Without the bypass switch, the upper bits of the address, 16 and above, are ignored, and the system address decoders must ensure that only relevant ITS writes arrive at the ITS. Writes to the ITS subordinate interface must set the awaddr\_its\_<num>\_s[16:0] signal to 0x0040, irrespective of whether the bypass switch is selected.

The ACE5-Lite subordinate interface ignores all awatop, a<x>snoop, a<x>cache, a<x>domain, and a<x>prot signals information other than to filter non-memory transactions such as atomics and cache maintenance operations, to ensure that it replies in a protocol-compliant manner.

The GIC-720AE uses the wstrb signal to determine the size of a transaction. The GIC rejects transactions where the strobes do not form a continuous block that is address aligned with the resultant size of the transaction.

To generate an LPI, the ITS requires the DeviceID of the issuing manager. For PCIe, the DeviceID is derived from the RequestorID.

The GIC-720AE supports 2 different methods for deriving the DeviceID with the ACE5-Lite subordinate interface:

- When using the MSI-64 configuration parameter, the write to GITS\_TRANSLATER is converted to 64-bit accesses at an unmapped system address and the DeviceID is transferred in the upper 32 bits of the access. In this case, only burst length 1, 64-bit ACE5-Lite writes are accepted.
- When not using MSI-64, the awuser\_its\_<num>\_s[did\_width−1:0] signal transports the DeviceID during the address (AW) phase of the register access. In this case, burst length 1, 32-bit or 16-bit writes are accepted.

These 2 modes cannot be mixed on a single ITS. The DeviceID must be transferred using a method that malicious software cannot spoof.

The ITS also supports a direct MSI interface, where MSIs are sent directly on an AXI5-Stream interface to the ITS. See [MSI delivery interface](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Interrupt-Translation-Service/MSI-delivery-interface?lang=en "The MSI delivery interface is a bidirectional AXI5-Stream interface for passing MSIs to an ITS for translation."). This interface can be configured alongside or instead of an ACE5-Lite subordinate interface.

If the bypass switch is configured, it includes a transaction tracker that ensures PCIe ordering requirements are met. The transaction tracker allows continuous downstream traffic including interleaved MSIs, unless the buffer slots become full. There are 2 buffers, `bypass_max_outstanding`, which specifies the number of concurrent downstream transactions allowed and `bypass_interrupt_count`, which specifies the number of concurrent MSIs that can be waiting for their prerequisite transactions to complete.

> ### Note
>
> - The ITS subordinate port contains only write-only registers, so the read channel always uses a simple transaction tracker that only allows transactions to one destination at a time.
> - If the Distributor and ITS both share the ACE5-Lite subordinate port, the port properties match those of the Distributor ACE5-Lite subordinate port, which [Distributor ACE5-Lite subordinate interface](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Distributor--GICD-/Distributor-ACE5-Lite-subordinate-interface?lang=en "The AMBA ACE5-Lite subordinate port on the GIC-720AE Distributor provides access to the entire register map except for the GITS_TRANSLATER register. The interface supports 64-bit, 128-bit, 256-bit, or 512-bit data widths.") describes.

The following table shows the acceptance capabilities of the ITS ACE5-Lite subordinate interface.



<table id="aba1432911916761__table.its_ace_lite_subordinate_acceptance_capabilites">
<caption>
<span class="documents-tablecap"><span class="documents-table--title-label">Table 1. </span>ITS <span>ACE5-Lite</span> subordinate interface acceptance capabilities</span>
</caption>
<colgroup>
<col span="1"/>
<col span="1"/>
<col span="1"/>
</colgroup>
<thead>
<tr>
<th class="documents-nocellnorowborder" colspan="1" id="d155976e243" rowspan="1">Attribute</th>
<th class="documents-nocellnorowborder" colspan="1" id="d155976e246" rowspan="1">With bypass switch</th>
<th class="documents-cell-norowborder" colspan="1" id="d155976e249" rowspan="1">Without bypass switch</th>
</tr>
</thead>
<tbody>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Combined acceptance capability</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read acceptance capability + Write acceptance capability</td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">3</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read acceptance capability</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>512</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1</td>
</tr>
<tr>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1">Read data reorder depth</td>
<td class="documents-nocellnorowborder" colspan="1" rowspan="1"><span>512</span></td>
<td class="documents-cell-norowborder" colspan="1" rowspan="1">1</td>
</tr>
<tr>
<td class="documents-row-nocellborder" colspan="1" rowspan="1">Write acceptance capability</td>
<td class="documents-row-nocellborder" colspan="1" rowspan="1"><code class="documents-parmname">bypass_max_outstanding</code>, but not exceeding 256</td>
<td class="documents-cellrowborder" colspan="1" rowspan="1">2</td>
</tr>
</tbody>
</table>



The ITS ACE5-Lite subordinate interface has an associated awakeup signal. To ensure that incoming traffic wakes the ITS correctly when it is clock gated hierarchically through the Q-Channel, the awakeup signal must be driven from a registered version of the awvalid and arvalid signals. To prevent spurious wake events, ensure that the awakeup signal is registered cleanly.
