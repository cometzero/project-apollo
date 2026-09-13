# ​0x8173, CAS_FAR_SPEC, Atomic memory Operation speculatively executed, Compare and Swap far

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8173--CAS-FAR-SPEC--Atomic-memory-Operation-speculatively-executed--Compare-and-Swap-far>

##### `0x8173`, CAS\_FAR\_SPEC, Atomic memory Operation speculatively executed, Compare and Swap far

The counter counts each Compare and Swap operation counted by [CAS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8174--CAS-SPEC--Atomic-memory-Operation-speculatively-executed--Compare-and-Swap?lang=en#event_cas_spec) that does not execute locally to the PE.

The definition of locally is IMPLEMENTATION DEFINED. Operations counted by [CAS\_FAR\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8173--CAS-FAR-SPEC--Atomic-memory-Operation-speculatively-executed--Compare-and-Swap-far?lang=en#event_cas_far_spec) do not generate [CAS\_NEAR\_PASS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8171--CAS-NEAR-PASS--Atomic-memory-Operation-speculatively-executed--Compare-and-Swap-pass?lang=en#event_cas_near_pass) or [CAS\_NEAR\_FAIL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8170--CAS-NEAR-FAIL--Atomic-memory-Operation-speculatively-executed--Compare-and-Swap-fail?lang=en#event_cas_near_fail) events.
