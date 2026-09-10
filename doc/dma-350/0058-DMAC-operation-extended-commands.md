# DMAC operation extended commands

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-extended-commands>

### DMAC operation extended commands

This section contains an overview of DMA-350 operation extended commands.

- **[Transfer type 2D](/documentation/102482/0000/DMAC-operation/DMAC-operation-extended-commands/Transfer-type-2D?lang=en)**
   The 2D transfers copies image-related data in the same format in the X and Y direction from one location to the other. The 2D operation contains extra registers for YSIZE, which defines the number of XSIZE-wide lines used in the copy.
- **[WRAP for 2D](/documentation/102482/0000/DMAC-operation/DMAC-operation-extended-commands/WRAP-for-2D?lang=en)**
   The WRAP operations extend the normal 2D copy by allowing different size and arrangement for the destination. The SRCXSIZE and SRCYSIZE parameters of the source can be mapped to a DESXSIZE / DESYSIZE destination location where the sizes can be the same or different between source and destination. Mapping the parameters results in having smaller or larger destination location, therefore requiring different wrap types. This allows reshaping the source data to the destination and also allows filling borders with a predefined fill value.
- **[Templated transfers](/documentation/102482/0000/DMAC-operation/DMAC-operation-extended-commands/Templated-transfers?lang=en)**
   The templated transfer feature allows 1D transfers to selectively copy data using predefined patterns. The patterns are defined by template registers that describe repetitive bit-mask of addresses to be transferred.
