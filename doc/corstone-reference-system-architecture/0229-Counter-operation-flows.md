# Counter operation flows

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/Counter-operation-flows>

### Counter operation flows

This section describes pseudo‑sequences for some of the commonly used Counter programming flows.

### Counter initialization

To initialize the counter, perform the following steps:

1. Ensure that CLKSEL is 0x01 and that REFCLK is running.
2. Disable the counter by setting CNTCR.EN = 0.
3. Configure the SoC clock generation to generate the frequencies that are required for the two clock sources.
4. Write to CNTSCR0 to set the scaling value for REFCLK clock source.
5. Write to CNTSCR1 to set the scaling value for FASTCLK clock source.
6. Enable the counter by setting CNTCR.EN = 1.
7. CLKSEL can now be changed at any time to switch the FCLK source between REFCLK and FASTCLK.

### Changing scaling registers

To change the scaling registers, perform the following steps:

1. Ensure that REFCLK is running.
2. Disable the counter by setting CNTCR.EN = 0.
3. Write new values to CNTSCR0 and CNTSCR1.
4. Enable the counter by setting CNTCR.EN = 1.
