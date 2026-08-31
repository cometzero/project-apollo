# Offline Task7 FVP ECAM-limit fixture

This is an immutable test-fixture excerpt bundle for the Task7 boundary gate.
It records the observed first ECAM read failure at `0x10040000000` on domain
`0004:00`, including the EL3 SError tuple and cleanup result.

It deliberately contains neither an FVP binary nor a runnable platform
profile. `source-identity.json` records the original profile, fvpconf, and
binary SHA-256 identities as metadata only. `manifest.json` hashes every
content file in this directory except itself, by the explicit non-circular
rule recorded in `NOTICE`.

`NOTICE` is the repository-authoritative provenance statement for this test
data. No repository-wide license file was present when this fixture was added,
so no SPDX identifier or redistribution grant is asserted. The fixture is
limited to project-authored JSON and minimal factual log excerpts; consult the
repository owner before redistributing it outside this repository.

Regenerate the reference gate with:

```bash
python3 scripts/test/validate_apollo_fvp_pcie_limit.py --output /tmp/reference-gate.json
python3 scripts/test/publish_apollo_fvp_pcie_limit.py --output /tmp/producer-gate.json
```

A passing gate means only that this recorded boundary is internally
consistent: FVP qualification remains `UNSUPPORTED`, no endpoint was
enumerated, and no ITS delivery or FVP/QBox parity is claimed.
