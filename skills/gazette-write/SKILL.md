---
name: gazette-write
description: Step 2 of a gazette run. Turns a SHIP hunt (hunts/<run>/RESULT.md) into story records in data/stories.json and story bodies in data/bodies/, following the house story shape, headline rules, status labels, two-way related links, chains, glossary and corrections. Use after gazette-gather calls SHIP, or when asked to write, correct or explain a story.
---

# Write: from hunt to stories

You are the **editor**: the only role that edits `data/`. Rewrite in the paper's voice. Never paste source text. Quote sparingly.

## 1. One story record per news item

Append to `data/stories.json` → `stories`. Never delete or reorder existing ones.

```json
{
  "id": "short-kebab-slug",
  "headline": "Punch line first, plain words, makes sense on a phone",
  "dek": "Who, when · the two or three facts that frame it",
  "section": "<one key from beats.sections>",
  "threads": ["<0+ keys from beats.threads>"],
  "tags": ["<0+ from beats.tags>"],
  "status": "confirmed",
  "status_chip": "New",
  "strike": 8,
  "date": "YYYY-MM-DD",
  "fold_date": "YYYY-MM-DD",
  "what_happened": ["Line one: the fact.", "Line two: the second fact."],
  "why_it_matters": "One or two sentences for this owner.",
  "take": "Optional: the paper's opinion, one short paragraph.",
  "try": ["Optional: something to learn or try today."],
  "for_you": ["Optional, private: what this means for the owner's project."],
  "related": ["other-story-id"],
  "sources": [
    { "title": "Company — Post title (date)", "url": "https://…", "status": "CONFIRMED", "checked": "14:05 IST 2 Nov" }
  ]
}
```

Field rules:
- `section`: **exactly one**, chosen by what the story is *about*, not who found it.
- `status`: `lead` (only one, set during publish) · `confirmed` · `brief` (build ideas, small items) · `rumor` · `archive`.
- `status_chip` (optional, lead only): `New` · `Cheaper` · `Dangerous` · `Open weights`, or omit.
- `what_happened`: exactly **two** strings. `why_it_matters`: one or two sentences. A story without `what_happened` is headline-only: it gets no page and is listed on its section page.
- `fold_date`: when it entered the paper. If it differs from `date`, the kicker says "Catch-up".
- Every live story needs `sources`, each with a fact status.
- `for_you` is private: it shows only in the private build.

## 2. The body (`data/bodies/<id>.html`)

Plain HTML fragment, no `<html>` or `<head>`. The page template adds the headline, What happened, Why it matters, receipts and related links.
- Short paragraphs (≤ ~70 words). `<h2>` for sub-heads. Lists for steps and numbers.
- Optional `<p class="pull">` pull quote at the top. Optional `<details class="selftest"><summary>Q</summary><p>A</p></details>` for explainers.
- Code in `<pre><code>…</code></pre>`.
- Put the opinion in `take`, not as an extra heading.
- Wrap anything about the private project in `<!-- private -->…<!-- /private -->`.
- Use only classes that exist in `theme/styles.css`.

## 3. Headlines and voice

- **Punch line first.** What changed and why the owner should care, in plain words. Long is fine if every word earns its place.
- **No internal words** in headlines ("held", "demoted", "lead", strike numbers). Those live in the record.
- **No hype adjectives** without a mechanism ("revolutionary", "game-changing").
- **Labels stay visible**: "RUMOR:" in a rumor's headline, "vendor numbers" in the dek when nobody else checked.
- **Surface depth beats headline depth.** When a model or tool ships, cover the API, tools, limits and pricing, not just the price.
- Voice: dry, sharp, respectful of builders. Short sentences where they hit.
- **Click-worthy bar:** the story teaches a mechanism, tradeoff or decision, OR sparks a same-day prototype, OR changes a cost/architecture/watchlist choice. If it does none of these, it goes to `thin_ticks` instead.

## 4. Links between stories

- **Related is always two-way.** If A lists B, B must list A. `check.py` fails otherwise.
- Link every news story to the explainer or Build idea behind it, and back.
- **Chains** (`stories.json` → `chains`) are ordered series, e.g. a product's versions or "Learn from zero". Add new entries in order.
- **Glossary** (`data/glossary.json`): add a term when a story brings jargon. Entry: `{"id", "term", "definition", "aliases"?, "match"?, "source"?}`. The build links the first mention on each page. Specific terms win over general ones automatically (longest match first).

## 5. Thin ticks, tape, watchlist

- `thin_ticks`: `{ "tag": "<section short>", "text": "One line with its STATUS." }`. Add `"private": true` for project-only lines.
- `tape`: model or product → price or version, **only when it moved**.
- `watchlist`: `{ "id", "label", "note": "Watch: …" }`. These are the questions for the next hunt.

## 6. Explainers (Learn)

Plain language, built from zero: the one-line idea → how it works → what it doesn't do → a self-test. Ids start `learn-`. Add to the "Learn from zero" chain. The reporter fact-checks every product or number claim before publishing.

## 7. Corrections

When a fact was wrong:
1. Fix the record and the body. Add `"corrections": [{"date": "31 Oct", "text": "An earlier version said X. The source says Y."}]`. It renders at the top of the story.
2. Fix the headline in the record. Every page that links to it updates on the next build.
3. Add the wrong wording to `data/corrections.json` → `do_not_reintroduce`: `{ "wrong", "right", "story", "date" }`. From then on `check.py` fails if it reappears anywhere.
4. Note it in `notes/MEMORY.md`.

## 8. Project ideas

If a story sparks an idea for the owner's project, follow `skills/gazette-build-for-project`.

Then continue with `skills/gazette-publish`.
