const PROJECT_ROOT = "/build/arm/arm-auto-solutions";

const INTERESTING_EVENTS = new Set([
  "session-start",
  "turn-complete",
  "pre-tool-use",
  "post-tool-use",
]);

const PROJECT_CONTEXT = Object.freeze({
  project: "arm-auto-solutions",
  root: PROJECT_ROOT,
  current_config: ".config.yaml",
  docs: [
    "doc/README.md",
    "doc/project-architecture.md",
    "doc/yocto-build-and-kas.md",
    "doc/yocto-layer-and-recipe-map.md",
    "doc/yocto-layer-recipe-review.md",
    "doc/linux-kernel-source-review.md",
    "doc/safety-island-and-zephyr.md",
    "doc/validation-ci-and-runtime.md",
    "doc/generated-artifacts-and-risks.md",
    "doc/codex-project-expert-workflow.md",
  ],
  codex: {
    agent: ".codex/agents/arm-auto-solutions-expert.toml",
    agents: {
      general: ".codex/agents/arm-auto-solutions-expert.toml",
      yocto: ".codex/agents/yocto-expert.toml",
      zephyr: ".codex/agents/zephyr-expert.toml",
      linux_kernel: ".codex/agents/linux-kernel-expert.toml",
      arm: ".codex/agents/arm-expert.toml",
      test: ".codex/agents/test-expert.toml",
      debug: ".codex/agents/debug-expert.toml",
    },
    skill: ".codex/skills/arm-auto-solutions/SKILL.md",
    yocto_review_skill: ".codex/skills/yocto-review/SKILL.md",
    linux_kernel_review_skill: ".codex/skills/linux-kernel-review/SKILL.md",
    review_reference:
      ".codex/skills/arm-auto-solutions/references/yocto-layer-recipe-review.md",
    auto_review_hook: ".omx/hooks/yocto-auto-review.mjs",
    linux_kernel_auto_review_hook: ".omx/hooks/linux-kernel-auto-review.mjs",
  },
  guardrails: [
    "Root is a kas workspace, not a Git repository.",
    "Use git -C for nested source repositories.",
    "Treat build/ as generated evidence, not source.",
    "Separate static, build, and runtime/FVP validation claims.",
  ],
});

function normalizePath(value) {
  return String(value || "").replace(/\/+$/, "");
}

function eventCwd(event) {
  const context = event?.context || {};
  return normalizePath(
    context.cwd ||
      context.working_directory ||
      context.projectRoot ||
      process.cwd(),
  );
}

function isProjectEvent(event) {
  const cwd = eventCwd(event);
  return cwd === PROJECT_ROOT || cwd.startsWith(`${PROJECT_ROOT}/`);
}

export async function onHookEvent(event, sdk) {
  if (!INTERESTING_EVENTS.has(String(event?.event || ""))) {
    return;
  }

  if (!isProjectEvent(event)) {
    return;
  }

  const snapshot = {
    ...PROJECT_CONTEXT,
    updated_at: new Date().toISOString(),
    last_event: event.event,
    source: event.source || "unknown",
    session_id: event.session_id || null,
    thread_id: event.thread_id || null,
  };

  await sdk.state.write("context", snapshot);

  if (event.event === "session-start" || event.event === "turn-complete") {
    await sdk.log.info("arm-auto-solutions context refreshed", {
      root: PROJECT_ROOT,
      event: event.event,
      skill: PROJECT_CONTEXT.codex.skill,
      agent: PROJECT_CONTEXT.codex.agent,
      agents: Object.keys(PROJECT_CONTEXT.codex.agents),
    });
  }
}
