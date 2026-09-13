# Clocks

Source: <https://developer.arm.com/documentation/107721/0001/Clocks-and-resets/Clocks>

### Clocks

The DynamIQ Shared Unit-120AE (DSU-120AE) has a separate clock signal for each standalone core or complex. There are also separate clocks for the internal logic, and some of the external interfaces.

The following table describes the clock signals of the DSU-120AE.

<table id="tzi1776269051029__table_f1d_jjb_qhb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   <span class="documents-keyword">
    DSU-120AE
   </span>
   clock signals
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d180964e85" rowspan="1">
    Signal
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d180964e88" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      COREyCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The clocks for each of the
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     in the cluster that are not part of a
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     .
    </p>
    <p>
     y is the
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     instance number, for example,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CORE0CLK
      </span>
     </span>
     is the clock for
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     0.
    </p>
    <p>
     These signals clock all
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     logic, including L1 and L2 caches.
    </p>
    <p>
     For
     <span>
      Mixed-configuration
     </span>
     <span>
      Lock-mode
     </span>
     ,
     <span>
      Hybrid-mode
     </span>
     , and
     <span>
      Split-mode
     </span>
     the clocks for each of the
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     in a
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     pair must be driven with a clock of the same frequency and phase. In
     <span>
      Split-mode
     </span>
     and
     <span>
      Hybrid-mode
     </span>
     the clocks can be gated independently.
    </p>
    <p>
     In
     <span>
      Split-configuration
     </span>
     , all
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     clocks can have different frequencies.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      COMPLEXxCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The clocks for each
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     in the cluster. Each clock is connected to all
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     in the respective
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     .
    </p>
    <p>
     x is the
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     instance number, for example,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       COMPLEX0CLK
      </span>
     </span>
     is the clock for
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     0.
    </p>
    <p>
     For
     <span>
      Mixed-configuration
     </span>
     <span>
      Lock-mode
     </span>
     ,
     <span>
      Hybrid-mode
     </span>
     , and
     <span>
      Split-mode
     </span>
     the clocks for each
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     in a
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     pair must be driven with a clock of the same frequency and phase. In
     <span>
      Split-mode
     </span>
     and
     <span>
      Hybrid-mode
     </span>
     the clocks can be gated independently.
    </p>
    <p>
     In
     <span>
      Split-configuration
     </span>
     , all
     <span>
      <span class="documents-keyword">
       complex
      </span>
     </span>
     clocks can have different frequencies.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      SCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     This clock is used for the Snoop Control Unit (SCU), L3 memory system, and all the external interfaces, including AXI, CHI, and Accelerator Coherency Port (ACP).
    </p>
    <p>
     It is also used for
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     and complexes that are configured to run synchronously with the
     <span class="documents-keyword">
      DSU-120AE
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      PCLK
     </span>
    </span>
    (DebugBlock)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The clock for the DebugBlock.
    <blockquote id="tzi1776269051029__note_w2785ab1b9b1b3b3b7b7b3b1_w2786ab1b9b1b3b3b7b7b3_w2787ab1b9b1b3b3b7b7_w2788ab1b9b1b3b3b7_w2789ab1b9b1b3b3_w2790ab1b9b1b3_w2791ab1b9b1_w2792ab1b9_w2793ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     The DebugBlock and the
     <span>
      <span class="documents-keyword">
       DSU-120AE DynamIQ&trade; cluster
      </span>
     </span>
     both have
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PCLK
      </span>
     </span>
     inputs. You might choose to connect both of these signals to the same clock. Alternatively, if you are using a different clock to drive the DebugBlock than the
     <span>
      <span class="documents-keyword">
       DSU-120AE DynamIQ&trade; cluster
      </span>
     </span>
     , ensure that you place an asynchronous bridge between the two clock domains.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      PCLK
     </span>
    </span>
    (
    <span class="documents-keyword">
     DSU-120AE
    </span>
    cluster)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The clock for the debug interface in the
    <span>
     <span class="documents-keyword">
      DSU-120AE DynamIQ&trade; cluster
     </span>
    </span>
    <blockquote id="tzi1776269051029__note_w2794ab1b9b1b3b3b7b9b3b2_w2795ab1b9b1b3b3b7b9b3_w2796ab1b9b1b3b3b7b9_w2797ab1b9b1b3b3b7_w2798ab1b9b1b3b3_w2799ab1b9b1b3_w2800ab1b9b1_w2801ab1b9_w2802ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     The DebugBlock and the
     <span>
      <span class="documents-keyword">
       DSU-120AE DynamIQ&trade; cluster
      </span>
     </span>
     both have
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PCLK
      </span>
     </span>
     inputs. You might choose to connect both of these signals to the same clock. Alternatively, if driving the DebugBlock with a different clock to the
     <span>
      <span class="documents-keyword">
       DSU-120AE DynamIQ&trade; cluster
      </span>
     </span>
     , ensure that you place an asynchronous bridge between the two clock domains.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ATCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The clock for the ATB trace bus output from the
    <span class="documents-keyword">
     DSU-120AE
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      GICCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The clock for the Generic Interrupt Controller (GIC) AXI-Stream interface between the
    <span class="documents-keyword">
     DSU-120AE
    </span>
    and an external GIC
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      PERIPHCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The clock for the peripheral logic inside the
    <span class="documents-keyword">
     DSU-120AE
    </span>
    such as clock and power management logic and timers
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      PPUCLK
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The clock for the Power Policy Units (PPUs). The PPUs reside in their own clock domain, see
    <a class="document-topic" document-topic-path="/107721/0001/Clocks-and-resets/Clock-domains?lang=en" href="/documentation/107721/0001/Clocks-and-resets/Clock-domains?lang=en" title="The DynamIQ Shared Unit-120AE (DSU-120AE) has multiple clock domains. Each core-pair or complex-pair can be implemented in a separate clock domain.">
     Clock domains
    </a>
    .
   </td>
  </tr>
 </tbody>
