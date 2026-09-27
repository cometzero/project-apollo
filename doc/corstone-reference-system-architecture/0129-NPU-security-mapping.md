# NPU security mapping

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/NPU/NPU-security-mapping>

### NPU security mapping

The NPU is capable of operating in different security modes. To change from operating in one security world to another, a reset is required.

When the NPU reset is released by the PPU controlling the NPU power domain PD\_NPU<m>, it samples the signals driven by:

- NPUSPPORSL.SP\_NPU<m>PORSL to determine its default security level.
- NPUSPPORPL.SP\_NPU<m>PORPL or NPUNSPORPL.NS\_NPU<m>PORPL to determine the NPU’s default privilege level.

See [NPUSPPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/NPUSPPORPL?lang=en "The NPU Secure Access Privileged Level Reset Control Register allows software to configure if each NPU resets to privileged or unprivileged state. The value of this register is only sampled by the NPU, when the NPU is released from reset and NPUSPPORSL.SP_NPU<m>PORSL is Secure State. The default reset value of this register is controlled by NPU<m>PORPLRST:") and [NPUNSPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/NPUNSPORPL?lang=en "The NPU power on reset Non-secure access privileged level reset control registers allow software to configure if each NPU resets to privileged or unprivileged state."). These registers are also used to control the PPC, which provides access protection to the NPU’s configuration interface.

> ### Note
>
> The PPC protection setting takes effect as soon as the security and privileged registers are updated.

The following sequences are recommended when transitioning the NPU to a new security or privilege level.

### Changing security level from Secure (S) to Non-secure (NS)

The following sequence details the steps for the Secure privilege software (SW) to change security level:

1. Read the current security from the corresponding System register: initial\_security= NPUSPPORSL.SP\_NPU<m>PORSL
2. If initial\_security=S then SW reads the privilege to be retained in the target Security state from the corresponding System register: initial\_privilege=NPUNSPORPL.NS\_NPU<m>PORPL else skip remaining sequence.
3. Write on the current security alias of the NPU (S) the configuration interface, targeting the CMD.power\_q\_enable register field of the NPU to prevent the NPU powering OFF (0 = Power OFF denied) while preserving the rest of the CMD register
4. Write on the current security alias of the NPU (S) the configuration interface, targeting the RESET.pending\_CSL register field of the NPU to set the new security level (1= Non-secure) while preserving RESET.pending\_CPL=initial\_privilege
5. Read repeatedly (poll) on the current security alias of the NPU (S) the configuration interface, targeting the STATUS register of the NPU until the field reset\_status no longer returns the value 1
6. Write the new security level into NPUSPPORSL.SP\_NPU<m>PORSL register field (1 = Non-secure)
7. Write on the current security alias of the NPU (NS) the configuration interface, targeting the CMD.power\_q\_enable register field of the NPU to the allow the NPU to speculatively power OFF (1 = Power OFF allowed) while preserving the rest of the CMD register

### Changing security level from Non-secure (NS) to Secure (S)

The following sequence details the steps for the Non-secure privilege software to change security level to Secure:

1. Read the current security from the corresponding System register: initial\_security=NPUSPPORSL.SP\_NPU<m>PORSL
2. If initial\_security=NS then SW reads the privilege to be retained in the target Security state from the corresponding System register: initial\_privilege=NPUSPPORPL.SP\_NPU<m>PORPL else skip remaining sequence.
3. Write on the current security alias of the NPU (NS) the configuration interface, targeting the CMD.power\_q\_enable register field of the NPU to the prevent the NPU powering OFF (0 = Power OFF denied) while preserving the rest of the CMD register
4. Write the new security level into NPUSPPORSL.SP\_NPU<m>PORSL register field (0 = Secure)
5. Write on the current security alias of the NPU (S) the configuration interface, targeting the RESET.pending\_CSL register field of the NPU to set the new security level (0=Secure) while preserving RESET.pending\_CPL=initial\_privilege
6. Read repeatedly (poll) on the current security alias of the NPU (S) the configuration interface, targeting the STATUS register of the NPU until the field reset\_status no longer returns the value 1
7. Write on the current security alias of the NPU (S) the configuration interface, targeting the CMD.power\_q\_enable register field of the NPU to the allow the NPU to speculatively power OFF (1 = Power OFF allowed) while preserving the rest of the CMD register

### Changing privilege level

Secure or Non-secure privilege software can change the privilege state of the NPU, as long as the privilege state being moved to is equal or lower than the software enacting the change and the security level of the software is at least matching the current security level (initial\_security) of the NPU.

The following sequence details the steps for the privilege software to change privilege level:

1. Read the current privilege level from the corresponding System register:

   Current security level = Non-secure

   initial\_privilege=NPUNSPORPL.NS\_NPU<m>PORPL

   Current security level = Secure

   initial\_privilege=NPUSPPORPL.SP\_NPU<m>PORPL
2. If initial\_privilege is the desired one, then skip remaining sequence.
3. Write on the current security alias of the NPU (initial\_security) the configuration interface, targeting the CMD.power\_q\_enable register field of the NPU to the prevent the NPU powering OFF (0 = Power OFF denied) while preserving the rest of the CMD register
4. Write to the current security alias of the NPU (initial\_security) the configuration interface, targeting the RESET.pending\_CPL register field of the NPU to set the new privilege level (0=User; 1=privileged) while preserving RESET.pending\_CSL=initial\_security
5. Read repeatedly (poll) from the current security alias of the NPU (initial\_security) the configuration interface, targeting the STATUS register of the NPU until the ﬁeld reset\_status no longer returns the value 1
6. Write to the alias corresponding to the current security level of the NPU (initial\_security) the new privilege level into

   Current security level = Non-secure

   NPUNSPORPL.NS\_NPU<m>PORPL

   Current security level = Secure

   NPUSPPORPL.SP\_NPU<m>PORPL
7. Write on the current security alias of the NPU (initial\_security) the configuration interface, targeting the CMD.power\_q\_enable register field of the NPU to the allow the NPU to speculatively power OFF (1 = Power OFF allowed) while preserving the rest of the CMD register
