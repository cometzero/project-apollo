# ROM tables

Source: <https://developer.arm.com/documentation/107721/0001/ROM-tables>

### ROM tables

The ROM tables hold the locations of debug components, which debuggers can use to determine which components are implemented. The DynamIQ Shared Unit-120AE (DSU-120AE) has three different types of ROM tables. There is a ROM table for DebugBlock components, a ROM table for the cluster components, and a ROM table for each standalone core or complex.

All the ROM tables comply with the [Arm® CoreSight™ Architecture Specification v3.0](https://developer.arm.com/documentation/ihi0029/latest). The ROM tables for the DSU-120AE contain locations for debug components, locations of some control and identification registers, and entry points for any sub-level ROM tables. For example, the cluster ROM table contains entry points for the ROM tables belonging to each core or complex in the cluster.

The debug components in the DSU-120AE include components for each core in the cluster, for example a Cross Trigger Interface (CTI) for each core in the cluster.

> ### Note
>
> For a cluster comprised of
> complexes or
> cores, the
> core numbering follows the
> core instance numbering, see
> [Core, complex, and processing element numbering](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Core--complex--and-processing-element-numbering?lang=en "A cluster contains two or more cores. The cluster can also contain two or more complexes which can be made up of either a single core or two cores. Because certain parts of the design, such as signal names and register bit values, depend on the number of cores and complexes within the cluster, a numbering system has been created.").

If a component is not included in your implementation, the corresponding ROM table entry indicates that the component is not present.

The following table lists the types of debug components that can be accessed for each ROM table in the DSU-120AE.

<table id="jjw1660577310093__table_bqb_jnt_bkb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Types of components listed in the ROM tables for the
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
   <th class="documents-cellrowborder" colspan="1" id="d144052e192" rowspan="1">
    ROM table
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d144052e195" rowspan="1">
    ROM table located in
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d144052e198" rowspan="1">
    Components
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DebugBlock
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DebugBlock
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <ul id="jjw1660577310093__ul_jdc_34t_bkb">
     <li>
      Cluster CTI
     </li>
     <li>
      CTI for each
      <span>
       <span class="documents-keyword">
        core
       </span>
      </span>
     </li>
     <li>
      Power control and status registers for the cluster
     </li>
     <li>
      Peripheral and component identification registers
     </li>
     <li>
      ROM table entry point for the Cluster ROM table
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cluster
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DebugBlock
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <ul id="jjw1660577310093__ul_cvd_1pt_bkb">
     <li>
      Cluster Performance Monitoring Unit (PMU)
     </li>
     <li>
      Cluster Embedded Logic Analyzer (ELA)
     </li>
     <li>
      ROM table entry points for each standalone
      <span>
       <span class="documents-keyword">
        core
       </span>
      </span>
      or
      <span>
       <span class="documents-keyword">
        complex
       </span>
      </span>
      .
     </li>
     <li>
      Power control and status registers for each standalone
      <span>
       <span class="documents-keyword">
        core
       </span>
      </span>
      or
      <span>
       <span class="documents-keyword">
        complex
       </span>
      </span>
      in the cluster.
     </li>
     <li>
      Peripheral and component identification registers
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Standalone core
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    See the Technical Reference Manual (TRM) for your
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    See the TRM for your
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
   </td>
  </tr>
 </tbody>
</table>
