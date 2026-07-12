---
name: alibaba-java-coding-guidelines-skill
description: Apply Alibaba Java Coding Guidelines when reviewing, generating, or refactoring Java, Spring, MyBatis, Maven, MySQL, SQL, logging, exception handling, and security-related code.
author: ns3154
version: "1.0"
tags:
  - java
  - coding-guidelines
  - code-review
  - spring
  - mybatis
  - mysql
  - security
---

# Alibaba Java Coding Guidelines

## Purpose

Use this skill as a quality baseline for Java code generation, refactoring, and review based on Alibaba Java Coding Guidelines. Treat mandatory rules as defects, recommended rules as default guidance, and reference rules as design advice.

The detailed summary is in `references/alibaba-java-rules.md`. For exact source text, use the official Alibaba Java Coding Guidelines page.

## When To Use

- Reviewing Java, Spring, MyBatis, Maven, SQL, DDL, logging, exception handling, or security-related changes.
- Generating classes, interfaces, DTOs, VOs, DOs, enums, exceptions, tests, mappers, services, DAOs, or SQL.
- Refactoring naming, constants, collections, concurrency, control flow, logging, exceptions, and database access.
- Producing code review findings, remediation checklists, guideline compliance reports, or targeted fixes.

## Workflow

1. Identify the task type: code generation, code review, refactoring, SQL or DDL review, dependency governance, or security review.
2. Inspect the existing project style, packages, testing framework, persistence patterns, and local conventions.
3. Prioritize findings:
   - Mandatory: report or fix violations.
   - Recommended: follow by default; explain tradeoffs if skipped.
   - Reference: use as design guidance.
4. Read only the relevant section of `references/alibaba-java-rules.md`.
5. Report issues in impact order: correctness and security, stability and performance, maintainability, then style consistency.

## Generation Defaults

- Use clear names: UpperCamelCase for classes, lowerCamelCase for methods and variables, and upper snake case for constants.
- Avoid magic values; use constants or enums for fixed sets.
- Use SLF4J-style logging. Avoid string concatenation in debug or trace logs.
- Prefer try-with-resources for closeable resources.
- Never return or throw a new exception from `finally`.
- Use MyBatis `#{}` parameters by default. Do not concatenate user input into SQL.
- Validate, authorize, escape, or desensitize user input and output in web, API, SQL, and HTML contexts.

## Review Output

When reviewing code, make each finding actionable:

- Level: mandatory, recommended, or reference.
- Location: file and line when available.
- Problem: the violated guideline category.
- Risk: correctness, security, performance, or maintenance impact.
- Fix: a concrete recommendation.

If no issues are found, state the checked scope and any remaining blind spots, such as tests not run, missing index information, or unavailable production logging configuration.

## Common Mistakes

- Do not only review formatting. Naming, null handling, exception boundaries, log context, transactions, SQL injection, and authorization also matter.
- Do not label recommended rules as mandatory defects.
- Do not replace project conventions without explaining the conflict.
- Do not depend on a specific agent runner, local path, or product-specific config.
