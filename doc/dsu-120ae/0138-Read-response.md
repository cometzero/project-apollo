# Read response

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/Read-response>

### Read response

The AXI manager can delay accepting a read data channel transfer by holding RREADY LOW for an indeterminate number of cycles.

RREADY can be deasserted LOW between read data channel transfers that form part of the same transaction.
