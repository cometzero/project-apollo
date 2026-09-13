# Bandwidth partitioning

Source: <https://developer.arm.com/documentation/107721/0001/L3-cache/Bandwidth-partitioning>

### Bandwidth partitioning

The DynamIQ Shared Unit-120AE (DSU-120AE) provides an optional mechanism to share bandwidth differently between different sources, based on the Memory System Resource Partitioning and Monitoring (MPAM) bandwidth partitioning. This is controlled using MPAM.

By default, the bandwidth available within the DynamIQ Shared Unit-120AE (DSU-120AE) should be distributed approximately fairly between all cores making requests. However, there might be circumstances when more control is required. For example, in a dual core cluster with two Accelerator Coherency Port (ACP) interfaces, each core and each ACP interface would get one quarter of the bandwidth. But, allowing both ACP interface, collectively to use up half of the overall bandwidth might impact on the performance of the cores. Therefore, the ACP could be restricted to using only a smaller proportion of the overall bandwidth.

A memory-bandwidth proportional-stride partitioning scheme is used, see  [Arm® Memory System Resource Partitioning and Monitoring (MPAM) System Component Specification](https://developer.arm.com/documentation/ihi0099/latest/).

Bandwidth partitioning allows you to control how bandwidth is split when the demand for bandwidth is greater than the bandwidth available.

Each MPAM PARTID has a separate MPAMCFG\_MBW\_PROP register, which contains an enable bit and the STRIDEM1 field. If the bandwidth partitioning is enabled for that MPAM PARTID, the 6-bit STRIDEM1 value controls how much bandwidth to give to ACP transactions and cores that are using that PARTID.

The STRIDEM1 value is the reciprocal of the relative bandwidth required, minus one. For example, if three PARTIDs are all contending for bandwidth and you want to assign bandwidths in the ratio 100:125:1000, you could program STRIDEM1 values of 9, 7, and 0, respectively. This is because 1/(9+1) : 1/(7+1) : 1/(0+1) gives the required ratio. As the numbers are relative, other values can also be used to give the same bandwidth ratio, such as 19, 15, and 1.

The bandwidth partitioning mechanism is work-conserving, which means that enabling it does not reduce the total bandwidth that the cluster uses. The scheme only regulates PARTIDs that are using more than their fair share of bandwidth. Therefore, if a PARTID is not attempting to use much bandwidth then this does not reduce the ability of other PARTIDs to use that bandwidth.

> ### Note
>
> Because of the following two reasons, the ratio of the bandwidth for certain PARTIDs might not be in the programmed ratio:
>
> - A PARTID that is already getting all the bandwidth that it wants does not gain more bandwidth with a lower STRIDEM1 value.
> - If there is spare bandwidth, the bandwidth partitioning does not regulate the bandwidth of any PARTIDs.

The STRIDEM1 value also affects the transaction latency in a congested system. This is because if a process has been given a small share of the bandwidth and it is attempting to use more bandwidth than it is allowed, its memory requests will have to wait to be arbitrated. You can give processes that are low bandwidth but high priority a very low STRIDEM1 value so that they have the lowest possible latency. As the scheme is work-conserving, the large bandwidth available to the process is not wasted if the process does not use it.

You can use a single PARTID for a software process that spans multiple cores or generates ACP transactions. The bandwidth mechanism considers the total bandwidth from all sources when regulating the bandwidth of a PARTID.

Where possible, software should avoid either:

- Using a mixture of PARTIDs with very different STRIDEM1 values on two cores in the same complex.
- Using a mixture of PARTIDs with very different STRIDEM1 values on an ACP interface.

When programmed like this, in certain situations the bandwidth that is achieved is a compromise. Therefore, some partitions might get more bandwidth than expected and others might get less bandwidth than expected.

For the best functioning of the mechanism, if a CHI system interconnect is not able to accept new transactions from the DSU-120AE, the interconnect should stop returning link-layer credits on the CHI REQ channel. The DSU-120AE will pick the most important transaction to send next. The interconnect should avoid generating large numbers of RetryAck responses in this situation because that reduces the ability of the DSU-120AE to control the order transactions are processed.

The cluster MPAM registers are used to configure the bandwidth QoS, see [External MPAM registers summary](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary?lang=en "The cluster Memory System Resource Partitioning and Monitoring (MPAM) registers are only accessible from memory-mapped accesses on the utility bus.").
