# ​Chapter D8 The AArch64 Virtual Memory System Architecture

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture>

### Chapter D8 The AArch64 Virtual Memory System Architecture

This chapter provides a system level view of the AArch64 *Virtual Memory System Architecture* (VMSA), the memory system architecture of an A-profile implementation that is executing in AArch64 state. It contains the following sections:

- [Address translation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-1-Address-translation?lang=en#mdsec_address_translation)
- [Translation process](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-2-Translation-process?lang=en#mdsec_translation_process)
- [Translation table descriptor formats](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-3-Translation-table-descriptor-formats?lang=en#mdsec_translation_table_descriptor_formats)
- [Memory access control](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-4-Memory-access-control?lang=en#mdsec_memory_access_control)
- [Hardware updates to the translation tables](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-5-Hardware-updates-to-the-translation-tables?lang=en#mdsec_hardware_updates_to_the_translation_tables)
- [Memory region attributes](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-6-Memory-region-attributes?lang=en#mdsec_memory_region_attributes)
- [Other descriptor fields](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-7-Other-descriptor-fields?lang=en#mdsec_other_descriptor_fields)
- [Address tagging](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-8-Address-tagging?lang=en#mdsec_address_tagging)
- [Logical Address Tagging](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-9-Logical-Address-Tagging?lang=en#mdsec_mte_tagging)
- [Pointer authentication](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-10-Pointer-authentication?lang=en#mdsec_pointer_authentication)
- [Checked Pointer Arithmetic](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-11-Checked-Pointer-Arithmetic?lang=en#mdsec_checked_pointer_arithmetic)
- [Memory Encryption Contexts extension](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-12-Memory-Encryption-Contexts-extension?lang=en#mdsec_mec_extension)
- [Virtualization Host Extensions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-13-Virtualization-Host-Extensions?lang=en#mdsec_virtualization_host_extensions)
- [Nested virtualization](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-14-Nested-virtualization?lang=en#mdsec_nested_virtualization)
- [Memory aborts](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-15-Memory-aborts?lang=en#mdsec_memory_aborts)
- [Translation Lookaside Buffers](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-16-Translation-Lookaside-Buffers?lang=en#mdsec_translation_lookaside_buffers)
- [TLB maintenance](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-17-TLB-maintenance?lang=en#mdsec_tlb_maintenance)
- [Caches](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-18-Caches?lang=en#mdsec_caches)
- [Pseudocode description of VMSA address translation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-19-Pseudocode-description-of-VMSA-address-translation?lang=en#mdsec_pseudocode_description_of_vmsa_address_translation)
