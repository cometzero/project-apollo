from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import TypeAlias

from .evidence import write_json
from .backend import Backend, ImageProfile
from .provenance import (
    JsonValue,
    ProvenanceError,
    ProvenanceRequest,
    capture_profile_provenance,
)
from .profiles import load_test_profile


JsonObject: TypeAlias = dict[str, JsonValue]


def _mapping(value: JsonValue) -> JsonObject:
    return value if isinstance(value, dict) else {}


def _string(value: JsonValue) -> str:
    return value if isinstance(value, str) else ""


def _integer(value: JsonValue) -> int:
    if type(value) is not int:
        raise ProvenanceError("blocked_fvp_reference_cpu_mismatch")
    return value


def _attach_profile_provenance(
    root: Path,
    run_dir: Path,
    context: JsonObject,
) -> None:
    profile_id = _string(context.get("test_profile"))
    if not profile_id or isinstance(context.get("provenance"), dict):
        return
    selection_path = run_dir / "selection.json"
    backends: dict[str, Backend] = {"fvp": "fvp", "qbox": "qbox"}
    backend = backends.get(_string(context.get("backend")))
    images: dict[str, ImageProfile] = {"bsp": "bsp", "product": "product"}
    image_profile = images.get(_string(context.get("image_profile")))
    if backend is None or image_profile is None:
        raise ProvenanceError("blocked_fvp_reference_malformed")
    if selection_path.is_file():
        try:
            loaded: JsonValue = json.loads(selection_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ProvenanceError("blocked_fvp_reference_malformed") from error
        raw_selectors = _mapping(loaded).get("ordered_tests")
        if not isinstance(raw_selectors, list):
            raise ProvenanceError("blocked_fvp_reference_selector_mismatch")
        selectors = tuple(_string(item) for item in raw_selectors)
    else:
        selectors = load_test_profile(
            root,
            profile_id,
            backend,
            image_profile,
        ).selectors
    if not selectors or any(not item for item in selectors):
        raise ProvenanceError("blocked_fvp_reference_selector_mismatch")
    testdata_path = Path(_string(context.get("testdata_path")))
    provenance = capture_profile_provenance(
        ProvenanceRequest(
            root=root,
            build_dir=testdata_path.parents[4],
            backend=backend,
            machine=_string(context.get("machine")),
            image=_string(context.get("image")),
            image_profile=image_profile,
            profile_id=profile_id,
            selectors=selectors,
            cpu_count=_integer(context.get("pc_cpus_count_default")),
        )
    )
    context["provenance"] = provenance.as_json()


def _git_revision(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plugin_receipts(context: JsonObject) -> list[JsonValue]:
    runtime_config = _mapping(context.get("runtime_config"))
    fvpconf_path = Path(_string(runtime_config.get("path")))
    if not fvpconf_path.is_file():
        return []
    try:
        fvpconf = _mapping(json.loads(fvpconf_path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as error:
        raise ProvenanceError("blocked_missing_crypto_plugin") from error
    args = fvpconf.get("args")
    if not isinstance(args, list):
        return []
    receipts: list[JsonValue] = []
    for index, raw_arg in enumerate(args[:-1]):
        plugin_path = args[index + 1]
        if raw_arg != "--plugin" or not isinstance(plugin_path, str):
            continue
        original = Path(plugin_path)
        try:
            resolved = original.resolve(strict=True)
            if not resolved.is_file():
                raise OSError
            digest = _file_digest(resolved)
        except OSError as error:
            raise ProvenanceError("blocked_missing_crypto_plugin") from error
        receipts.append(
            {
                "path": str(original),
                "resolved_path": str(resolved),
                "sha256": digest,
            }
        )
    return receipts


def capture_run_inputs(
    root: Path,
    run_dir: Path,
    context: JsonObject,
    *,
    attach_profile_provenance: bool = True,
) -> Path:
    if attach_profile_provenance:
        _attach_profile_provenance(root, run_dir, context)
    context["input_revisions"] = {
        "workspace": _git_revision(root),
        "qa_runner": _git_revision(root),
        "bsp_layer": _git_revision(root / "hsoc-stack/yocto/meta-hsoc-bsp"),
        "platform_layer": _git_revision(
            root / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
        ),
    }
    evidence_dir = run_dir / "evidence"
    runtime_config = _mapping(context.get("runtime_config"))
    input_paths = {
        "testdata": context.get("testdata_path"),
        "runtime_config": runtime_config.get("path"),
    }
    entries: list[JsonValue] = []
    for kind, raw_path in input_paths.items():
        if not isinstance(raw_path, str) or not raw_path:
            continue
        source = Path(raw_path)
        if not source.is_file():
            continue
        evidence_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix if kind == "runtime_config" else ".testdata.json"
        snapshot = evidence_dir / f"resolved{suffix}"
        shutil.copy2(source, snapshot)
        entries.append(
            {
                "kind": kind,
                "source": str(source),
                "snapshot": str(snapshot),
                "size": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        )
    path = evidence_dir / "input-manifest.json"
    payload: JsonObject = {"inputs": entries}
    plugins = _plugin_receipts(context)
    if plugins:
        payload["plugins"] = plugins
    provenance = context.get("provenance")
    if isinstance(provenance, dict):
        payload["provenance"] = provenance
    accepted = context.get("accepted_fvp_reference")
    if isinstance(accepted, dict):
        payload["accepted_fvp_reference"] = accepted
    comparison_mode = context.get("comparison_mode")
    if isinstance(comparison_mode, str):
        payload["comparison_mode"] = comparison_mode
    write_json(path, payload)
    return path
