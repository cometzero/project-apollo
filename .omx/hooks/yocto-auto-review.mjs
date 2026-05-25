const PROJECT_ROOT = "/build/arm/arm-auto-solutions";
const STATE_KEY = "review";
const MAX_PENDING_PATHS = 40;
const MAX_PROMPT_PATHS = 16;

const WATCH_EVENTS = new Set(["post-tool-use", "turn-complete"]);
const IGNORED_PREFIXES = [
  ".codex/",
  ".omx/",
  "doc/",
  "build/",
];

const SOURCE_PREFIXES = [
  "arm-zena-css/yocto/",
  "sw-ref-stack/yocto/",
  "layers/",
];

const YOCTO_EXT_RE =
  /\.(bb|bbappend|bbclass|inc|conf|patch|scc|cfg|wks|yml|yaml)$/;

function normalizePath(value) {
  let path = String(value || "")
    .trim()
    .replace(/^["'`]+|["'`,:)]+$/g, "")
    .replace(/\\/g, "/");
  if (path.startsWith(`${PROJECT_ROOT}/`)) {
    path = path.slice(PROJECT_ROOT.length + 1);
  }
  if (path.startsWith("./")) {
    path = path.slice(2);
  }
  return path.replace(/\/+/g, "/");
}

function eventCwd(event) {
  const context = event?.context || {};
  return String(
    context.cwd ||
      context.working_directory ||
      context.projectRoot ||
      context.project_path ||
      process.cwd(),
  ).replace(/\/+$/, "");
}

function isProjectEvent(event) {
  const cwd = eventCwd(event);
  return cwd === PROJECT_ROOT || cwd.startsWith(`${PROJECT_ROOT}/`);
}

function isYoctoReviewPath(value) {
  const path = normalizePath(value);
  if (!path || path.includes("\u0000") || path.includes("..")) {
    return false;
  }
  if (IGNORED_PREFIXES.some((prefix) => path.startsWith(prefix))) {
    return false;
  }
  if (!SOURCE_PREFIXES.some((prefix) => path.startsWith(prefix))) {
    return false;
  }
  if (!YOCTO_EXT_RE.test(path)) {
    return false;
  }
  return (
    path.includes("/conf/") ||
    path.includes("/classes/") ||
    path.includes("/recipes-") ||
    path.includes("/dynamic-layers/") ||
    path.includes("/files/") ||
    path.includes("/kas/") ||
    path.includes("/wks/")
  );
}

function addPath(paths, path, action = "touched") {
  const normalized = normalizePath(path);
  if (!isYoctoReviewPath(normalized)) {
    return;
  }
  const existing = paths.get(normalized);
  if (existing) {
    existing.action = existing.action === "created" ? "created" : action;
    return;
  }
  paths.set(normalized, { path: normalized, action });
}

function stringify(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value || "");
  }
}

function looksWriteLikePayload(text) {
  return /(\*\*\* Add File:|\*\*\* Update File:|^\+\+\+\s+b\/|^\s*(?:[ MADRCU?][MADRCU?]|\?\?)\s+|apply_patch|git status|git diff --name|writeFile|touch\s|tee\s|cat\s+>|sed\s+-i|cp\s|mv\s)/m.test(
    String(text || ""),
  );
}

