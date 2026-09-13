# Error containment

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Error-containment>

### Error containment

The DynamIQ Shared Unit-120AE (DSU-120AE) supports error containment, which means that an error is detected and not silently propagated.

Error containment also implies support for poisoning if there is a double error on an eviction. This ensures that the error of the associated data is reported when it is consumed.

Support for the Error Synchronization Barrier (ESB) instruction in the core also allows further isolation of imprecise exceptions that are reported when poisoned data is consumed.
