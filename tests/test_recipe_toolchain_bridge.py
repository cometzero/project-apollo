from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def write_executable(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    path.chmod(0o755)


def run_bash(command: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("bash", "-c", command),
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def output_of(result: subprocess.CompletedProcess[str]) -> str:
    return f"{result.stdout}\n{result.stderr}"


def make_recipe_toolchain_fixture(tmp_path: Path) -> dict[str, str]:
    tools_dir = tmp_path / "tools"
    workdir = tmp_path / "tmp_baremetal/work/kernel"
    native_sysroot = workdir / "recipe-sysroot-native"
    target_sysroot = workdir / "recipe-sysroot"
    compiler = (
        native_sysroot
        / "usr/bin/aarch64-poky-linux/aarch64-poky-linux-gcc"
    )
    write_executable(
        compiler,
        "#!/usr/bin/env bash\n"
        '[[ "${1:-}" == -print-sysroot ]] && printf "/not/exist\\n"\n',
    )
    (target_sysroot / "usr/include/linux").mkdir(parents=True)
    (native_sysroot / "usr/lib/ossl-modules").mkdir(parents=True)
    (target_sysroot / "usr/include/linux/version.h").write_text(
        "#define LINUX_VERSION_CODE 1\n",
        encoding="utf-8",
    )

    bitbake_log = tmp_path / "bitbake.log"
    query_log = tmp_path / "recipe-query.log"
    write_executable(
        tools_dir / "bitbake",
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "${APOLLO_TEST_BITBAKE_LOG}"\n',
    )
    write_executable(
        tools_dir / "recipe-toolchain-query",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'printf "%s\\n" "$*" >> "${APOLLO_TEST_QUERY_LOG}"\n'
        'for recipe in "$@"; do\n'
        '    printf "%s\\t%s\\taarch64-poky-linux-\\n" \\\n'
        '        "${recipe}" "${APOLLO_TEST_WORKDIR}"\n'
        "done\n",
    )

    return {
        "APOLLO_AUTO_RESOURCE_LIMITS": "0",
        "APOLLO_LOCAL_BUILD_USE_YOCTO_VARS": "0",
        "APOLLO_TEST_BITBAKE_LOG": str(bitbake_log),
        "APOLLO_TEST_QUERY_LOG": str(query_log),
        "APOLLO_TEST_WORKDIR": str(workdir),
        "BITBAKE": str(tools_dir / "bitbake"),
        "HOME": str(tmp_path),
        "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
        "MACHINE": "apollo-qvp",
        "PATH": f"{tools_dir}:/usr/bin:/bin",
        "RECIPE_TOOLCHAIN_QUERY": str(tools_dir / "recipe-toolchain-query"),
        "YOCTO_BUILD_DIR": str(tmp_path / "yocto-build"),
    }


def test_parent_prepares_unique_recipe_sysroot_then_children_only_activate(
    tmp_path: Path,
) -> None:
    env = os.environ.copy() | make_recipe_toolchain_fixture(tmp_path)
    command = "\n".join(
        (
            "set -euo pipefail",
            "source scripts/build/local_build_common.sh",
            "source scripts/build/modules/build_recipe_toolchain.sh",
            "recipe_toolchain_init_bitbake_env() { BITBAKE_EXTRA_ARGS=(); }",
            "prepare_bitbake_extra_args() { BITBAKE_EXTRA_ARGS=(); }",
            "prepare_selected_component_toolchains linux buildroot u-boot",
            "activate_component_recipe_toolchain linux",
            'printf "recipe=%s\\n" "${RECIPE_TOOLCHAIN_RECIPE}"',
            'printf "native=%s\\n" "${SDK_NATIVE_SYSROOT}"',
            'printf "target=%s\\n" "${SDK_TARGET_SYSROOT}"',
            'printf "prefix=%s\\n" "${AARCH64_PREFIX}"',
            'printf "openssl=%s\\n" "${OPENSSL_MODULES}"',
            '"${SDK_NATIVE_SYSROOT}/usr/bin/${AARCH64_PREFIX%-}/'
            '${AARCH64_PREFIX}gcc" -print-sysroot',
        )
    )

    result = run_bash(command, env)

    assert result.returncode == 0, output_of(result)
    workdir = Path(env["APOLLO_TEST_WORKDIR"])
    output = result.stdout
    assert "recipe=virtual/kernel" in output
    assert f"native={workdir / 'recipe-sysroot-native'}" in output
    assert f"target={workdir / 'recipe-sysroot'}" in output
    assert "prefix=aarch64-poky-linux-" in output
    assert f"openssl={workdir / 'recipe-sysroot-native/usr/lib/ossl-modules'}" in output
    assert output.rstrip().endswith("/not/exist")

    bitbake_calls = Path(env["APOLLO_TEST_BITBAKE_LOG"]).read_text(
        encoding="utf-8"
    ).splitlines()
    assert len(bitbake_calls) == 1
    assert "virtual/kernel" in bitbake_calls[0]
    assert "u-boot" in bitbake_calls[0]
    assert "-c prepare_recipe_sysroot" in bitbake_calls[0]
    assert "populate_sdk" not in bitbake_calls[0]

    query_calls = Path(env["APOLLO_TEST_QUERY_LOG"]).read_text(
        encoding="utf-8"
    ).splitlines()
    assert query_calls == ["virtual/kernel u-boot"]


def test_freestanding_component_activation_does_not_require_linux_gcc(
    tmp_path: Path,
) -> None:
    env = os.environ.copy() | make_recipe_toolchain_fixture(tmp_path)
    workdir = Path(env["APOLLO_TEST_WORKDIR"])
    compiler = (
        workdir
        / "recipe-sysroot-native/usr/bin/aarch64-poky-linux"
        / "aarch64-poky-linux-gcc"
    )
    compiler.unlink()
    command = "\n".join(
        (
            "set -euo pipefail",
            "source scripts/build/local_build_common.sh",
            "source scripts/build/modules/build_recipe_toolchain.sh",
            "recipe_toolchain_init_bitbake_env() { BITBAKE_EXTRA_ARGS=(); }",
            "prepare_selected_component_toolchains tf-m",
            "activate_component_recipe_toolchain tf-m",
        )
    )

    result = run_bash(command, env)

    assert result.returncode == 0, output_of(result)


def test_components_without_cross_compile_do_not_prepare_recipe_sysroots(
    tmp_path: Path,
) -> None:
    env = os.environ.copy() | make_recipe_toolchain_fixture(tmp_path)
    command = "\n".join(
        (
            "set -euo pipefail",
            "source scripts/build/local_build_common.sh",
            "source scripts/build/modules/build_recipe_toolchain.sh",
            "prepare_selected_component_toolchains "
            "qbox zephyr flash-images boot-disk fvpconf debug-manifest",
            "activate_component_recipe_toolchain qbox",
            "activate_component_recipe_toolchain zephyr",
            "activate_component_recipe_toolchain flash-images",
            "activate_component_recipe_toolchain boot-disk",
        )
    )

    result = run_bash(command, env)

    assert result.returncode == 0, output_of(result)
    assert not Path(env["APOLLO_TEST_BITBAKE_LOG"]).exists()
    assert not Path(env["APOLLO_TEST_QUERY_LOG"]).exists()


def test_kbuild_compiler_uses_active_recipe_sysroot(tmp_path: Path) -> None:
    env = os.environ.copy() | {
        "APOLLO_LOCAL_BUILD_CCACHE": "0",
        "LOCAL_BUILD_DIR": str(tmp_path / "local-build"),
    }
    command = "\n".join(
        (
            "set -euo pipefail",
            "source scripts/build/local_build_common.sh",
            "RECIPE_TOOLCHAIN_SYSROOT_FLAG=--sysroot=/recipe/sysroot",
            "local_build_kbuild_ccache_args args aarch64-poky-linux-",
            'printf "%s\\n" "${args[@]}"',
        )
    )

    result = run_bash(command, env)

    assert result.returncode == 0, output_of(result)
    assert result.stdout.strip() == (
        "CC=aarch64-poky-linux-gcc --sysroot=/recipe/sysroot"
    )
