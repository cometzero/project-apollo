# Interrupt protection initialization

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization>

### Interrupt protection initialization

When the GIC exits reset, the interrupt protection starts a Built-In Self Test (BIST) to check for any errors. We recommend that software checks that the BIST check was successful.

When BIST completes, that is page-2 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").BISTBusy == 0, we recommend that software reads page-2 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").error\_BIST\_valid, to check for any errors:

error\_BIST\_valid == 0
:   BIST detected no errors. See [Post-BIST initialization](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en#rpq1523546077672__section.post_BIST_init) for the remainder of the initialization process.

error\_BIST\_valid == 1
:   BIST detected an error, so interrupt delivery cannot be guaranteed.

### Post-BIST initialization

If BIST is successful, the GIC starts to initialize the interrupt protection logic and the intialization process sets page-2 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").DetectionPaused = 1.

To determine when the intialization process completes, software can poll for either:

page-2 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").DetectionPaused == 0
:   The initialization is successful. Software can now program the interrupt protection page-1 control registers.

[FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").error\_DetectionPaused == 1
:   The initialization failed. The interrupt protection logic is not ready to begin error detection on all INTIDs.

    To discover which INTIDs are faulty, software can:

    1. Read page-1 for all INTIDs, to discover which INTIDs still have [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").DetectionPaused == 1.
    2. Disable the interrupt protection for that INTID, by writing 0 to the page-1 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").Enable bit, which causes page-1 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").DetectionPaused to become 0.
    3. Repeat step [2](https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/Interrupt-protection-initialization?lang=en#rpq1523546077672__li.disable) for any other INTIDs where page-1 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").DetectionPaused == 1.
    4. Verify that page-2 [FMU\_SMRDATA](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary/FMU-SMRDATA--Safety-Mechanism-Read-Data-register?lang=en "This register contains the data that is read during a page read access.").DetectionPaused == 0.
