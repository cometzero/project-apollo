# Multiple CHI bus requester port configurations

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/Multiple-CHI-bus-requester-port-configurations>

### Multiple CHI bus requester port configurations

You can configure the DynamIQ Shared Unit-120AE (DSU-120AE) to have one, two, three, or four CHI bus requester ports, at build time configuration, to give a range of bandwidth options. Transactions from the cores are routed to one of the CHI bus requester ports based on the transaction type, memory type, and transaction address.

The DSU-120AE also supports a configurable address target group methodology for the CHI bus requester ports. The address target groups are used to optimize the interconnect connectivity between the bus requester ports and the system.

Transactions are grouped into designated address target groups based on the target address, the memory type, and a set of configuration signals. Assigning a particular transaction to a group depends on the memory type targeted, for example Device transactions might be assigned to address target group 0. The address target groups are then assigned to different physical bus requester ports based on a pre-defined mapping. At reset time, any of the bus requester ports can optionally be disabled using a configuration signal which then alters the mapping between the address target groups and the remaining bus requester ports accordingly. Once the address target groups are mapped to bus requester ports, the address target groups are managed through the bus requester ports.
