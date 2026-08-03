#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import NoReturn

import jsonschema


class BuildError(RuntimeError):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason


def fail(reason: str, detail: str = "") -> NoReturn:
    raise BuildError(reason, detail)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def logical_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def validate_isolated_paths(args: argparse.Namespace, workspace: Path) -> None:
    output = args.output_root.resolve()
    active_tmp = (workspace / "build/tmp_baremetal").resolve()
    active_deploy = (active_tmp / "deploy").resolve()
    resolved_paths: list[Path] = []
    for name in ("tmpdir", "deploy_dir", "deploy_dir_image", "sstate_dir"):
        logical = logical_path(getattr(args, name))
        if not is_relative_to(logical, output):
            fail("active_default_path_forbidden", name)
        path = logical.resolve()
        if (
            is_relative_to(path, active_tmp)
            or is_relative_to(active_tmp, path)
            or is_relative_to(path, active_deploy)
        ):
            fail("active_default_path_forbidden", name)
        resolved_paths.append(path)
    backing_roots = {
        Path("/srv/arm") / path.relative_to("/srv/arm").parts[0]
        for path in resolved_paths
        if is_relative_to(path, Path("/srv/arm"))
    }
    if backing_roots:
        if len(backing_roots) != 1:
            fail("invalid_generated_backing", "multiple roots")
        backing = next(iter(backing_roots))
        if not backing.name.startswith("gic720ae-task27-"):
            fail("invalid_generated_backing", str(backing))
        if any(
            not is_relative_to(path, backing)
            for path in resolved_paths
            if not is_relative_to(path, output)
        ):
            fail("invalid_generated_backing", "path outside backing")
    if not is_relative_to(
        logical_path(args.deploy_dir_image),
        logical_path(args.deploy_dir),
    ):
        fail("invalid_isolated_path", "deploy-dir-image")


def verify_provider_path(value: str, workspace: Path) -> Path:
    expected = (
        workspace
        / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-test/"
        "gic720ae-selftest/gic720ae-selftest.bb"
    ).resolve()
    provider = Path(value).resolve()
    if provider != expected:
        fail("unexpected_recipe_provider", str(provider))
    return provider


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def oe_environment(workspace: Path) -> dict[str, str]:
    setup = (
        "source layers/poky/oe-init-build-env build >/dev/null && "
        "env -0"
    )
    result = subprocess.run(
        ["bash", "-c", setup],
        cwd=workspace,
        check=False,
        capture_output=True,
        timeout=60,
    )
    if result.returncode != 0:
        fail("bitbake_environment_failed")
    environment = {
        key.decode(): value.decode()
        for item in result.stdout.split(b"\0")
        if item
        for key, value in [item.split(b"=", 1)]
    }
    environment["MACHINE"] = "apollo-qvp"
    return environment


