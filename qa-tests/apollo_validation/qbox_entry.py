from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import TextIO

from .context import inspect_context
from .evidence import append_record, now, run_log, write_json
from .fvp_reference import (
    FVPReferenceError,
    FVPReferenceRequest,
    validate_fvp_reference,
)
from .listing import run_list
from .profiles import load_test_profile
from .provenance import (
    ProfileProvenance,
    JsonValue,
    ProvenanceError,
    ProvenanceRequest,
    capture_profile_provenance,
)
from .qbox_runner import QBoxRunRequest, run_qbox_category
from .root_cli import RootOptions, parse_root_args
from .root_runner import (
    _acquire_lock,
    _print_result,
    _run_dir,
    _validate_request,
)
from .run_inputs import capture_run_inputs
from .selection import SelectionError, prepare_selection, write_selection_evidence


def _profile_provenance(
    root: Path,
    options: RootOptions,
    context: dict[str, JsonValue],
) -> ProfileProvenance:
    profile_name = options.test_profile
    if profile_name is None:
        raise ProvenanceError("blocked_fvp_reference_profile_mismatch")
    profile = load_test_profile(
        root,
        profile_name,
        options.backend,
        options.image_profile,
    )
    raw_cpu_count = context.get("pc_cpus_count_default")
    if type(raw_cpu_count) is not int:
        raise ProvenanceError("blocked_fvp_reference_cpu_mismatch")
    return capture_profile_provenance(
        ProvenanceRequest(
            root=root,
            build_dir=options.build_dir,
            backend=options.backend,
            machine=options.machine,
            image=options.image,
            image_profile=options.image_profile,
            profile_id=profile_name,
            selectors=profile.selectors,
            cpu_count=raw_cpu_count,
        )
    )


def request_uses_qbox(argv: list[str]) -> bool:
    for index, argument in enumerate(argv):
        if argument == "--qbox" or argument == "--machine=apollo-qvp":
            return True
        if argument == "--machine" and index + 1 < len(argv):
            return argv[index + 1] == "apollo-qvp"
    return False


def _write_qbox_context(
    root: Path,
    options: RootOptions,
    run_dir: Path,
) -> int:
    run_log("START context")
    context = inspect_context(
        root,
        options.build_dir,
        options.machine,
        options.image,
        options.backend,
    )
    context.update(
        {
            "backend": options.backend,
            "image_profile": options.image_profile,
            "test_profile": options.test_profile,
        }
    )
    if options.test_profile is not None:
        provenance = _profile_provenance(root, options, context)
        reference_path = options.fvp_reference
        if reference_path is None:
            raise FVPReferenceError("blocked_fvp_reference_required")
        accepted = validate_fvp_reference(
            FVPReferenceRequest(root, reference_path, run_dir.name, provenance)
        )
        context["provenance"] = provenance.as_json()
        context["accepted_fvp_reference"] = accepted.as_json()
    input_manifest = capture_run_inputs(root, run_dir, context)
    manifest_path = run_dir / "manifest.json"
    write_json(manifest_path, context)
    status = "blocked" if context.get("status") == "blocked" else "pass"
    append_record(
        run_dir / "commands.jsonl",
        {
            "name": "context",
            "argv": ["apollo_validation.cli", "context", "--qbox"],
            "status": status,
            "started_at": now(),
            "finished_at": now(),
            "required": True,
            "artifacts": [
                {"kind": "manifest", "path": str(manifest_path)},
                {"kind": "input_manifest", "path": str(input_manifest)},
            ],
            "blockers": context.get("blockers", []),
        },
    )
    run_log(f"DONE context ({status})")
    return 2 if status == "blocked" else 0


def _qbox_request(
    root: Path,
    options: RootOptions,
    run_dir: Path,
) -> QBoxRunRequest:
    return QBoxRunRequest(
        root=root,
        build_dir=options.build_dir,
        machine=options.machine,
        image=options.image,
        image_profile=options.image_profile,
        timeout=(
            options.timeout_oeqa
            if options.test_profile is not None
            else options.timeout_fvp
        ),
        out_dir=run_dir,
        dry_run=options.dry_run or options.skip_runtime,
        preflight_only=options.preflight_only,
        test_profile=options.test_profile,
    )


def run_qbox_root(root: Path, argv: list[str]) -> int:
    try:
        options = parse_root_args(argv)
    except SystemExit as error:
        return int(error.code) if isinstance(error.code, int) else 64
    run_dir = _run_dir(root, options)
    rejection = _validate_request(root, options.build_dir, run_dir)
    if rejection is not None:
        print(f"error: {rejection}", file=sys.stderr)
        return 64
    if options.tui:
        print("error: QBox validation currently requires --headless", file=sys.stderr)
        return 64
    try:
        selection, options = prepare_selection(root, options)
    except SelectionError as error:
        print(f"error: {error}", file=sys.stderr)
        return 64
    if options.test_profile is not None and options.fvp_reference is None:
        print("error: blocked_fvp_reference_required", file=sys.stderr)
        return 64

    run_dir.mkdir(parents=True, exist_ok=True)
    os.environ["APOLLO_RUN_TEST_LOG"] = str(run_dir / "logs/runner.log")
    run_log("Environment")
    run_log(f"  backend: {options.backend}")
    run_log(f"  machine: {options.machine}")
    run_log(f"  image: {options.image}")
    run_log(f"  run_dir: {run_dir}")
    run_log(f"  timeout_boot: {options.timeout_fvp}")
    try:
        if _write_qbox_context(root, options, run_dir) != 0:
            return _print_result(root, run_dir)
    except (FVPReferenceError, ProvenanceError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 64
    if selection is not None:
        write_selection_evidence(run_dir, selection)
    if options.list_suites:
        category = options.category if options.category_requested else None
        run_list(run_dir, category)
        return _print_result(root, run_dir)

    lock_handle: TextIO | None = None
    if options.preflight_only or not (options.dry_run or options.skip_runtime):
        lock_result, lock_handle = _acquire_lock(root, run_dir)
        if lock_result != 0:
            return _print_result(root, run_dir)
    try:
        run_qbox_category(_qbox_request(root, options, run_dir), options.category)
    except KeyboardInterrupt:
        timestamp = now()
        append_record(
            run_dir / "commands.jsonl",
            {
                "name": "interrupt",
                "argv": ["KeyboardInterrupt"],
                "status": "blocked",
                "started_at": timestamp,
                "finished_at": timestamp,
                "required": True,
                "blockers": [{"reason": "blocked_interrupted"}],
            },
        )
    finally:
        if lock_handle is not None:
            lock_handle.close()
    return _print_result(root, run_dir)
