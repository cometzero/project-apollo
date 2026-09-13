# Cache slice and requester port selection

Source: <https://developer.arm.com/documentation/107721/0001/L3-cache/Cache-slices-and-power-portions/Cache-slice-and-requester-port-selection>

### Cache slice and requester port selection

For an implementation with more than one cache slice, requests are sent to a particular slice depending on the address and the memory attributes.

The mapping from address to slice is not configurable, but the mapping from address to requester port is configurable and can be independent from the slice mapping.
