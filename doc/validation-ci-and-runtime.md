# Validation, CI, And Runtime Analysis

Generated: 2026-05-15

## Summary

Validation has two major surfaces. Yocto/OEQA runtime tests are configured
through machine and layer metadata. A separate Python pytest-based
`test_automation` package drives FVP and FPGA test flows with YAML platform
configs. GitLab CI composes shared template jobs plus local build/test fragments.

## OEQA Runtime Tests

The Zena validation docs describe runtime integration tests as a mechanism for
validating core Arm Auto Solutions functionality on the image using OEQA
(`arm-zena-css/documentation/design/validation.rst:13`,
`arm-zena-css/documentation/design/validation.rst:17`,
`arm-zena-css/documentation/design/validation.rst:20`).

The machine config sets:

- `TEST_TARGET = "OEFVPTarget"`
- `TEST_TARGET_IP = "127.0.0.1:2222"`
- `TEST_SERVER_IP = "127.0.1.1"`
- a test suite list that includes ping, ssh, boot, RSE, secure partition,
  Safety Island, FVP boot, and FVP devices.

Evidence:
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:102`
through `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:119`.

The docs identify BSP test case sources in
`yocto/meta-zena-css-bsp/lib/oeqa/runtime/cases` and
`meta-arm/lib/oeqa/runtime/cases`
(`arm-zena-css/documentation/design/validation.rst:26`,
`arm-zena-css/documentation/design/validation.rst:31`,
`arm-zena-css/documentation/design/validation.rst:32`,
`arm-zena-css/documentation/design/validation.rst:33`).

## PFDI Validation

PFDI testing validates service status, application execution, and CLI behavior
(`arm-zena-css/documentation/design/validation.rst:179`,
`arm-zena-css/documentation/design/validation.rst:182`,
`arm-zena-css/documentation/design/validation.rst:184`,
`arm-zena-css/documentation/design/validation.rst:185`).

The implementation reference is
`yocto/meta-arm-auto-solutions/lib/oeqa/runtime/cases/test_10_pfdi.py`
(`arm-zena-css/documentation/design/validation.rst:187`,
`arm-zena-css/documentation/design/validation.rst:188`).

The documented tests cover systemd service startup, `pfdi-tool`, the sample app,
CLI information/result queries, forced error injection, and monitoring logs
(`arm-zena-css/documentation/design/validation.rst:192` through
`arm-zena-css/documentation/design/validation.rst:219`).

## Python Test Automation Package

`sw-ref-stack/test_automation/pyproject.toml` defines a Python package named
`Test-Automation` with dependencies on pytest, pytest-subtests,
pytest-timeout, pexpect, PyYAML, and paramiko
(`sw-ref-stack/test_automation/pyproject.toml:13`,
`sw-ref-stack/test_automation/pyproject.toml:14`,
`sw-ref-stack/test_automation/pyproject.toml:17`,
`sw-ref-stack/test_automation/pyproject.toml:18`,
`sw-ref-stack/test_automation/pyproject.toml:19`,
`sw-ref-stack/test_automation/pyproject.toml:20`,
`sw-ref-stack/test_automation/pyproject.toml:21`,
`sw-ref-stack/test_automation/pyproject.toml:22`,
`sw-ref-stack/test_automation/pyproject.toml:23`).

It installs a CLI entry point named `test-automation`
(`sw-ref-stack/test_automation/pyproject.toml:39`,
`sw-ref-stack/test_automation/pyproject.toml:40`). The current CLI is primarily
a version/help entry point (`sw-ref-stack/test_automation/test_automation/cli.py:13`,
`sw-ref-stack/test_automation/test_automation/cli.py:19`,
`sw-ref-stack/test_automation/test_automation/cli.py:25`,
`sw-ref-stack/test_automation/test_automation/cli.py:28`).

## FVP Runtime Config

The baremetal test automation config defines platform `fvp_rd_aspen` as type
`fvp`, parameterized by `${FVP_BINARY}` and `${BUILD_DIR}`
(`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:8`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:9`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:10`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:11`).

It points FVP parameters at local build artifacts such as:

