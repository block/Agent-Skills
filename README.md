# Agent Skills

A collection of reusable **Agent Skills** maintained by Block to help AI agents perform real-world tasks more effectively.

These skills are designed to be:
- ✅ Portable across agents (Goose, Claude Desktop, and others that support agent skills)
- ✅ Easy to install
- ✅ Easy to understand before installing
- ✅ Community-extensible

---

## What are Agent Skills?

Agent Skills are reusable sets of instructions and supporting resources that teach an AI agent how to perform a specific workflow or task.

A skill might include:
- A structured checklist (e.g. code review)
- A workflow (e.g. deploying a service)
- Domain knowledge (e.g. using a specific API)
- Supporting files like scripts, templates, or examples

Each skill lives in its own folder and includes a `SKILL.md` file.

---

## Installing a Skill

You can install skills using the `skills` CLI:

```bash
npx skills add https://github.com/block/Agent-Skills --skill api-setup
```
Make sure you have the built in skills extension enabled

This will install the skill locally so compatible agents (like Goose or Claude Desktop) can automatically load and use it.

## Browse Skills

You can browse all available skills via the Goose Skills Marketplace:
👉 https://goose-docs.ai/skills/

There you can:

- Read the full skill before installing

- Copy the install command

- View source on GitHub

## Contributing a Skill

We love community contributions and welcome new skills from anyone.

If you’ve built a useful workflow, checklist, or guide that could help other agents (and humans), you can submit it to this repository.

### How to contribute

1. Fork this repository
2. Create a new branch for your skill
3. Add your skill folder (with `SKILL.md` and any supporting files)
4. Commit your changes
5. [Open a pull request](https://github.com/block/agent-skills/compare)

#### Skill requirements (quick version)

Each skill must include a `SKILL.md` file with the following required frontmatter:

```md
---
name: api-setup
description: Set up API integration with configuration and helper scripts
author: goose
version: "1.0"
tags:
  - api
  - integration
  - setup
---
```

For detailed guidelines, formatting rules, and examples, see the [full contribution guide](https://github.com/block/Agent-Skills/blob/main/CONTRIBUTING.md)


Every submission is automatically validated using our skills validator, and feedback will appear directly on your PR.

### Not sure if your idea qualifies?

Good candidates for skills include:
- Repeatable workflows (deployments, releases, migrations)
- Checklists (code review, incident response, security audits)
- Domain knowledge (APIs, internal tools, infrastructure patterns)
- Templates or scripts paired with instructions

If you’re unsure, feel free to open a draft PR or start a discussion.
