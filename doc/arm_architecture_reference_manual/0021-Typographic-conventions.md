# Typographic conventions

Source: <https://developer.arm.com/documentation/ddi0487/mc/Preface/Conventions/Typographic-conventions>

##### Typographic conventions

The typographical conventions are:

*italic*
:   Introduces special terminology, and denotes citations.

bold
:   Denotes signal names, and is used for terms in descriptive lists, where appropriate.

`monospace`
:   Used for assembler syntax descriptions, pseudocode, and source code examples.

    Also used in the main text for instruction mnemonics and for references to other items appearing in assembler syntax descriptions, pseudocode, and source code examples.

SMALL CAPITALS
:   Used in body text for a few terms that have specific technical meanings, and are defined in the [Glossary](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#part_glossary).

Colored text
:   Indicates a link. This can be:

    - A URL, for example <https://developer.arm.com>.
    - A link, to a chapter or appendix, or to a glossary entry, or to the section of the Manual that defines the colored term, for example [Simple sequential execution](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfdijc) or [SCTLR](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions/-G8-2-General-system-control-registers/-G8-2-127-SCTLR--System-Control-Register?lang=en#reg_aarch32_sctlr).

{ and }
:   Braces, { and }, have two distinct uses:

    Optional items
    :   In syntax descriptions braces enclose optional items. In the following example they indicate that the `<shift>`parameter is optional:

        ```
            ADD <Wd|WSP>, <Wn|WSP>, #<imm>{, <shift>}
        ```

        Similarly, they can be used in generalized field descriptions, for example [TCR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#tcr_elx).{I}PS refers to a field in the [TCR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#tcr_elx) registers that is called either IPS or PS.

    Sets of items
    :   Braces can be used to enclose sets. For example, [HCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-61-HCR-EL2--Hypervisor-Configuration-Register?lang=en#reg_aarch64_hcr_el2).{E2H, TGE} refers to a set of two register fields, [HCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-61-HCR-EL2--Hypervisor-Configuration-Register?lang=en#reg_aarch64_hcr_el2).E2H and [HCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-61-HCR-EL2--Hypervisor-Configuration-Register?lang=en#reg_aarch64_hcr_el2).TGE.

Notes
:   Notes are formatted as:

    > #### Note
    >
    > This is a Note.

    In this Manual, Notes are used only to provide additional information, usually to help understanding of the text. While a Note might repeat architectural information given elsewhere in the Manual, a Note never provides any part of the definition of the architecture.
