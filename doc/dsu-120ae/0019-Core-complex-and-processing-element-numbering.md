# Core, complex, and processing element numbering

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Core--complex--and-processing-element-numbering>

### Core, complex, and processing element numbering

A cluster contains two or more cores. The cluster can also contain two or more complexes which can be made up of either a single core or two cores. Because certain parts of the design, such as signal names and register bit values, depend on the number of cores and complexes within the cluster, a numbering system has been created.

Throughout this document, the following numbering is used for cores, Processing Elements (PEs), and complexes.

Core
:   The numbering of core instances in the cluster ranges from zero to CN, where CN has the value of the total number of cores minus one. This numbering also includes cores instantiated within a complex. For example, CN = 5 for a cluster comprised of two dual-core complexes and two standalone cores.

    For individual core instances, the term y is used, which ranges from zero to CN. For example, when referring to the second instance of a core, y = 1. The term y is called the core instance number. The instance numbering in different configurations and modes are explained as follows:

    - In Lock-configuration the core numbering is based on the number of logical core instances. A Lock-configuration cluster that consists of two core pairs has two logical cores and so the cores are numbered 0 and 1.
    - In Split-configuration and Mixed-configuration the core numbering is based on the number of physical core instances.
    - In Mixed-configuration, Lock-mode there is only one logical core active in each core pair and so the logical core numbering matches the physical numbering of the primary core in each core pair. In a Mixed-configuration, Lock-mode with two core pairs the numbering of the logical cores will be 0 and 2.

Complexes
:   The numbering of
    complex instances in the cluster ranges from zero to CX, where CX has the value of total number of
    complexes minus one. For example, CX = 1 for a cluster comprised of two
    complexes.
:   For individual complex instances, the term x is used, which ranges from zero to CX. For example, when referring to the second instance of a complex, x = 1. The term x is called the complex instance number. The instance numbering in different configurations and modes are explained as the follows:

    - In Lock-configuration the complex numbering is based on the number of logical complex instances. A Lock-configuration cluster that consists of two dual core complex pairs has two logical complexes and four logical cores and so the complexes are numbered 0 and 1 and the cores are numbered 0, 1, 2, 3.
    - In Split-configuration and Mixed-configuration the complex numbering is based on the number of physical complex instances.
    - In Mixed-configuration, Lock-mode there is only one logical complex active in each complex pair and so the logical complex numbering matches the physical numbering of the primary complex in each complex pair. In a Mixed-configuration, Lock-mode with 2 dual-core complex pairs the numbering of the logical complexes will be 0 and 2 and the numbering of the logical cores will be 0, 1, 4, 5.

Processing element
:   The Arm architecture allows for cores to support multiple Processing Elements (PEs).

    The DynamIQ Shared Unit-120AE (DSU-120AE) supports cores with multiple PEs. Where a reference to a core is made, the core could be a core with only one PE (single-threaded core) or multiple PEs (multi-threaded core).

    The parameter PE is the total number of PEs in the cluster, starting from one. This numbering also includes cores within complexes. For example, PE = 6 for a cluster comprised of two dual-core complexes and two standalone cores, with all cores having one PE each.

    For reference to individual PEs, the term z is used, which ranges from zero to PE-1. For example, when referring to the second PE, z = 1.

    > ### Note
    >
    > In the current
    > DSU-120AE, each
    > core only has one PE. Therefore, PE = CN+1.

For more information on the instance numbering for cores and complexes in the cluster, see RTL configuration process in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
