#!/usr/bin/env node

import { spawn } from "node:child_process";
import { pathToFileURL } from "node:url";

const HEADER_SEPARATOR = Buffer.from("\r\n\r\n");
const CONTENT_LENGTH = /(?:^|\r\n)Content-Length:\s*(\d+)/i;

function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function rewriteInitializePayload(payload) {
  const message = JSON.parse(payload.toString("utf8"));
  if (message.method !== "initialize" || !isRecord(message.params)) {
    return payload;
  }
  const capabilities = message.params.capabilities;
  if (!isRecord(capabilities) || !isRecord(capabilities.workspace)) {
    return payload;
  }

  const workspace = { ...capabilities.workspace };
  delete workspace.workspaceFolders;
  message.params = {
    ...message.params,
    capabilities: { ...capabilities, workspace },
  };
  return Buffer.from(JSON.stringify(message));
}

export class LspFrameRewriter {
  #buffer = Buffer.alloc(0);

  push(chunk) {
    this.#buffer = Buffer.concat([this.#buffer, chunk]);
    const frames = [];

    while (true) {
      const headerEnd = this.#buffer.indexOf(HEADER_SEPARATOR);
      if (headerEnd < 0) {
        return frames;
      }
      const header = this.#buffer.subarray(0, headerEnd).toString("ascii");
      const match = CONTENT_LENGTH.exec(header);
      if (match === null) {
        throw new Error("LSP frame is missing Content-Length");
      }
      const length = Number.parseInt(match[1], 10);
      const bodyStart = headerEnd + HEADER_SEPARATOR.length;
      const frameEnd = bodyStart + length;
      if (this.#buffer.length < frameEnd) {
        return frames;
      }

      const payload = rewriteInitializePayload(
        this.#buffer.subarray(bodyStart, frameEnd),
      );
      frames.push(Buffer.concat([
        Buffer.from(`Content-Length: ${payload.length}\r\n\r\n`),
        payload,
      ]));
      this.#buffer = this.#buffer.subarray(frameEnd);
    }
  }
}

function main() {
  const server = spawn("devicetree-language-server", ["--stdio"], {
    stdio: ["pipe", "pipe", "inherit"],
  });
  const rewriter = new LspFrameRewriter();

  process.stdin.on("data", (chunk) => {
    for (const frame of rewriter.push(chunk)) {
      server.stdin.write(frame);
    }
  });
  process.stdin.on("end", () => server.stdin.end());
  server.stdout.pipe(process.stdout);
  server.on("error", (error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
  server.on("exit", (code) => {
    process.exitCode = code ?? 1;
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
