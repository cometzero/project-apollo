import assert from "node:assert/strict";
import test from "node:test";

import {
  LspFrameRewriter,
  rewriteInitializePayload,
} from "../scripts/lsp/devicetree_lsp_wrapper.mjs";

test("initialize rewrite removes unsupported workspaceFolders", () => {
  const payload = Buffer.from(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      capabilities: {
        workspace: {
          configuration: true,
          workspaceFolders: true,
        },
      },
    },
  }));

  const rewritten = JSON.parse(rewriteInitializePayload(payload).toString());

  assert.equal(rewritten.params.capabilities.workspace.configuration, true);
  assert.equal("workspaceFolders" in rewritten.params.capabilities.workspace, false);
});

test("frame rewriter accepts a fragmented initialize request", () => {
  const payload = Buffer.from(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: { capabilities: { workspace: { workspaceFolders: true } } },
  }));
  const frame = Buffer.concat([
    Buffer.from(`Content-Length: ${payload.length}\r\n\r\n`),
    payload,
  ]);
  const rewriter = new LspFrameRewriter();

  const first = rewriter.push(frame.subarray(0, 17));
  const second = rewriter.push(frame.subarray(17));

  assert.deepEqual(first, []);
  assert.equal(second.length, 1);
  assert.doesNotMatch(second[0].toString(), /workspaceFolders/);
});