def run(
    argv: list[str], workspace: Path, environment: dict[str, str],
    log: Path, timeout: int,
) -> str:
    result = subprocess.run(
        argv,
        cwd=workspace,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        fail("build_command_failed", " ".join(argv))
    return result.stdout


def bitbake_value(
    recipe: str, variable: str, include: Path, workspace: Path,
    environment: dict[str, str], log_dir: Path,
) -> str:
    output = run(
        ["bitbake", "-R", str(include), "-e", recipe],
        workspace, environment, log_dir / f"{recipe}-environment.log", 180,
    )
    prefix = f'{variable}="'
    values = [
        line[len(prefix):-1]
        for line in output.splitlines()
        if line.startswith(prefix) and line.endswith('"')
    ]
    if not values:
        fail("bitbake_variable_missing", f"{recipe}:{variable}")
    return values[-1]


def write_override(
    args: argparse.Namespace, path: Path, workspace: Path,
) -> None:
    values = {
        "TMPDIR": logical_path(args.tmpdir),
        "DEPLOY_DIR": logical_path(args.deploy_dir),
        "DEPLOY_DIR_IMAGE": logical_path(args.deploy_dir_image),
        "SSTATE_DIR": logical_path(args.sstate_dir),
    }
    lines = [f'{name} = "{value}"' for name, value in values.items()]
    default_sstate = (workspace / "build/sstate-cache").resolve()
    lines.append(
        'SSTATE_MIRRORS = "file://.* '
        f'file://{default_sstate}/PATH;downloadfilename=PATH"'
    )
    resolved_tmp = args.tmpdir.resolve()
    ignored = (
        "sstate-control", "buildstats", "sysroots-components", "pkgdata",
    )
    lines.append(
        'PSEUDO_IGNORE_PATHS .= ",'
        + ",".join(str(resolved_tmp / relative) for relative in ignored)
        + '"'
    )
    lines.append('INSANE_SKIP:openvswitch-src += "buildpaths"')
    lines.append(f'IMAGE_INSTALL:append = " {args.package}"')
    lines.append(
        f'KERNEL_DEVICETREE:pn-{args.image} = "apollo-qvp.dtb"'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def one(paths: list[Path], role: str) -> Path:
    existing = [path for path in paths if path.exists()]
    if len(existing) != 1:
        fail("isolated_output_missing", role)
    return existing[0]


def copy_artifact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source.resolve(), destination)


def clear_generated_deploy(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child)


def artifact(role: str, path: Path) -> dict[str, str]:
    return {"role": role, "path": str(path.resolve()), "sha256": sha256(path)}


def storage_mapping(path: Path) -> dict[str, object]:
    logical = logical_path(path)
    resolved = logical.resolve()
    usage = shutil.disk_usage(resolved)
    return {
        "logical_path": str(logical),
        "resolved_realpath": str(resolved),
        "symlinked": logical.is_symlink(),
        "device": os.stat(resolved).st_dev,
        "total_bytes": usage.total,
        "free_bytes": usage.free,
    }


def verify_uki_dtb(
    wic: Path, expected_dtb: Path, output_root: Path, workspace: Path,
    environment: dict[str, str], logs: Path,
) -> list[Path]:
    verification = output_root / "verification"
    verification.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    for slot in ("a", "b"):
        uki = verification / f"{slot}.efi"
        dtb = verification / f"{slot}.dtb"
        run(
            [
                "mcopy", "-o", "-i", f"{wic}@@1048576",
                f"::/EFI/Linux/{slot}-slot/auto-ad-nexios-{slot}.efi",
                str(uki),
            ],
            workspace, environment, logs / f"extract-uki-{slot}.log", 120,
        )
        run(
            ["llvm-objcopy", "--dump-section", f".dtb={dtb}", str(uki)],
            workspace, environment, logs / f"extract-dtb-{slot}.log", 120,
        )
        if sha256(dtb) != sha256(expected_dtb):
            fail("uki_dtb_mismatch", slot)
        extracted.append(dtb)
    return extracted


def task_provenance(
    tmpdir: Path, sstate_dir: Path, recipe: str, task: str,
) -> dict[str, str]:
    sigdata = list(
        tmpdir.glob(f"stamps/*/{recipe}/*.{task}.sigdata.*")
    )
    if not sigdata:
        fail("task_provenance_missing", f"{recipe}:{task}")
    path = max(sigdata, key=lambda item: item.stat().st_mtime_ns)
    taskhash = path.name.rsplit(".", 1)[-1]
    sstate = list(sstate_dir.glob(f"**/*{taskhash}*"))
    sstate_file = next((item for item in sstate if item.is_file()), None)
    return {
        "recipe": recipe,
        "task": task,
        "taskhash": taskhash,
        "sigdata": f"{path.resolve()}:{sha256(path)}",
        "sstate": (
            f"{sstate_file.resolve()}:{sha256(sstate_file)}"
            if sstate_file is not None
            else "task-executed-no-sstate-file"
        ),
    }


def compare_default(
    workspace: Path, root: Path, baseline: Path, output: Path,
) -> None:
    result = subprocess.run(
        [
            "python3",
            "scripts/test/capture_gic720ae_default_deploy_manifest.py",
            "--root", str(root),
            "--mode", "complete-instance",
            "--compare", str(baseline),
            "--schema",
            "tests/schemas/gic720ae-default-deploy-manifest.schema.json",
            "--output", str(output),
        ],
        cwd=workspace,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        fail("default_deploy_contaminated")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-clean-build", action="store_true")
    parser.add_argument("--machine", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--tmpdir", type=Path, required=True)
    parser.add_argument("--deploy-dir", type=Path, required=True)
    parser.add_argument("--deploy-dir-image", type=Path, required=True)
    parser.add_argument("--sstate-dir", type=Path, required=True)
    parser.add_argument("--default-yocto-provenance", type=Path, required=True)
    parser.add_argument("--default-deploy-manifest", type=Path, required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--profile-output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=14400)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(__file__).resolve().parents[2]
    logs = args.output_root / "logs"
    try:
        if (
            args.machine != "apollo-qvp"
            or args.image != "nexios-bsp-initramfs"
            or args.package != "gic720ae-selftest"
        ):
            fail("unsupported_profile")
        validate_isolated_paths(args, workspace)
        if args.force_clean_build:
            clear_generated_deploy(args.deploy_dir)
        default_provenance = json.loads(
            args.default_yocto_provenance.read_text(encoding="utf-8")
        )
        if default_provenance.get("verdict") != "PASS":
            fail("default_provenance_failed")
        before = json.loads(args.default_deploy_manifest.read_text(encoding="utf-8"))
        if before.get("verdict") != "PASS" or before.get("mode") != "complete-instance":
            fail("default_deploy_manifest_invalid")
        if not args.overlay.is_file():
            fail("overlay_missing")
        args.output_root.mkdir(parents=True, exist_ok=True)
        for path in (
            args.tmpdir, args.deploy_dir_image, args.sstate_dir,
            args.output_root / "deploy",
        ):
            path.mkdir(parents=True, exist_ok=True)
        include = args.output_root / "conf/gic720ae-linux-probe.inc"
        write_override(args, include, workspace)
        environment = oe_environment(workspace)
        show = run(
            ["bitbake-layers", "show-recipes", args.package],
            workspace, environment, logs / "show-recipes.log", 180,
        )
        if args.package not in show or "meta-hsoc-bsp" not in show:
            fail("unexpected_recipe_provider", "show-recipes")
        provider = verify_provider_path(
            bitbake_value(
                args.package, "FILE", include, workspace, environment, logs,
            ),
            workspace,
        )
        bitbake = ["bitbake", "-R", str(include)]
        if args.force_clean_build:
            run(
                bitbake + [
                    "-c", "cleansstate", "linux-yocto-rt",
                    args.package, args.image,
                ],
                workspace, environment, logs / "cleansstate.log", args.timeout,
            )
        run(
            bitbake + ["linux-yocto-rt", "-c", "deploy"],
            workspace, environment, logs / "kernel-deploy.log", args.timeout,
        )
        base_dtb = args.deploy_dir_image / "apollo-qvp.dtb"
        base_copy = args.output_root / "base-apollo-qvp.dtb"
        copy_artifact(base_dtb, base_copy)
        interrupt_parent = run(
            ["fdtget", "-t", "x", str(base_copy), "/", "interrupt-parent"],
            workspace, environment, logs / "base-interrupt-parent.log", 60,
        ).strip()
        if interrupt_parent != "1":
            fail("unexpected_base_gic_phandle", interrupt_parent)
        overlay_blob = args.output_root / "apollo-qvp-gic720ae.dtbo"
        run(
            [
                "dtc", "-@", "-I", "dts", "-O", "dtb",
                "-o", str(overlay_blob), str(args.overlay.resolve()),
            ],
            workspace, environment, logs / "dtc.log", 60,
        )
        run(
            [
                "fdtoverlay", "-i", str(base_copy), "-o", str(base_dtb),
                str(overlay_blob),
            ],
            workspace, environment, logs / "fdtoverlay.log", 60,
        )
        run(
            bitbake + [args.image],
            workspace, environment, logs / "image-build.log", args.timeout,
        )
        compatible = run(
            [
                "fdtget", "-t", "s", str(base_dtb),
                "/gic720ae-linux-selftest", "compatible",
            ],
            workspace, environment, logs / "merged-compatible.log", 60,
        ).strip()
        interrupts = run(
            [
                "fdtget", "-t", "x", str(base_dtb),
                "/gic720ae-linux-selftest", "interrupts",
            ],
            workspace, environment, logs / "merged-interrupts.log", 60,
        ).strip()
        if compatible != "arm,gic720ae-linux-selftest":
            fail("merged_overlay_missing", "compatible")
        if interrupts != "0 36 1":
            fail("merged_overlay_missing", "interrupts")

        deploy = args.output_root / "deploy"
        output_kernel = deploy / "Image"
        output_dtb = deploy / "apollo-qvp-gic720ae-probe.dtb"
        output_wic = deploy / "nexios-bsp-initramfs-apollo-qvp-gic720ae-probe.wic"
        output_packages = deploy / "rootfs-packages.txt"
        copy_artifact(args.deploy_dir_image / "Image", output_kernel)
        copy_artifact(base_dtb, output_dtb)
        source_wic = (
            args.deploy_dir_image / "nexios-bsp-initramfs-apollo-qvp.wic"
        )
        embedded_dtbs = verify_uki_dtb(
            source_wic, base_dtb, args.output_root,
            workspace, environment, logs,
        )
        copy_artifact(source_wic, output_wic)
        copy_artifact(
            args.deploy_dir_image / "nexios-bsp-initramfs-apollo-qvp.manifest",
            output_packages,
        )
        module_source = one(
            list(args.tmpdir.glob(
                "work/*/nexios-bsp-initramfs/*/rootfs/lib/modules/"
                "*/extra/gic720ae_test.ko"
            )),
            "module",
        )
        kernel_release = module_source.parents[2].name
        output_module = (
            deploy / "lib/modules" / kernel_release / "extra/gic720ae_test.ko"
        )
        copy_artifact(module_source, output_module)

        source_qboxconf = args.deploy_dir_image / (
            "nexios-bsp-initramfs-apollo-qvp.qboxconf"
        )
        qboxconf = json.loads(source_qboxconf.read_text(encoding="utf-8"))
        qboxconf["images"]["kernel"] = output_kernel.name
        qboxconf["images"]["dtb"] = output_dtb.name
        qboxconf["images"]["rootfs_wic"] = output_wic.name
        for role, filename in qboxconf["images"].items():
            if role not in {"kernel", "dtb", "rootfs_wic"}:
                copy_artifact(args.deploy_dir_image / filename, deploy / filename)
        output_qboxconf = deploy / (
            "nexios-bsp-initramfs-apollo-qvp-gic720ae-probe.qboxconf"
        )
        output_qboxconf.write_text(
            json.dumps(qboxconf, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if args.package not in output_packages.read_text(encoding="utf-8"):
            fail("isolated_package_missing")
        compare_default(
            workspace,
            workspace / "build/tmp_baremetal/deploy/images/apollo-qvp",
            args.default_deploy_manifest,
            args.output_root / "default-deploy-after.json",
        )
        source_paths = [
            workspace / "hsoc-stack/components/primary_compute/linux/tools/"
            "testing/selftests/irq/gic720ae/gic720ae_test.c",
            args.overlay,
            provider,
        ]
        payload = {
            "format_version": 1,
            "verdict": "PASS",
            "reason": "linux_probe_profile_built",
            "machine": args.machine,
            "package": args.package,
            "provider": str(provider),
            "artifacts": [
                artifact("kernel", output_kernel),
                artifact("merged_dtb", output_dtb),
                artifact("wic", output_wic),
                artifact("qboxconf", output_qboxconf),
                artifact("rootfs_packages", output_packages),
                artifact("gic720ae_test", output_module),
                artifact("uki_a_dtb", embedded_dtbs[0]),
                artifact("uki_b_dtb", embedded_dtbs[1]),
            ],
            "sources": {
                str(path.resolve()): sha256(path)
                for path in source_paths
            },
            "configuration": {
                "override": str(include.resolve()),
                "override_sha256": sha256(include),
                "tmpdir": str(logical_path(args.tmpdir)),
                "deploy_dir": str(logical_path(args.deploy_dir)),
                "deploy_dir_image": str(logical_path(args.deploy_dir_image)),
                "sstate_dir": str(logical_path(args.sstate_dir)),
                "generated_storage": {
                    "tmpdir": storage_mapping(args.tmpdir),
                    "deploy_dir": storage_mapping(args.deploy_dir),
                    "sstate_dir": storage_mapping(args.sstate_dir),
                    "content_policy": "generated-bitbake-artifacts-only",
                    "retention": "retained-until-explicit-cleanup",
                },
                "isolated_qa_exception": {
                    "package": "openvswitch-src",
                    "check": "buildpaths",
                    "scope": "generated-source-debug-line-directive",
                },
                "default_deploy_manifest": str(
                    args.default_deploy_manifest.resolve()
                ),
                "default_deploy_manifest_sha256": sha256(
                    args.default_deploy_manifest
                ),
                "default_image_exclusion": before["package_exclusion"],
            },
            "task_provenance": [
                task_provenance(
                    args.tmpdir, args.sstate_dir,
                    "linux-yocto-rt", "do_compile",
                ),
                task_provenance(
                    args.tmpdir, args.sstate_dir, args.image, "do_rootfs",
                ),
            ],
        }
        schema = workspace / "tests/schemas/gic720ae-linux-probe-profile.schema.json"
        jsonschema.validate(payload, json.loads(schema.read_text()))
        args.profile_output.parent.mkdir(parents=True, exist_ok=True)
        args.profile_output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return 0
    except (BuildError, OSError, ValueError, json.JSONDecodeError) as error:
        reason = error.reason if isinstance(error, BuildError) else "profile_build_failed"
        failure = {
            "format_version": 1,
            "verdict": "FAIL",
            "reason": reason,
            "machine": "apollo-qvp",
            "package": "gic720ae-selftest",
            "provider": "",
            "artifacts": [],
            "sources": {},
            "configuration": {},
            "task_provenance": [],
        }
        args.profile_output.parent.mkdir(parents=True, exist_ok=True)
        args.profile_output.write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
