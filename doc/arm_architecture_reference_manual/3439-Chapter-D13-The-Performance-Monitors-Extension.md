# ​Chapter D13 The Performance Monitors Extension

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension>

### Chapter D13 The Performance Monitors Extension

This chapter describes the implementation of the Arm Performance Monitors, which are an optional non-invasive debug component. It describes version 3 of the *Performance Monitor Unit* (PMU) architecture, [FEAT\_PMUv3](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-1-The-Armv8-0-architecture-extension?lang=en#feat_feat_pmuv3). It contains the following sections:

- [About the Performance Monitors](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-1-About-the-Performance-Monitors?lang=en#b1chdeejjh)
- [Accuracy of the Performance Monitors](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-2-Accuracy-of-the-Performance-Monitors?lang=en#cihdgedi)
- [Behavior on overflow](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-3-Behavior-on-overflow?lang=en#cihhhafh)
- [Attributability](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-4-Attributability?lang=en#cacbieia)
- [Controlling the PMU counters](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-5-Controlling-the-PMU-counters?lang=en#cihidfee)
- [Multithreaded implementations](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-6-Multithreaded-implementations?lang=en#caciaggh)
- [Event filtering](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-7-Event-filtering?lang=en#cihccbgi)
- [Event threshold and edge counting](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-8-Event-threshold-and-edge-counting?lang=en#cacbgfjeg4)
- [PMU snapshots](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-9-PMU-snapshots?lang=en#babfdihdf2)
- [Performance Monitors and Debug state](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-10-Performance-Monitors-and-Debug-state?lang=en#cacdadad)
- [Counter access](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-11-Counter-access?lang=en#cihhbffb)
- [Performance Monitors Extension registers](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D13-The-Performance-Monitors-Extension/-D13-12-Performance-Monitors-Extension-registers?lang=en#ciaijcdd)

> #### Note
>
> [Table K14-2](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-1-Register-name-disambiguation-by-Execution-state?lang=en#tbl_cihddgii) disambiguates the general register references used in this chapter.
