---
name: gazette-build-for-project
description: Turns news in the current edition into concrete, labelled same-day suggestions for the owner's own project (gazette.config.json → project). Writes private build-<project>-* stories that never appear in a public build. Use during gazette-write when a story could change what the owner builds, or when the owner asks "what should I try for <project>?".
---

# Build for the owner's project

Read `gazette.config.json` → `project`. If `enabled` is false, skip this skill. The `about` field is all you know about the project. Don't assume features it doesn't mention. If an idea depends on something you don't know, say what you'd need to know.

## When to write one

Only when a story in this edition gives the project a **concrete, testable** move, for example:
- a price or model change that makes a cheaper or better setup possible
- a technique (explainer, paper, incident) the project can apply or should guard against
- a tool release that removes work the project is doing by hand

Aim for 0–2 per edition. Don't force one into every run. A missing idea is better than a vague one.

## The record

Same shape as any story (`skills/gazette-write`), plus:
- `id`: starts with `project.id_prefix` (e.g. `build-pocketful-…`). The prefix is what makes it private.
- `section`: `"build"` · `status`: `"brief"` · strike: same scale. Ideas still have to earn 7+ to lead the Build section.
- `headline`: starts with **"Build:"** and names the move, e.g. "Build: let the small model sort transactions on-device, and call the cloud only for the ones it can't place".
- `dek`: "Suggestion for <project> · private".
- `what_happened`: line 1 is **"Suggestion: …"**, the change. Line 2 is **how to test it** in a day: inputs, what to measure, the pass bar.
- `why_it_matters`: why it matters for *this* project's users or costs.
- `related`: the news story that sparked it, two-way. Add the idea's id to that story's `related` too.
- `sources`: the same primary sources as the news story.

Optional body (`data/bodies/<id>.html`): steps, a small code sketch, risks, and what would make you drop the idea.

## Privacy rules

- Project ideas are **suggestions**, never news. Say so.
- Inside *public* stories, anything about the project goes in `for_you` (record) or between `<!-- private -->` and `<!-- /private -->` (body). Never in `headline`, `dek`, `what_happened`, `why_it_matters` or `take`.
- Wire or ticker lines about the project get `"private": true`.
- **Any project detail in a public field is a leak, even without the project's name.** The public check can only find the marker words in `project.private_markers`; it can't recognise a paraphrase ("the student budgeting app"). Keeping project details out of public fields is your job, not the script's.
- Before anything leaves the machine, `python3 scripts/build.py --public && python3 scripts/check.py --public` must pass with 0 private markers.

## General build ideas

Ideas that aren't tied to the project (useful to any reader) use a normal id like `build-<slug>`, without the project prefix. They stay public, in the same Build section.
