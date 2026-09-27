# Trace Infrastructure

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration/Trace-Infrastructure>

### Trace Infrastructure

When DEBUGLEVEL = 2, CRSAS Ma1 provides a trace infrastructure that funnels all trace source from all processor cores to a single trace data stream. This stream is then replicated and one drives the ATB Trace interface that is expected to be picked up by a TPIU. The other stream is taken up by the ETB, allowing the trace data to be read by software or by an external debugger through the Debug Access Interface.

When DEBUGLEVEL < 2, CRSAS Ma1 does not provide any trace infrastructure.
