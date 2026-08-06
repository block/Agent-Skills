#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

/**
 * CLI
 *  --repo-root path                Treat this directory as repo root (fork-safe validation)
 *
 * Note: the workflow also passes --skills and --report. Neither is implemented here:
 * validation always covers every skill dir under the repo root, and the report summary
 * is written by the workflow. Left as-is so this change does not narrow coverage.
 */
function parseArgs(argv) {
  const args = { repoRoot: null, sawRepoRoot: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--repo-root") {
      args.sawRepoRoot = true;
      args.repoRoot = (argv[++i] || "").trim();
    }
  }
  return args;
}

const { repoRoot: repoRootArg, sawRepoRoot } = parseArgs(process.argv.slice(2));

// An empty --repo-root must not silently fall back to cwd: in the fork job cwd is the
// *base* checkout, so we would validate the trusted tree and pass the untrusted one.
if (sawRepoRoot && !repoRootArg) {
  console.error("❌ --repo-root was passed without a value");
  process.exit(2);
}

// Repo root (fork-safe): a fork's tree is validated by pointing this trusted copy of the
// script at it, never by executing the copy of the script that lives inside that tree.
const REPO_ROOT = repoRootArg ? path.resolve(repoRootArg) : process.cwd();
const SKILLS_ROOT = REPO_ROOT;

const MAX_FILE_BYTES = 1_000_000;
const MAX_FILES_PER_SKILL = 400;

// Binary masquerading sampling (keep fast + predictable)
const TEXT_SAMPLE_MAX_BYTES = 64 * 1024;
const MIN_PRINTABLE_RATIO = 0.8;
// NOTE: validate-skills currently does FAIL-only reporting.
// We log encoding weirdness as a warning to stdout (does not fail).
const UTF8_REPLACEMENT_WARN_RATIO = 0.02;

const DENY_FILENAMES = new Set([
  ".env",
  ".env.local",
  ".env.production",
  ".env.development",
  ".npmrc",
  ".yarnrc",
  ".pypirc",
  "id_rsa",
  "id_ed25519",
  "known_hosts",
  "authorized_keys",
]);

const DENY_EXTENSIONS = new Set([
  ".exe",
  ".dll",
  ".dmg",
  ".pkg",
  ".msi",
  ".bin",
  ".so",
  ".class",
  ".jar",
  ".pyc",
  ".o",
  ".a",
  ".zip",
  ".tar",
  ".gz",
  ".7z",
]);

const ALLOW_EXTENSIONS = new Set([
  ".md",
  ".txt",
  ".json",
  ".yaml",
  ".yml",
  ".toml",
  ".graphql",
  ".css",
  ".html",
  ".js",
  ".mjs",
  ".cjs",
  ".ts",
  ".tsx",
  ".jsx",
  ".py",
  ".sh",
  ".bash",
  ".zsh",
  ".sql",
]);

const ALLOW_FILENAMES = new Set([
  "SKILL.md",
  "LICENSE",
  "NOTICE",
  "README",
  "README.md",
  "package.json",
  "package-lock.json",
  "pnpm-lock.yaml",
  "yarn.lock",
  ".gitignore",
]);

// Detect "binary pretending to be text" using magic bytes + text-likeness heuristics
const MAGIC = [
  { name: "ELF", bytes: [0x7f, 0x45, 0x4c, 0x46] },
  { name: "PE", bytes: [0x4d, 0x5a] }, // MZ
  { name: "ZIP", bytes: [0x50, 0x4b, 0x03, 0x04] },
  { name: "PDF", bytes: [0x25, 0x50, 0x44, 0x46] }, // %PDF
  { name: "PNG", bytes: [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a] },
  { name: "GZIP", bytes: [0x1f, 0x8b] },
  { name: "WASM", bytes: [0x00, 0x61, 0x73, 0x6d] }, // \0asm
];

function detectMagic(buf) {
  for (const m of MAGIC) {
    if (buf.length >= m.bytes.length && m.bytes.every((b, i) => buf[i] === b)) return m.name;
  }
  return null;
}

function analyzeTextlikeness(buf) {
  let nulFound = false;
  let printable = 0;

  for (let i = 0; i < buf.length; i++) {
    const c = buf[i];
    if (c === 0) nulFound = true;

    // printable ASCII + common whitespace
    const isPrintable =
      (c >= 0x20 && c <= 0x7e) || c === 0x09 || c === 0x0a || c === 0x0d;
    if (isPrintable) printable++;
  }

  const printableRatio = buf.length ? printable / buf.length : 1;

  // best-effort encoding sanity check
  const text = buf.toString("utf8");
  const repl = (text.match(/\uFFFD/g) || []).length;
  const replacementRatio = text.length ? repl / text.length : 0;

  return { nulFound, printableRatio, replacementRatio };
}

