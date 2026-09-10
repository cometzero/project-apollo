# About the programmers model

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/About-the-programmers-model>

### About the programmers model

This section describes the functions and programmers model of the CoreLink DMA-350.

When using the programmers model, adhere to the following guidelines:

- Do not attempt to access reserved or unused address locations. Attempting to access these locations can result in unpredictable behavior.
- Unless otherwise stated in the accompanying text:

  - Do not modify undefined register bits.
  - Ignore undefined register bits on reads.
  - Unless otherwise specified, all register bits are reset to a logic 0 by a system or power up reset.

The following describes the access type:

RW
:   Read and write

RO
:   Read-only

WO
:   Write-only

RAZ
:   Read-As-Zero

WI
:   Writes ignored

W1C
:   Write 1 to Clear
