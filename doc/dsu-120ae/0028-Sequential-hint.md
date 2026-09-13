# Sequential hint

Source: <https://developer.arm.com/documentation/107721/0001/Technical-overview/Interfaces/Sequential-hint>

### Sequential hint

The bus manager ports provide speculative information about the probability of a sequential access to the other half of an aligned 128-byte range, close in time to this access. Your DRAM controller could use this hint to optimize accesses. When this bit is high, it indicates that the core has identified that there is a high probability that a sequential access might be requested soon.

The sequential hint information is provided as a source sideband signal on either the CHI or AXI bus manager ports.
