# Todo 24 validation documentation handoff

Date: 2026-08-22

## Completed documentation

Todo 24 documentation was completed under the fast-pass policy. It documents
the current supported, implemented, deferred, and blocked state without
starting F1-F4 and without claiming final runtime parity.

Exact documentation commits:

- top-level documentation/evidence/submodule pin:
  `069b0640c5172e9621264b84bb2ad70547a3cb9e`
- qbox-platform Apollo README:
  `3b700467c3819d67d7d7a0141b5772d8108eaef2`

Files updated:

- `qa-tests/README.md`
- `doc/qbox-fvp-emulation-project.md`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`
- `.omo/evidence/validation-profiles/task-24/docs-consistency.log`

## Documented contract

- 15 non-Xen Arm Zena CSS v2.2 run-time validation areas.
- 14 public profiles.
- 100 mapped actions.
- BSP/product placement for every profile.
- Named QBox profile runs require `--fvp-reference <summary.json>`.
- `platform-devices` QBox network transport is semantic, not FVP-identical
  host ping/SSH.
- `crypto-extension` QBox coverage is semantic and must not reuse FVP
  crypto-plugin wall-time thresholds.
- MBPP remains isolated 16-CPU only; the normal four-CPU lane is not a PASS
  source.
- Xen/virtualization is explicitly excluded from this profile set.

## Verification

Evidence:

- `.omo/evidence/validation-profiles/task-24/docs-consistency.log`

The checker parsed the live validation matrix and root CLI. It confirmed:

- 14 unique public profiles.
- 15 validation areas.
- 100 actions.
- semantic QBox profiles exactly `crypto-extension` and `platform-devices`.
- Xen selectors in scope: 0.
- `--fvp-reference` parses for a named QBox BSP profile.

`git diff --check` passed for:

- `qa-tests/README.md`
- `doc/qbox-fvp-emulation-project.md`
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md`

## Deferred final artifact dependency

The real final 28-run aggregate is still pending Todo 23. No current final
`coverage.json` exists for 14 FVP plus 14 QBox results, and the documentation
intentionally does not link one as current evidence.

Continue from `.work/validation-plan/final-review-backlog.md` before F1-F4.
Todo 23 must produce the final real aggregate artifacts before Todo 24 can be
upgraded from documentation handoff to final runtime evidence closure.
