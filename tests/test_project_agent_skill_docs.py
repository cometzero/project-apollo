from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/test/validate_project_agent_skill_docs.py"


def run_validator(root: Path, check: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(VALIDATOR), "--root", str(root), "--check", check],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_topology_matches_active_qvp_environment() -> None:
    # Given: the checked-out project and its active build configuration.
    # When: the topology contract is validated.
    result = run_validator(ROOT, "topology")
    # Then: source paths and top-level guidance agree with the QVP baseline.
    assert result.returncode == 0, result.stdout


def test_agent_routing_matches_task_complexity() -> None:
    # Given: all project-local Codex agent definitions.
    # When: explicit model, effort, and sandbox routing is validated.
    result = run_validator(ROOT, "agents")
    # Then: simple routing is light and specialist implementation stays deep.
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    routes = {agent["name"]: agent for agent in payload["agents"]}
    assert routes["arm-auto-solutions-expert"]["model"] == "gpt-5.6-terra"
    assert routes["arm-auto-solutions-expert"]["reasoning_effort"] == "medium"
    assert routes["debug-expert"]["model"] == "gpt-5.6-sol"
    assert routes["debug-expert"]["reasoning_effort"] == "xhigh"
    assert routes["test-expert"]["model"] == "gpt-5.6-terra"
    assert routes["qbox_dev"]["model"] == "gpt-5.6-sol"
    assert routes["yocto-expert"]["sandbox_mode"] == "read-only"
    assert routes["yocto_dev"]["sandbox_mode"] == "workspace-write"


def test_project_defaults_use_sol_for_skill_execution() -> None:
    # Given: project-local Codex defaults used when a skill runs in the leader.
    config_path = ROOT / ".codex/config.toml"
    # When: the project configuration is parsed.
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    # Then: skill execution defaults to the new Sol model at bounded effort.
    assert config["model"] == "gpt-5.6-sol"
    assert config["model_reasoning_effort"] == "high"
    registered = config["agents"]
    for name in (
        "arm-auto-solutions-expert",
        "arm-expert",
        "debug-expert",
        "linux-kernel-expert",
        "qbox_dev",
        "systemc_dev",
        "test-expert",
        "yocto-expert",
        "yocto_dev",
        "zephyr-expert",
    ):
        assert registered[name]["config_file"] == f"./agents/{name}.toml"


def test_skills_match_current_project_contract() -> None:
    # Given: all project-local skills and their OpenAI interfaces.
    # When: skill metadata and current source-path guidance are validated.
    result = run_validator(ROOT, "skills")
    # Then: every skill is well formed and uses the current project topology.
    assert result.returncode == 0, result.stdout


def test_docs_match_current_project_contract() -> None:
    # Given: the project-owned guidance document allowlist.
    # When: active QVP and dynamic local-build references are validated.
    result = run_validator(ROOT, "docs")
    # Then: every selected document contains the current workflow anchors.
    assert result.returncode == 0, result.stdout


def test_skills_reject_malformed_frontmatter(tmp_path: Path) -> None:
    # Given: a skill whose frontmatter name disagrees with its directory.
    skill = tmp_path / ".codex/skills/broken"
    (skill / "agents").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: different\ndescription: broken fixture\n---\n",
        encoding="utf-8",
    )
    (skill / "agents/openai.yaml").write_text(
        "interface:\n  display_name: Broken\n",
        encoding="utf-8",
    )
    # When: only skill contracts are checked.
    result = run_validator(tmp_path, "skills")
    # Then: the boundary reports a stable malformed-frontmatter code.
    assert result.returncode == 1
    codes = {item["code"] for item in json.loads(result.stdout)["violations"]}
    assert "invalid-skill-frontmatter" in codes


def test_agents_reject_malformed_toml(tmp_path: Path) -> None:
    # Given: an agent file that cannot be parsed as TOML.
    agent_dir = tmp_path / ".codex/agents"
    agent_dir.mkdir(parents=True)
    (agent_dir / "broken.toml").write_text('name = "unterminated\n', encoding="utf-8")
    # When: only agent contracts are checked.
    result = run_validator(tmp_path, "agents")
    # Then: the boundary reports a stable invalid-TOML code.
    assert result.returncode == 1
    codes = {item["code"] for item in json.loads(result.stdout)["violations"]}
    assert "invalid-agent-toml" in codes


def test_skills_report_invalid_frontmatter_yaml(tmp_path: Path) -> None:
    # Given: a skill whose frontmatter is syntactically invalid YAML.
    skill = tmp_path / ".codex/skills/broken"
    (skill / "agents").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: [\n---\n",
        encoding="utf-8",
    )
    (skill / "agents/openai.yaml").write_text(
        "interface:\n  display_name: Broken\n",
        encoding="utf-8",
    )
    # When: the skill boundary parses the frontmatter.
    result = run_validator(tmp_path, "skills")
    # Then: it emits JSON with a stable syntax violation instead of a traceback.
    assert result.returncode == 1
    codes = {item["code"] for item in json.loads(result.stdout)["violations"]}
    assert "invalid-skill-yaml" in codes


def test_skills_report_invalid_interface_yaml(tmp_path: Path) -> None:
    # Given: a valid skill entrypoint with a syntactically invalid UI interface.
    skill = tmp_path / ".codex/skills/broken"
    (skill / "agents").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: broken\ndescription: broken fixture\n---\n",
        encoding="utf-8",
    )
    (skill / "agents/openai.yaml").write_text("interface: [\n", encoding="utf-8")
    # When: the skill boundary parses agents/openai.yaml.
    result = run_validator(tmp_path, "skills")
    # Then: it emits JSON with a stable interface syntax violation.
    assert result.returncode == 1
    codes = {item["code"] for item in json.loads(result.stdout)["violations"]}
    assert "invalid-skill-interface-yaml" in codes
