#!/usr/bin/env python3
"""Validate project-local agent, skill, and documentation contracts."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
import tomllib

import yaml


EXPECTED_ROUTES = {
    "arm-auto-solutions-expert": ("gpt-5.6-terra", "medium", "read-only"),
    "arm-expert": ("gpt-5.6-sol", "high", "workspace-write"),
    "debug-expert": ("gpt-5.6-sol", "xhigh", "workspace-write"),
    "linux-kernel-expert": ("gpt-5.6-sol", "high", "workspace-write"),
    "qbox_dev": ("gpt-5.6-sol", "high", "workspace-write"),
    "systemc_dev": ("gpt-5.6-sol", "high", "workspace-write"),
    "test-expert": ("gpt-5.6-terra", "medium", "workspace-write"),
    "yocto-expert": ("gpt-5.6-sol", "high", "read-only"),
    "yocto_dev": ("gpt-5.6-sol", "high", "workspace-write"),
    "zephyr-expert": ("gpt-5.6-sol", "high", "workspace-write"),
}
EXPECTED_SKILLS = {
    "arm-auto-solutions",
    "github-push",
    "linux-kernel-review",
    "qbox-dev",
    "systemc-dev",
    "update-codebase-indexes",
    "update-local-build-conf",
    "yocto-dev",
    "yocto-review",
}
DOC_REQUIREMENTS = {
    "AGENTS.md": ("Current machine: `apollo-qvp`", "nexios-image"),
    "README.md": ("Apollo QVP", "build/local-${MACHINE}"),
    "scripts/README.md": ("build/local-${MACHINE}", "apollo-qvp"),
    "hsoc-stack/components/system_mgmt/zephyrproject/README.md": ("Apollo QVP", "zephyr_hsoc_src"),
    "hsoc-stack/tools/qbox-platform/README.md": ("hsoc-stack/tools/qbox-platform", "qemu-components/rse_cpu_accel", "apollo-qvp"),
    "hsoc-stack/tools/qbox-platform/platforms/apollo/README.md": ("build/local-${MACHINE}", "apollo-qvp"),
}


@dataclass(frozen=True, slots=True)
class Violation:
    code: str
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class AgentRoute:
    name: str
    model: str
    reasoning_effort: str
    sandbox_mode: str


def add_missing_path(root: Path, relative: str, violations: list[Violation]) -> None:
    if not (root / relative).exists():
        violations.append(Violation("missing-path", relative, "required path is absent"))


def validate_topology(root: Path, violations: list[Violation]) -> list[str]:
    checked = ["build/conf/local.conf", "build/conf/bblayers.conf", "build/conf/templateconf.cfg", ".codex/config.toml", "AGENTS.md"]
    for relative in checked:
        add_missing_path(root, relative, violations)
    for relative in (
        ".git",
        "hsoc-stack/tools/buildroot",
        "hsoc-stack/tools/qbox",
        "hsoc-stack/tools/qbox-platform",
        "hsoc-stack/tools/qemu",
        "hsoc-stack/components/system_mgmt/zephyrproject/zephyr",
        "hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src",
    ):
        add_missing_path(root, relative, violations)
    local_conf = root / "build/conf/local.conf"
    template = root / "build/conf/templateconf.cfg"
    codex_config = root / ".codex/config.toml"
    agents = root / "AGENTS.md"
    if local_conf.exists():
        text = local_conf.read_text(encoding="utf-8")
        for token in ('MACHINE ??= "apollo-qvp"', 'TMPDIR = "${TOPDIR}/tmp_baremetal"'):
            if token not in text:
                violations.append(Violation("stale-topology", str(local_conf.relative_to(root)), f"missing {token}"))
    if template.exists() and "templates/apollo-qvp" not in template.read_text(encoding="utf-8"):
        violations.append(Violation("stale-topology", str(template.relative_to(root)), "active template is not apollo-qvp"))
    if codex_config.exists():
        config = tomllib.loads(codex_config.read_text(encoding="utf-8"))
        if (config.get("model"), config.get("model_reasoning_effort")) != ("gpt-5.6-sol", "high"):
            violations.append(Violation("stale-model-default", ".codex/config.toml", "expected gpt-5.6-sol with high effort"))
    if agents.exists():
        text = agents.read_text(encoding="utf-8")
        for token in DOC_REQUIREMENTS["AGENTS.md"]:
            if token not in text:
                violations.append(Violation("stale-guidance", "AGENTS.md", f"missing {token}"))
    return checked


def validate_agents(root: Path, violations: list[Violation]) -> tuple[list[str], list[AgentRoute]]:
    agent_dir = root / ".codex/agents"
    paths = sorted(agent_dir.glob("*.toml"))
    hook = root / ".omx/hooks/arm-auto-solutions-context.mjs"
    routes: list[AgentRoute] = []
    names: set[str] = set()
    for path in paths:
        relative = str(path.relative_to(root))
        try:
            config = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            violations.append(Violation("invalid-agent-toml", relative, str(error)))
            continue
        name = config.get("name")
        model_value = config.get("model")
        effort_value = config.get("model_reasoning_effort")
        sandbox_value = config.get("sandbox_mode")
        if not isinstance(name, str):
            violations.append(Violation("missing-agent-name", relative, "name must be a string"))
            continue
        if name in names:
            violations.append(Violation("duplicate-agent-name", relative, name))
        names.add(name)
        if not (isinstance(model_value, str) and isinstance(effort_value, str) and isinstance(sandbox_value, str)):
            violations.append(Violation("incomplete-agent-route", relative, "model, effort, and sandbox must be explicit"))
            continue
        model, effort, sandbox = model_value, effort_value, sandbox_value
        route = (model, effort, sandbox)
        routes.append(AgentRoute(name, model, effort, sandbox))
        if EXPECTED_ROUTES.get(name) != route:
            violations.append(Violation("unexpected-agent-route", relative, f"expected {EXPECTED_ROUTES.get(name)}, got {route}"))
        instructions = config.get("developer_instructions", "")
        for stale in (".config.yaml", "fvp-rd-aspen", "components/safety_island/zephyr/src"):
            if stale in instructions:
                violations.append(Violation("stale-agent-guidance", relative, f"contains {stale}"))
        if "build/conf/local.conf" not in instructions:
            violations.append(Violation("missing-agent-intake", relative, "missing active build config intake"))
    missing = sorted(set(EXPECTED_ROUTES) - names)
    extra = sorted(names - set(EXPECTED_ROUTES))
    if missing:
        violations.append(Violation("missing-agents", ".codex/agents", ", ".join(missing)))
    if extra:
        violations.append(Violation("unexpected-agents", ".codex/agents", ", ".join(extra)))
    add_missing_path(root, str(hook.relative_to(root)), violations)
    if hook.exists():
        hook_text = hook.read_text(encoding="utf-8")
        for token in ("build/conf/local.conf", "qbox_dev.toml", "systemc_dev.toml", "yocto_dev.toml"):
            if token not in hook_text:
                violations.append(Violation("stale-agent-hook", str(hook.relative_to(root)), f"missing {token}"))
    return [str(path.relative_to(root)) for path in paths] + [str(hook.relative_to(root))], routes


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if match is None:
        return {}, text
    payload = yaml.safe_load(match.group(1))
    return payload if isinstance(payload, dict) else {}, text


def validate_skills(root: Path, violations: list[Violation]) -> list[str]:
    skill_dir = root / ".codex/skills"
    paths = sorted(skill_dir.glob("*/SKILL.md"))
    names: set[str] = set()
    for path in paths:
        relative = str(path.relative_to(root))
        try:
            metadata, text = frontmatter(path)
        except yaml.YAMLError as error:
            metadata, text = {}, path.read_text(encoding="utf-8")
            violations.append(Violation("invalid-skill-yaml", relative, str(error)))
        name = metadata.get("name")
        if name != path.parent.name:
            violations.append(Violation("invalid-skill-frontmatter", relative, "name must match directory"))
        if not isinstance(metadata.get("description"), str):
            violations.append(Violation("invalid-skill-frontmatter", relative, "description must be a string"))
        if isinstance(name, str):
            names.add(name)
        openai = path.parent / "agents/openai.yaml"
        if not openai.exists():
            violations.append(Violation("missing-skill-interface", str(openai.relative_to(root)), "agents/openai.yaml is absent"))
        else:
            try:
                interface = yaml.safe_load(openai.read_text(encoding="utf-8"))
            except yaml.YAMLError as error:
                interface = {}
                violations.append(Violation("invalid-skill-interface-yaml", str(openai.relative_to(root)), str(error)))
            if not isinstance(interface, dict) or not isinstance(interface.get("interface"), dict):
                violations.append(Violation("invalid-skill-interface", str(openai.relative_to(root)), "interface mapping is absent"))
        if path.parent.name == "yocto-dev" and len(text.splitlines()) >= 500:
            violations.append(Violation("oversized-skill", relative, "SKILL.md must stay below 500 lines"))
    if names != EXPECTED_SKILLS:
        violations.append(Violation("skill-inventory-mismatch", ".codex/skills", f"expected {sorted(EXPECTED_SKILLS)}, got {sorted(names)}"))
    requirements = {
        "arm-auto-solutions": ("hsoc-stack/tools/buildroot", "agent_type", "gpt-5.6-terra", "gpt-5.6-sol"),
        "github-push": ("top-level", "recursive submodules", "gpt-5.6-sol"),
        "linux-kernel-review": ("hsoc-stack/components/primary_compute/linux", "agent_type", "linux-kernel-expert", "gpt-5.6-sol"),
        "qbox-dev": ("./local_build.sh qbox", "agent_type", "qbox_dev", "gpt-5.6-sol"),
        "systemc-dev": ("build/local-${MACHINE}/work/qbox-platform", "agent_type", "systemc_dev", "gpt-5.6-sol"),
        "yocto-dev": ("build/tmp_baremetal", "agent_type", "yocto_dev", "gpt-5.6-sol"),
        "yocto-review": ("meta-hsoc-auto-solutions", "agent_type", "yocto-expert", "gpt-5.6-sol"),
    }
    by_name = {path.parent.name: path for path in paths}
    for name, tokens in requirements.items():
        path = by_name.get(name)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                violations.append(Violation("stale-skill-guidance", str(path.relative_to(root)), f"missing {token}"))
    return [str(path.relative_to(root)) for path in paths]


def validate_docs(root: Path, violations: list[Violation]) -> list[str]:
    for relative, tokens in DOC_REQUIREMENTS.items():
        path = root / relative
        add_missing_path(root, relative, violations)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                violations.append(Violation("stale-doc-guidance", relative, f"missing {token}"))
    return sorted(DOC_REQUIREMENTS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", choices=("all", "topology", "agents", "skills", "docs"), default="all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    violations: list[Violation] = []
    checked_paths: list[str] = []
    routes: list[AgentRoute] = []
    if args.check in ("all", "topology"):
        checked_paths.extend(validate_topology(root, violations))
    if args.check in ("all", "agents"):
        agent_paths, routes = validate_agents(root, violations)
        checked_paths.extend(agent_paths)
    if args.check in ("all", "skills"):
        checked_paths.extend(validate_skills(root, violations))
    if args.check in ("all", "docs"):
        checked_paths.extend(validate_docs(root, violations))
    report = {
        "passed": not violations,
        "check": args.check,
        "inventory": {"agents": len(routes), "skills": len(list((root / ".codex/skills").glob("*/SKILL.md")))},
        "agents": [asdict(route) for route in routes],
        "checked_paths": sorted(set(checked_paths)),
        "allowlisted_fvp_references": ["apollo_fvp identifiers", "explicit FVP comparison and debug workflows"],
        "violations": [asdict(violation) for violation in violations],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