</table>

For more information on core and complex clock signaling, see Functional integration in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

The clocks for the two cores in a core pair must be driven from the same clock source with the same frequency and phase. All other clocks can be driven fully asynchronously to each other. The DSU-120AE contains all the necessary synchronizing logic for crossing between clock domains. There are no clock dividers and no latches in the design. The entire design is rising-edge triggered.

### Lock configuration and lock-mode clock restrictions

Due to Lock configuration and Lock-mode timeout mechanisms, there is a constraint on the maximum clock ratio that is supported between any two clocks. The maximum supported clock frequency ratio is 20:1.

> ### Note
>
> - You can configure the cores to run synchronously to the L3 memory system, on a per-core pair basis at the build time configuration stage. If this option is chosen, the corresponding COREyCLK signals and COMPLEXxCLK signals (if applicable) are not present and the synchronous cores are run with SCLK.
> - The DebugBlock can be clocked by a different clock from the cluster PCLK. To allow this, you must add asynchronous bridges between the cluster and the DebugBlock.

Some external interfaces, such as the main CHI or AXI bus manager port, support a clock enable input to allow the external logic to run at a lower-synchronous frequency.

Only the clocks for the two cores in a core pair or the two complexes in a complex pair require a synchronous relationship. The relationship between the other clocks is designed to be fully asynchronous, however the DSU-120AE is designed with the following expectations achieve acceptable performance:

- The COREyCLK or COMPLEXxCLK can be dynamically scaled to match the performance requirements of that core pair.
- The two cores or complexes in a pair are driven either by the COREyCLK and COREyCLKCHK clocks, or they are driven by the COMPLEXxCLK and COMPLEXxCLKCHK clocks. The primary clocks and their CHK clocks must be the same frequency and in phase at all times. This means that any dynamic frequency scaling must be done to both cores or complexes in the pair.
- SCLK is recommended to run between the maximum COREyCLK or COMPLEXxCLK frequency and approximately half of the maximum COREyCLK or COMPLEXxCLK frequency.
- SCLK can run at synchronous 1:1 or 2:1 frequencies with the external interconnect, avoiding the need for an asynchronous bridge between them.
- The frequency of ATCLK must be determined based on the trace bandwidth of the system.
- GICCLK can be run at the same frequency as the interrupt controller that it connects to. This would typically be approximately 25% of the maximum COREyCLK or COMPLEXxCLK frequency.
- PCLK can run at the same frequency as the debug subsystem that it connects to. This would typically be approximately 25% of the maximum COREyCLK or COMPLEXxCLK frequency.
- The PERIPHCLK domain contains the architectural timers, and software performance can be impacted if reads to these registers take too long. Therefore, Arm® recommends that the PERIPHCLK frequency is at least 25% of the maximum COREyCLK or COMPLEXxCLK frequency.
- Arm® recommends that the PPUCLK clock frequency is at least 25% of the maximum COREyCLK or COMPLEXxCLK frequency. When implementing the retention power state controls for retention power and operating modes, retention entry and exit latency is limited by the PPUCLK clock frequency.

### Related information

- [Clock domains](/documentation/107721/0001/Clocks-and-resets/Clock-domains?lang=en "The DynamIQ Shared Unit-120AE (DSU-120AE) has multiple clock domains. Each core-pair or complex-pair can be implemented in a separate clock domain.")
- [DynamIQ Shared Unit-120AE configuration options](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-configuration-options?lang=en "You must configure the DynamIQ Shared Unit-120AE (DSU-120AE) RTL for your implementation requirements prior to hardware synthesis at build time configuration. Configuration for the DSU-120AE is carried out together with configuration for the cores in your cluster.")