- `rse-rom-image.img`
- `rse-flash-image.img`
- `ap-flash-image.img`
- `baremetal-image-fvp-rd-aspen.wic`
- `efi-capsule-update-disk-image-fvp-rd-aspen.img`

Evidence:
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:14`
through `sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:21`.

It configures user networking with SSH forwarded from host port 2222 to target
port 22 (`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:22`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:23`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:24`).

It maps required terminals and console names for RSE, SCP, Primary Compute, and
secure-world AP console
(`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:61`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:62`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:83`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:84`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:85`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:86`,
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml:87`).

## Pytest Fixtures

The test framework creates per-run log directories under `logs/`
(`sw-ref-stack/test_automation/tests/conftest.py:39`,
`sw-ref-stack/test_automation/tests/conftest.py:40`,
`sw-ref-stack/test_automation/tests/conftest.py:41`,
`sw-ref-stack/test_automation/tests/conftest.py:42`,
`sw-ref-stack/test_automation/tests/conftest.py:43`).

It loads FVP target plugins dynamically when the selected platform type is
`fvp` (`sw-ref-stack/test_automation/tests/conftest.py:52`,
`sw-ref-stack/test_automation/tests/conftest.py:60`,
`sw-ref-stack/test_automation/tests/conftest.py:65`,
`sw-ref-stack/test_automation/tests/conftest.py:68`,
`sw-ref-stack/test_automation/tests/conftest.py:69`).

The session fixture powers on the selected platform, waits for readiness, logs
into the primary console when supported, and powers off during teardown
(`sw-ref-stack/test_automation/tests/conftest.py:316`,
`sw-ref-stack/test_automation/tests/conftest.py:333`,
`sw-ref-stack/test_automation/tests/conftest.py:343`,
`sw-ref-stack/test_automation/tests/conftest.py:344`,
`sw-ref-stack/test_automation/tests/conftest.py:347`,
`sw-ref-stack/test_automation/tests/conftest.py:350`).

CLI pytest options require `--platform` and allow `--config`, `--build-dir`,
`--fvp-binary`, `--debug-logs`, and `--host`
(`sw-ref-stack/test_automation/tests/conftest.py:480` through
`sw-ref-stack/test_automation/tests/conftest.py:526`).

## GitLab CI

Both `sw-ref-stack` and `arm-zena-css` define stages:

- Setup
- Quality
- Build
- Test
- Release
- Cleanup

Evidence: `sw-ref-stack/.gitlab-ci.yml:52` through
`sw-ref-stack/.gitlab-ci.yml:58`; `arm-zena-css/.gitlab-ci.yml:55` through
`arm-zena-css/.gitlab-ci.yml:61`.

The CI pipelines include shared automation templates for baseline checks, docs
build, kas build/test templates, test automation, stable uploads, artifact
injection, and header checks
(`sw-ref-stack/.gitlab-ci.yml:60` through `sw-ref-stack/.gitlab-ci.yml:77`;
`arm-zena-css/.gitlab-ci.yml:63` through `arm-zena-css/.gitlab-ci.yml:80`).

Local CI fragments are also included. `sw-ref-stack` includes local rules,
build, test, Yocto QA, and test automation fragments
(`sw-ref-stack/.gitlab-ci.yml:98` through `sw-ref-stack/.gitlab-ci.yml:102`).
`arm-zena-css` includes local rules, build/test fragments, a `sw-ref-stack`
fragment, and Yocto QA
(`arm-zena-css/.gitlab-ci.yml:81` through `arm-zena-css/.gitlab-ci.yml:86`).

## Useful Local Test Commands

Python package smoke checks:

```bash
python -m compileall sw-ref-stack/test_automation
pytest sw-ref-stack/test_automation/unittests
```

FVP runtime tests require local build artifacts and an FVP binary:

```bash
pytest sw-ref-stack/test_automation/tests \
  --platform fvp_rd_aspen \
  --config sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml \
  --build-dir build/tmp_baremetal/deploy/images/fvp-rd-aspen \
  --fvp-binary /path/to/FVP_Zena_CSS_Cfg2
```

Do not report runtime validation as passing unless the FVP binary, required
plugins, deploy images, and console readiness were verified in the same run.
