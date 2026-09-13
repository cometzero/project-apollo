# Supported standards and specifications

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Supported-standards-and-specifications>

### Supported standards and specifications

The DynamIQ Shared Unit-120AE (DSU-120AE) complies with the Arm®v9.2-A architecture and all previous Arm®v8‑A architectures up to Arm®v8.7‑A.

> ### Note
>
> The
> DSU-120AE is compatible with the architecture for the supported
> cores in the cluster. See the section
> Supported standards and specifications in your
> core Technical Reference Manual (TRM) for a list of specific architectural versions and features that the
> cores support.

The DSU-120AE complies with the architectures listed in the following table.

<table id="akh1660577208264__table_kcd_pxr_k3b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Standards and specifications support in the
   <span class="documents-keyword">
    DSU-120AE
   </span>
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d362668e123" rowspan="1">
    Standard of specification
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d362668e126" rowspan="1">
    Version
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d362668e129" rowspan="1">
    Notes
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-keyword">
     Arm
    </span>
    architecture
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span>
      <span class="documents-keyword">
       Arm&reg;v9.2-A
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The
     <span class="documents-keyword">
      DSU-120AE
     </span>
     supports
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     based on the
     <span>
      <span class="documents-keyword">
       Arm&reg;v9.2-A
      </span>
     </span>
     architecture. These
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     also support previous
     <span>
      <span class="documents-keyword">
       Arm&reg;v8‑A
      </span>
     </span>
     architectures up to
     <span>
      <span class="documents-keyword">
       Arm&reg;
      </span>
      <span class="documents-keyword">
       v8.7‑A
      </span>
     </span>
     , dependent on the
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     .
    </p>
    <p>
     See the section
     <cite>
      Supported standards and specifications
     </cite>
     in your
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     Technical Reference Manual (TRM) for details.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FEAT_RAS, Reliability, Availability, and Serviceability (RAS)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    RAS v8.4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    supports RAS features that conform to the v8.4 RAS architecture, see
    <a class="document-topic" document-topic-path="/107721/0001/RAS-extension-support?lang=en" href="/documentation/107721/0001/RAS-extension-support?lang=en" title="The DynamIQ Shared Unit-120AE (DSU-120AE) supports the Reliability, Availability, Serviceability (RAS) Extension, including all extensions up to Armv9.0-A. You can optionally enable Error Correcting Code (ECC) support for the L3 cache RAMs and snoop filter RAMs at build time configuration.">
     RAS extension support
    </a>
    .
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Advanced Microcontroller Bus Architecture (AMBA)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <ul id="akh1660577208264__ul_f1g_5vl_xvb">
     <li>
      AMBA 5 CHI Issue E
     </li>
     <li>
      AMBA AXI5 Issue H
     </li>
     <li>
      <p>
       AMBA APB5 Issue D
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    For more information on the AMBA protocols supported by the
    <span class="documents-keyword">
     DSU-120AE
    </span>
    interfaces, see
    <a class="document-topic" document-topic-path="/107721/0001/Technical-overview/Interfaces?lang=en" href="/documentation/107721/0001/Technical-overview/Interfaces?lang=en" title="The DynamIQ Shared Unit-120AE (DSU-120AE) manages all the external interfaces to the System on Chip (SoC) including those from the cores and complexes in the cluster.">
     Interfaces
    </a>
    .
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-keyword">
     CoreSight&trade;
    </span>
    architecture
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    v3.0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     For more information on
     <span class="documents-keyword">
      CoreSight&trade;
     </span>
     architecture, see the
     <cite>
      <span>
       <a href="https://developer.arm.com/documentation/ihi0029/latest" target="_blank">
        <span class="documents-keyword">
         Arm&reg;
        </span>
        <span class="documents-keyword">
         CoreSight&trade;
        </span>
        Architecture Specification v3.0
       </a>
      </span>
     </cite>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Debug
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     <span class="documents-keyword">
      Arm&reg;v9.2-A
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span>
      <span class="documents-keyword">
       Arm&reg;v9.2-A
      </span>
     </span>
     architecture that is implemented with
     <span>
      <span class="documents-keyword">
       Arm&reg;
      </span>
      <span class="documents-keyword">
       v8.4-A
      </span>
     </span>
     Debug architecture support and
     <span>
      <span class="documents-keyword">
       Arm&reg;
      </span>
      <span class="documents-keyword">
       v8.3-A
      </span>
     </span>
     FEAT_DoPD, Debug over PowerDown support.
    </p>
    <p>
     See FEAT_DoPD in the
     <cite>
      <span>
       <a href="https://developer.arm.com/documentation/ddi0487/latest/" target="_blank">
        <span class="documents-keyword">
         Arm&reg;
        </span>
        Architecture Reference Manual for A-profile architecture
       </a>
      </span>
     </cite>
     for information on this architectural feature.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FEAT_GICv4p1, Generic Interrupt Controller (GIC) architecture CPU interface and Stream Protocol interface.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     GICv4.1
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The
     <span class="documents-keyword">
      DSU-120AE
     </span>
     uses Affinity level 1 to distinguish between different
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     . This level is not supported by some interrupt controllers, such as GIC-500.
    </p>
    <p>
     For information on FEAT_GICv4p1, see
     <cite>
      <span>
       <cite>
        <span>
         <a href="https://developer.arm.com/documentation/ihi0069/latest/" target="_blank">
          <span class="documents-keyword">
           Arm&reg;
          </span>
          Generic Interrupt Controller Architecture Specification, GIC architecture version 3 and version 4
         </a>
        </span>
       </cite>
      </span>
     </cite>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Performance Monitoring Unit (PMU)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    PMUv3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
 </tbody>
</table>

### Related information

- [DynamIQ cluster shared logic components](/documentation/107721/0001/Technical-overview/DynamIQ-cluster-shared-logic-components?lang=en "The DynamIQ cluster shared logic includes the following components:")
- [Interfaces](/documentation/107721/0001/Technical-overview/Interfaces?lang=en "The DynamIQ Shared Unit-120AE (DSU-120AE) manages all the external interfaces to the System on Chip (SoC) including those from the cores and complexes in the cluster.")
