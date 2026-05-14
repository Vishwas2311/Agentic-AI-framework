import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.name === "node_modules" || entry.name === ".next") return [];
    return entry.isDirectory() ? walk(path) : [path];
  });
}

test("generated app keeps data in typed demo files only", () => {
  const files = walk(root).map((file) => file.replaceAll("\\", "/"));
  assert.equal(files.some((file) => file.toLowerCase().includes("prisma")), false);
  assert.equal(files.some((file) => file.toLowerCase().includes("fastapi")), false);
});

test("OpenAI key is environment-only", () => {
  const source = walk(root)
    .filter((file) => /\.(ts|tsx|mjs|json|md|example)$/.test(file))
    .map((file) => readFileSync(file, "utf8"))
    .join("\n");
  assert.match(source, /process\.env\.OPENAI_API_KEY/);
  assert.doesNotMatch(source, /sk-[A-Za-z0-9]{20,}/);
});