function readFileSample(absPath, sizeBytes) {
  const sampleSize = Math.min(TEXT_SAMPLE_MAX_BYTES, sizeBytes);
  if (sampleSize <= 0) return Buffer.alloc(0);

  const fd = fs.openSync(absPath, "r");
  try {
    const buf = Buffer.alloc(sampleSize);
    fs.readSync(fd, buf, 0, sampleSize, 0);
    return buf;
  } finally {
    fs.closeSync(fd);
  }
}

const IGNORE_DIRS_AT_ROOT = new Set([".git", ".github", "scripts", "node_modules"]);

let hadFailure = false;

function fail(msg) {
  hadFailure = true;
  console.error(`❌ ${msg}`);
}

function ok(msg) {
  console.log(`✅ ${msg}`);
}

function isSymlink(p) {
  return fs.lstatSync(p).isSymbolicLink();
}

function safeJoin(base, target) {
  const resolved = path.resolve(base, target);
  if (!resolved.startsWith(path.resolve(base) + path.sep)) {
    throw new Error(`Path traversal detected: ${target}`);
  }
  return resolved;
}

// --- frontmatter parsing ---
function parseFrontmatter(md) {
  const trimmed = md.replace(/^\uFEFF/, "");
  if (!trimmed.startsWith("---\n")) return null;
  const end = trimmed.indexOf("\n---\n", 4);
  if (end === -1) return null;

  const yamlText = trimmed.slice(4, end).trimEnd();
  const fm = {};
  let currentKey = null;

  for (const rawLine of yamlText.split("\n")) {
    const line = rawLine.replace(/\r$/, "");
    if (!line.trim()) continue;

    const listMatch = line.match(/^\s*-\s+(.*)\s*$/);
    if (listMatch && currentKey) {
      if (!Array.isArray(fm[currentKey])) fm[currentKey] = [];
      fm[currentKey].push(listMatch[1]);
      continue;
    }

    const kv = line.match(/^([A-Za-z0-9_-]+)\s*:\s*(.*)\s*$/);
    if (kv) {
      const key = kv[1];
      let value = kv[2];
      currentKey = key;

      if (value === "") {
        fm[key] = fm[key] ?? [];
        continue;
      }

      value = value.replace(/^"(.*)"$/, "$1").replace(/^'(.*)'$/, "$1");
      fm[key] = value;
      continue;
    }

    throw new Error(`Unsupported frontmatter line: "${line}"`);
  }

  return { frontmatter: fm };
}

function validateSkillFrontmatter(skillName, fm) {
  const required = ["name", "description", "author", "version"];
  for (const k of required) {
    const v = fm[k];
    if (typeof v !== "string" || !v.trim()) {
      fail(`${skillName}: frontmatter "${k}" must be a non-empty string`);
    }
  }

  const tags = fm.tags;
  if (
    !Array.isArray(tags) ||
    tags.length === 0 ||
    tags.some((t) => typeof t !== "string" || !t.trim())
  ) {
    fail(`${skillName}: frontmatter "tags" must be a non-empty list of strings`);
  }
}

function walkDir(dir, relativeBase) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = [];

  for (const ent of entries) {
    const rel = path.join(relativeBase, ent.name);
    const abs = safeJoin(REPO_ROOT, rel);

    if (ent.isDirectory()) {
      files.push(...walkDir(abs, rel));
    } else if (ent.isFile()) {
      files.push({ abs, rel });
    } else {
      // includes symlinks/specials
      try {
        if (isSymlink(abs)) fail(`${relativeBase}: symlink not allowed: ${rel}`);
        else fail(`${relativeBase}: unsupported file type: ${rel}`);
      } catch {
        fail(`${relativeBase}: unsupported/special file: ${rel}`);
      }
    }
  }

  return files;
}

