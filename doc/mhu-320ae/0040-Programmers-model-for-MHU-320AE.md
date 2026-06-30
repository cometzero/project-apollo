# Programmers model for MHU-320AE

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE>

### Programmers model for MHU-320AE

The MHU-320AE consists of a MHU Sender component, a MHU Receiver component, and an optional bridge component. The MHU Sender and MHU Receiver is accessed through memory‑mapped registers for configuration, topology, and status information. Depending on the configuration, these are accessed via either APB or ACE‑Lite reads and writes.

In configurations with `FUSA_PRESENT` == 1, each FMU present has its own APB programming interface in addition to the MHU Sender and MHU Receiver programming interfaces.

The base address of the configuration registers is not fixed and can be different for any particular system implementation. The offset of each register from the configuration base address is fixed.

When accessing the configuration registers, do not attempt to access reserved or unused address locations. Attempting to access these locations can result in unpredictable behavior. Unless otherwise stated in the accompanying text:

- Do not modify undefined register bits.
- Ignore undefined register bits on reads.
- All register bits are reset to 0 by a system or Cold reset.

Each register has an associated access type. The MHU-320AE registers use the following access type abbreviations:

RW
:   Read and write

RO
:   Read only

WO
:   Write only

RAZ
:   Read as zero

WI
:   Write ignored

Some bit positions in registers are described as reserved. These bit positions have the following access types:

- RAZ/WI in an RW register
- RAZ in an RO register
- WI in a WO register

The MHU-320AE registers are accessed using the APB completer or ACE‑Lite subordinate interfaces. Accesses to unmapped or reserved registers are WI or RAZ. Non‑secure accesses to Secure registers are WI or RAZ.

MHU-320AE contains several control registers that enable software to modify the behavior of the product. Usually, programming the control registers immediately impacts the execution of transactions that flow through MHU-320AE.

MHU-320AE provides a mechanism for software to discover the configuration of the product. For more information, see [Discovery](/documentation/107612/0001/Programmers-model-for-MHU-320AE/Discovery?lang=en "Discovery is an algorithm that software can use to determine the structure of the MHU-320AE configuration as the system boots. Therefore, software can determine the structure of the MHU-320AE domains, components, and subfeatures without previous knowledge of the configuration.").