function extractPathsFromText(text) {
  const paths = new Map();
  const body = String(text || "");

  for (const match of body.matchAll(/^\*\*\* Add File:\s+(.+)$/gm)) {
    addPath(paths, match[1], "created");
  }
  for (const match of body.matchAll(/^\*\*\* Update File:\s+(.+)$/gm)) {
    addPath(paths, match[1], "updated");
  }
  for (const match of body.matchAll(/^\+\+\+\s+b\/(.+)$/gm)) {
    addPath(paths, match[1], "updated");
  }
  for (const match of body.matchAll(/^---\s+a\/(.+)$/gm)) {
    addPath(paths, match[1], "updated");
  }
  for (const match of body.matchAll(/^\s*(?:[ MADRCU?][MADRCU?]|\?\?)\s+(.+)$/gm)) {
    const action = match[0].includes("?") || match[0].includes("A")
      ? "created"
      : "updated";
    addPath(paths, match[1], action);
  }

  if (looksWriteLikePayload(body)) {
    const tokenRe =
      /(?:^|[\s"'`(])((?:\.\/)?(?:arm-zena-css|sw-ref-stack|layers)\/[A-Za-z0-9._@%+:/=-]+?\.(?:bbappend|bbclass|bb|inc|conf|patch|scc|cfg|wks|ya?ml))(?:$|[\s"'`,)])/gm;
    for (const match of body.matchAll(tokenRe)) {
      addPath(paths, match[1], "touched");
    }
  }

  return [...paths.values()].sort((a, b) => a.path.localeCompare(b.path));
}

function extractPathsFromPayload(value, seen = new Set()) {
  const paths = new Map();

  function merge(items) {
    for (const item of items) {
      paths.set(item.path, item);
    }
  }

  function visit(item) {
    if (typeof item === "string") {
      merge(extractPathsFromText(item));
      return;
    }
    if (!item || typeof item !== "object") {
      return;
    }
    if (seen.has(item)) {
      return;
    }
    seen.add(item);
    if (Array.isArray(item)) {
      for (const child of item) {
        visit(child);
      }
      return;
    }
    for (const child of Object.values(item)) {
      visit(child);
    }
  }

  visit(value);
  return [...paths.values()].sort((a, b) => a.path.localeCompare(b.path));
}

function fingerprint(paths) {
  return paths
    .map((entry) => entry.path)
    .sort()
    .join("\n");
}

function compactPending(entries) {
  const merged = new Map();
  for (const entry of entries || []) {
    if (!entry || !entry.path) {
      continue;
    }
    const normalized = normalizePath(entry.path);
    if (!isYoctoReviewPath(normalized)) {
      continue;
    }
    merged.set(normalized, {
      path: normalized,
      action: entry.action || "touched",
      first_seen_at: entry.first_seen_at || new Date().toISOString(),
      last_seen_at: entry.last_seen_at || new Date().toISOString(),
    });
  }
  return [...merged.values()]
    .sort((a, b) => a.path.localeCompare(b.path))
    .slice(-MAX_PENDING_PATHS);
}

async function queueReview(event, sdk) {
  const context = event.context || {};
  const payload = context.payload || context;
  const detected = extractPathsFromPayload(payload);
  if (detected.length === 0) {
    return;
  }

  const now = new Date().toISOString();
  const state = (await sdk.state.read(STATE_KEY, {})) || {};
  const pending = compactPending(state.pending_paths || []);
  const byPath = new Map(pending.map((entry) => [entry.path, entry]));

  for (const item of detected) {
    const existing = byPath.get(item.path);
    byPath.set(item.path, {
      path: item.path,
      action: existing?.action === "created" ? "created" : item.action,
      first_seen_at: existing?.first_seen_at || now,
      last_seen_at: now,
    });
  }

  const pendingPaths = compactPending([...byPath.values()]);
  await sdk.state.write(STATE_KEY, {
    enabled: true,
    status: "pending",
    pending_paths: pendingPaths,
    pending_count: pendingPaths.length,
    last_detection: {
      at: now,
      event: event.event,
      tool_name:
        payload.tool_name ||
        payload.toolName ||
        payload.tool ||
        context.tool_name ||
        "unknown",
      paths: detected,
    },
    last_sent_fingerprint: state.last_sent_fingerprint || "",
    last_sent_at: state.last_sent_at || null,
  });

  await sdk.log.warn("yocto metadata review queued", {
    skill: "$yocto-review",
    paths: detected.map((entry) => entry.path),
  });
}

function buildPrompt(paths) {
  const shown = paths.slice(0, MAX_PROMPT_PATHS);
  const extra = paths.length - shown.length;
  const bullets = shown.map((entry) => `- ${entry.path}`).join("\n");
  const suffix = extra > 0 ? `\n- ... ${extra} more path(s)` : "";
  return [
    "$yocto-review Auto-review newly created or changed Yocto metadata files.",
    "",
    bullets + suffix,
    "",
    "Use doc/yocto-layer-recipe-review.md and report static, parse, task, image, and runtime evidence separately.",
  ].join("\n");
}

async function maybeSendReviewPrompt(event, sdk) {
  const state = (await sdk.state.read(STATE_KEY, {})) || {};
  const pending = compactPending(state.pending_paths || []);
  if (pending.length === 0) {
    return;
  }

  const currentFingerprint = fingerprint(pending);
  if (state.last_sent_fingerprint === currentFingerprint) {
    return;
  }

  const prompt = buildPrompt(pending);
  const result = await sdk.tmux.sendKeys({
    text: prompt,
    cooldownMs: 1000,
  });

  const now = new Date().toISOString();
  await sdk.state.write(STATE_KEY, {
    ...state,
    status: result.ok ? "sent" : "pending",
    pending_paths: pending,
    pending_count: pending.length,
    last_sent_fingerprint: result.ok
      ? currentFingerprint
      : state.last_sent_fingerprint || "",
    last_sent_at: result.ok ? now : state.last_sent_at || null,
    last_send_result: {
      at: now,
      ok: result.ok,
      reason: result.reason,
      target: result.target || null,
    },
  });

  const logPayload = {
    skill: "$yocto-review",
    pending_count: pending.length,
    result: result.reason,
  };
  if (result.ok) {
    await sdk.log.info("yocto metadata auto-review prompt sent", logPayload);
  } else {
    await sdk.log.warn("yocto metadata auto-review prompt not sent", logPayload);
  }
}

export async function onHookEvent(event, sdk) {
  if (!WATCH_EVENTS.has(String(event?.event || ""))) {
    return;
  }
  if (!isProjectEvent(event)) {
    return;
  }

  if (event.event === "post-tool-use") {
    await queueReview(event, sdk);
    return;
  }

  if (event.event === "turn-complete") {
    await maybeSendReviewPrompt(event, sdk);
  }
}