function main() {
  if (!fs.existsSync(SKILLS_ROOT) || !fs.statSync(SKILLS_ROOT).isDirectory()) {
    fail(`Repo root is not a directory: ${SKILLS_ROOT}`);
    process.exit(1);
  }

  const rootEntries = fs.readdirSync(SKILLS_ROOT, { withFileTypes: true });

  const skillDirs = rootEntries
    .filter((e) => e.isDirectory() && !IGNORE_DIRS_AT_ROOT.has(e.name) && !e.name.startsWith("."))
    .map((e) => e.name);

  if (skillDirs.length === 0) {
    fail("No skill directories found at repo root.");
    process.exit(1);
  }

  ok(`Found ${skillDirs.length} skill directories.`);

  for (const skillName of skillDirs) {
    const skillPath = path.join(SKILLS_ROOT, skillName);
    const skillMd = path.join(skillPath, "SKILL.md");

    if (!fs.existsSync(skillMd)) {
      fail(`${skillName}: missing SKILL.md`);
      continue;
    }

    try {
      const parsed = parseFrontmatter(fs.readFileSync(skillMd, "utf8"));
      if (!parsed) fail(`${skillName}: SKILL.md must start with YAML frontmatter (---)`);
      else validateSkillFrontmatter(skillName, parsed.frontmatter);
    } catch (e) {
      fail(`${skillName}: invalid frontmatter: ${e?.message ?? String(e)}`);
    }

    const files = walkDir(skillPath, skillName);

    if (files.length > MAX_FILES_PER_SKILL) {
      fail(`${skillName}: too many files (${files.length}). Limit ${MAX_FILES_PER_SKILL}`);
    }

    for (const { abs, rel } of files) {
      // block symlinks (again, in case)
      try {
        if (isSymlink(abs)) {
          fail(`${skillName}: symlink not allowed: ${rel}`);
          continue;
        }
      } catch {
        fail(`${skillName}: could not stat file: ${rel}`);
        continue;
      }

      const base = path.basename(rel);
      const ext = path.extname(rel).toLowerCase();

      if (DENY_FILENAMES.has(base)) fail(`${skillName}: denylisted filename: ${rel}`);
      if (DENY_EXTENSIONS.has(ext)) fail(`${skillName}: denylisted extension "${ext}": ${rel}`);

      const isAllowedByName = ALLOW_FILENAMES.has(base);
      if (!isAllowedByName) {
        if (ext) {
          if (!ALLOW_EXTENSIONS.has(ext) && base !== "SKILL.md") {
            fail(`${skillName}: extension "${ext}" not allowed: ${rel}`);
          }
        } else {
          // no-extension files are risky; treat as fail to be strict
          fail(`${skillName}: file without extension not allowed: ${rel}`);
        }
      }

      const st = fs.statSync(abs);
      if (st.size > MAX_FILE_BYTES) fail(`${skillName}: file too large (${st.size} bytes): ${rel}`);

      // ---- Binary masquerading detection (FAIL fast) ----
      // If it's an allowed "text-ish" file, ensure it actually looks like text.
      const isTextAllowed =
        base === "SKILL.md" ||
        isAllowedByName ||
        (ext && ALLOW_EXTENSIONS.has(ext));

      if (isTextAllowed) {
        try {
          const buf = readFileSample(abs, st.size);
          if (buf.length > 0) {
            const magic = detectMagic(buf);
            if (magic) {
              fail(`${skillName}: binary masquerading detected (${magic}) in text file: ${rel}`);
            }

            const { nulFound, printableRatio, replacementRatio } = analyzeTextlikeness(buf);

            if (nulFound) {
              fail(`${skillName}: NUL byte found (binary content) in: ${rel}`);
            }

            if (printableRatio < MIN_PRINTABLE_RATIO) {
              fail(
                `${skillName}: low printable ratio (${printableRatio.toFixed(
                  2
                )}) in text file: ${rel}`
              );
            }

            // This is a "warn" signal, but validate-skills is fail-only.
            if (replacementRatio > UTF8_REPLACEMENT_WARN_RATIO) {
              console.warn(
                `⚠️ ${skillName}: suspicious encoding (UTF-8 replacement ratio ${(replacementRatio * 100).toFixed(
                  2
                )}%) in: ${rel}`
              );
            }
          }
        } catch (e) {
          fail(
            `${skillName}: could not sample file for binary masquerading checks: ${rel} (${
              e?.message ?? String(e)
            })`
          );
        }
      }
    }

    if (!hadFailure) ok(`${skillName}: structure validated`);
  }

  if (hadFailure) {
    console.error("\nStructure validation FAILED.");
    process.exit(1);
  }

  console.log("\nStructure validation PASSED.");
  process.exit(0);
}

main();
