import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

const validatorPath = fileURLToPath(new URL("./validate-skills.mjs", import.meta.url));

function runValidator(files) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "agent-skills-validator-"));
  const skillDir = path.join(root, "unicode-skill");
  fs.mkdirSync(skillDir);

  for (const [relativePath, content] of Object.entries(files)) {
    const target = path.join(skillDir, relativePath);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, content);
  }

  try {
    return spawnSync(process.execPath, [validatorPath], {
      cwd: root,
      encoding: "utf8",
    });
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

const validFrontmatter = `---
name: unicode-skill
description: Validates multilingual skill content
author: test
version: "1.0"
tags:
  - unicode
---
`;

test("accepts valid UTF-8 text containing CJK and emoji", () => {
  const result = runValidator({
    "SKILL.md": `${validFrontmatter}\n# 多语言技能\n\n这是可打印的中文内容。事实核验完成。`,
    "references/guide.md": "核验来源、适用范围和发布日期。✅\n".repeat(20),
  });

  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
});

test("continues to reject binary control bytes in text files", () => {
  const result = runValidator({
    "SKILL.md": `${validFrontmatter}\n# Binary fixture`,
    "references/bad.txt": Buffer.from([0x41, 0x00, 0x42]),
  });

  assert.notEqual(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.match(result.stderr, /NUL byte found/);
});
