window.GAZETTE_CATALOG = {
  "paper": "THE SAMPLE GAZETTE",
  "edition_label": "Vol. 1, No. 3",
  "edition": {
    "number": 3,
    "published": "2026-11-02T14:10:00+05:30",
    "slot": "afternoon"
  },
  "folio": "Monday · 2 November 2026 · afternoon",
  "lead": "northwind-kestrel-3",
  "flash": "Mon afternoon: Northwind's Kestrel 3 lands at a fifth of last generation's price, with a 400K context and a Mini that runs on a laptop. Also: Tessellate's agent CLI now sandboxes every plugin by default.",
  "taxonomy": [
    "Models",
    "Tools",
    "Build",
    "Startups",
    "Learn",
    "Hardware",
    "People",
    "Voice",
    "Memory",
    "Safety",
    "Pricing",
    "Open weights",
    "Agents"
  ],
  "sections": [
    {
      "key": "models",
      "label": "Models & Pricing",
      "short": "Models",
      "blurb": "Model launches, price lists, context windows, benchmarks.",
      "page": "stories/section-models.html"
    },
    {
      "key": "tools",
      "label": "Tools & Harnesses",
      "short": "Tools",
      "blurb": "Coding agents, harness releases, APIs, sandboxes and agent incidents.",
      "page": "stories/section-tools.html"
    },
    {
      "key": "build",
      "label": "Build",
      "short": "Build",
      "blurb": "Ideas to try — suggestions, not news.",
      "page": "stories/section-build.html"
    },
    {
      "key": "startups",
      "label": "Builders & Startups",
      "short": "Startups",
      "blurb": "Agent products, funding rounds, builder launches.",
      "page": "stories/section-startups.html"
    },
    {
      "key": "learn",
      "label": "Learn",
      "short": "Learn",
      "blurb": "Explainers, papers and safety reports — the why behind the news.",
      "page": "stories/section-learn.html"
    },
    {
      "key": "hardware",
      "label": "Hardware & Deals",
      "short": "Hardware",
      "blurb": "Chips, compute, acquisitions, big deals and policy.",
      "page": "stories/section-hardware.html"
    },
    {
      "key": "people",
      "label": "People",
      "short": "People",
      "blurb": "Moves and culture.",
      "front": "strip",
      "page": "stories/section-people.html"
    }
  ],
  "threads": [
    {
      "key": "voice",
      "label": "Voice agents",
      "chip": "Voice",
      "blurb": "Speech in, speech out, and talking over the agent.",
      "page": "stories/thread-voice.html"
    },
    {
      "key": "memory",
      "label": "Memory",
      "chip": "Memory",
      "blurb": "What agents remember, and how.",
      "page": "stories/thread-memory.html"
    },
    {
      "key": "safety",
      "label": "Harness safety & sandbox",
      "chip": "Safety",
      "blurb": "Permissions, sandboxes, incidents.",
      "page": "stories/thread-safety.html"
    },
    {
      "key": "pricing",
      "label": "Pricing",
      "chip": "Pricing",
      "blurb": "What it costs to run.",
      "page": "stories/thread-pricing.html"
    }
  ],
  "glossary": "stories/glossary.html",
  "stories": [
    {
      "id": "northwind-kestrel-3",
      "headline": "Northwind’s Kestrel 3 costs a fifth of Kestrel 2, reads 400K tokens at once — and its Mini version runs on a laptop",
      "dek": "Northwind Labs, Mon 2 Nov · two models, one API · price cut, longer context, a small model with open weights",
      "section": "models",
      "section_label": "Models & Pricing",
      "categories": [
        "Models",
        "Pricing",
        "Agents",
        "Open weights"
      ],
      "threads": [
        "pricing"
      ],
      "tags": [
        "Agents",
        "Open weights"
      ],
      "status": "lead",
      "status_chip": "Cheaper",
      "strike": 8,
      "front": true,
      "date": "2026-11-02",
      "what_happened": [
        "Northwind Labs released Kestrel 3 at $3 in / $15 out per million tokens, down from $15/$75 for Kestrel 2, with a 400K-token context window.",
        "Kestrel 3 Mini ships with open weights under a permissive licence and runs on a 32 GB laptop, Northwind says."
      ],
      "why_it_matters": "A fivefold price cut changes which jobs are worth handing to a big model; the open Mini makes a cheap local first pass realistic.",
      "related": [
        "northwind-kestrel-2",
        "learn-context-windows",
        "build-cheap-draft-strong-check",
        "build-pocketful-kestrel-mini-router",
        "halyard-h2-chip"
      ],
      "sources": [
        {
          "title": "Northwind Labs — Introducing Kestrel 3 (2 Nov)",
          "url": "https://example.com/northwind/kestrel-3",
          "status": "CONFIRMED",
          "checked": "14:02 IST 2 Nov"
        },
        {
          "title": "Northwind API pricing page",
          "url": "https://example.com/northwind/pricing",
          "status": "CONFIRMED",
          "checked": "14:03 IST 2 Nov"
        },
        {
          "title": "Kestrel 3 Mini model card",
          "url": "https://example.org/models/northwind/kestrel-3-mini",
          "status": "VENDOR-REPORTED",
          "checked": "14:05 IST 2 Nov"
        }
      ],
      "body_path": "stories/northwind-kestrel-3.html"
    },
    {
      "id": "northwind-kestrel-2",
      "headline": "Kestrel 2 arrives with a 128K context and Northwind’s first agent mode",
      "dek": "Northwind Labs · the previous generation",
      "section": "models",
      "section_label": "Models & Pricing",
      "categories": [
        "Models",
        "Agents"
      ],
      "threads": [],
      "tags": [
        "Agents"
      ],
      "status": "archive",
      "strike": 7,
      "date": "2026-10-31",
      "what_happened": [
        "Northwind released Kestrel 2 with a 128K-token context and an agent mode that can call tools in a loop.",
        "It cost $15 in / $75 out per million tokens."
      ],
      "why_it_matters": "It set the price that Kestrel 3 just cut by five.",
      "related": [
        "northwind-kestrel-3"
      ],
      "sources": [
        {
          "title": "Northwind Labs — Kestrel 2 (31 Oct)",
          "url": "https://example.com/northwind/kestrel-2",
          "status": "CONFIRMED",
          "checked": "09:10 IST 31 Oct"
        }
      ],
      "body_path": "stories/northwind-kestrel-2.html",
      "cooled_in": 3
    },
    {
      "id": "rumor-kestrel-4",
      "headline": "RUMOR: a forum post says Northwind is already training Kestrel 4",
      "dek": "One anonymous post · no primary source",
      "section": "models",
      "section_label": "Models & Pricing",
      "categories": [
        "Models"
      ],
      "threads": [],
      "tags": [],
      "status": "rumor",
      "strike": 5,
      "date": "2026-11-02",
      "related": [],
      "sources": [
        {
          "title": "Forum thread (anonymous)",
          "url": "https://example.net/forum/kestrel-4",
          "status": "RUMOR",
          "checked": "13:50 IST 2 Nov"
        }
      ],
      "body_path": null
    },
    {
      "id": "tessellate-tess-cli-2",
      "headline": "Tessellate’s coding agent now runs every plugin in its own sandbox — no network, no home folder, unless you allow it",
      "dek": "Tess CLI 2.0 · plugins isolated by default · a per-plugin allowlist",
      "section": "tools",
      "section_label": "Tools & Harnesses",
      "categories": [
        "Tools",
        "Safety",
        "Agents"
      ],
      "threads": [
        "safety"
      ],
      "tags": [
        "Agents"
      ],
      "status": "confirmed",
      "strike": 8,
      "date": "2026-11-02",
      "what_happened": [
        "Tess CLI 2.0 runs each plugin in a separate sandbox with no network and no access to your home folder by default.",
        "Owners grant access per plugin in a small allowlist file that lives next to the project."
      ],
      "why_it_matters": "After last week's plugin incident, default-deny is the right shape: a bad plugin can only touch what you listed.",
      "related": [
        "tessellate-plugin-incident",
        "build-cheap-draft-strong-check"
      ],
      "sources": [
        {
          "title": "Tess CLI 2.0 release notes",
          "url": "https://example.com/tessellate/releases/2.0.0",
          "status": "CONFIRMED",
          "checked": "13:40 IST 2 Nov"
        },
        {
          "title": "Tessellate docs — plugin permissions",
          "url": "https://example.com/tessellate/docs/permissions",
          "status": "CONFIRMED",
          "checked": "13:42 IST 2 Nov"
        }
      ],
      "body_path": "stories/tessellate-tess-cli-2.html"
    },
    {
      "id": "tessellate-plugin-incident",
      "headline": "A tampered Tess plugin copied API keys from about 4,000 machines before it was pulled",
      "dek": "Tessellate incident report · 11 hours live · rotate keys if you installed “tess-fmt-plus”",
      "section": "tools",
      "section_label": "Tools & Harnesses",
      "categories": [
        "Tools",
        "Safety",
        "Agents"
      ],
      "threads": [
        "safety"
      ],
      "tags": [
        "Agents"
      ],
      "status": "confirmed",
      "strike": 7,
      "date": "2026-10-30",
      "what_happened": [
        "A tampered copy of the community plugin “tess-fmt-plus” was live for about 11 hours and read API keys from environment variables.",
        "Tessellate says about 4,000 installs pulled it; it has been removed and keys should be rotated."
      ],
      "why_it_matters": "Agent plugins run with your agent's permissions, so one bad plugin reaches every secret the agent can see.",
      "related": [
        "tessellate-tess-cli-2"
      ],
      "sources": [
        {
          "title": "Tessellate — incident report (30 Oct)",
          "url": "https://example.com/tessellate/incident-2026-10-30",
          "status": "CONFIRMED",
          "checked": "19:05 IST 30 Oct"
        }
      ],
      "body_path": "stories/tessellate-plugin-incident.html"
    },
    {
      "id": "tess-cli-1-9",
      "headline": "Tess CLI 1.9 adds session resume",
      "dek": "Point release",
      "section": "tools",
      "section_label": "Tools & Harnesses",
      "categories": [
        "Tools"
      ],
      "threads": [],
      "tags": [],
      "status": "archive",
      "strike": 6,
      "date": "2026-10-29",
      "related": [],
      "sources": [
        {
          "title": "Tess CLI 1.9 changelog",
          "url": "https://example.com/tessellate/releases/1.9.0",
          "status": "CONFIRMED",
          "checked": "09:20 IST 30 Oct"
        }
      ],
      "body_path": null,
      "cooled_in": 2
    },
    {
      "id": "lumen-voice-barge",
      "headline": "Lumen Voice lets you interrupt its phone agent mid-sentence — and it stops talking in under 200 ms",
      "dek": "Lumen Voice, seed-stage startup · full-duplex calls · the number is the company's own",
      "section": "startups",
      "section_label": "Builders & Startups",
      "categories": [
        "Startups",
        "Voice",
        "Agents"
      ],
      "threads": [
        "voice"
      ],
      "tags": [
        "Agents"
      ],
      "status": "confirmed",
      "strike": 7,
      "date": "2026-11-01",
      "fold_date": "2026-11-02",
      "what_happened": [
        "Lumen Voice launched a phone agent that keeps listening while it speaks and stops when the caller talks over it.",
        "It says the agent stops in under 200 ms on average; no outside test yet."
      ],
      "why_it_matters": "How fast an agent yields when you interrupt is what makes a voice agent feel like a person or like a menu.",
      "related": [
        "learn-barge-in",
        "build-pocketful-voice-interrupt"
      ],
      "sources": [
        {
          "title": "Lumen Voice launch post",
          "url": "https://example.com/lumen/launch",
          "status": "VENDOR-REPORTED",
          "checked": "13:30 IST 2 Nov"
        }
      ],
      "body_path": "stories/lumen-voice-barge.html"
    },
    {
      "id": "brightline-memory-seed",
      "headline": "Brightline raises a $6M seed to give agents memory that users can read and delete",
      "dek": "Brightline · memory as an editable file · seed round",
      "section": "startups",
      "section_label": "Builders & Startups",
      "categories": [
        "Startups",
        "Memory",
        "Agents"
      ],
      "threads": [
        "memory"
      ],
      "tags": [
        "Agents"
      ],
      "status": "confirmed",
      "strike": 7,
      "date": "2026-11-02",
      "what_happened": [
        "Brightline raised a $6M seed round for a memory layer that stores what an agent remembers as plain entries a user can open, edit and delete.",
        "It ships as an API and a small open-source client."
      ],
      "why_it_matters": "Memory that users can see is easier to trust and easier to get right than memory hidden inside embeddings.",
      "related": [
        "build-pocketful-memory-consent",
        "learn-context-windows"
      ],
      "sources": [
        {
          "title": "Brightline — seed announcement",
          "url": "https://example.com/brightline/seed",
          "status": "CONFIRMED",
          "checked": "13:55 IST 2 Nov"
        }
      ],
      "body_path": "stories/brightline-memory-seed.html"
    },
    {
      "id": "halyard-h2-chip",
      "headline": "Halyard’s H2 inference chip claims three times the tokens per watt of its first chip",
      "dek": "Halyard Compute · vendor numbers · sampling in December",
      "section": "hardware",
      "section_label": "Hardware & Deals",
      "categories": [
        "Hardware",
        "Pricing"
      ],
      "threads": [
        "pricing"
      ],
      "tags": [],
      "status": "confirmed",
      "strike": 7,
      "date": "2026-11-02",
      "what_happened": [
        "Halyard Compute announced the H2, an inference chip it says delivers three times the tokens per watt of the H1.",
        "Sampling starts in December; Halyard named no customers."
      ],
      "why_it_matters": "Cheaper inference per watt is what eventually shows up as lower prices like Kestrel 3's.",
      "related": [
        "northwind-kestrel-3"
      ],
      "sources": [
        {
          "title": "Halyard Compute — H2 announcement",
          "url": "https://example.com/halyard/h2",
          "status": "VENDOR-REPORTED",
          "checked": "13:58 IST 2 Nov"
        }
      ],
      "body_path": "stories/halyard-h2-chip.html"
    },
    {
      "id": "learn-context-windows",
      "headline": "Context windows, explained from zero: what “400K tokens” buys you, and what it doesn’t",
      "dek": "Learn explainer · tokens · context window · why long context is not memory",
      "section": "learn",
      "section_label": "Learn",
      "categories": [
        "Learn",
        "Memory"
      ],
      "threads": [
        "memory"
      ],
      "tags": [],
      "status": "confirmed",
      "strike": 7,
      "date": "2026-11-02",
      "what_happened": [
        "A context window is how much text a model can read in one go; Kestrel 3's is 400K tokens, roughly a long novel.",
        "Reading more is not remembering: when the conversation ends, the window is empty again."
      ],
      "why_it_matters": "Bigger windows make some tasks simpler, but they cost more per call and do not replace a memory you control.",
      "related": [
        "northwind-kestrel-3",
        "brightline-memory-seed"
      ],
      "sources": [
        {
          "title": "Northwind docs — context and tokens",
          "url": "https://example.com/northwind/docs/context",
          "status": "CONFIRMED",
          "checked": "14:00 IST 2 Nov"
        }
      ],
      "body_path": "stories/learn-context-windows.html"
    },
    {
      "id": "learn-barge-in",
      "headline": "Barge-in, explained from zero: what has to happen when you talk over a voice agent",
      "dek": "Learn explainer · barge-in · stop speaking, stop thinking, start listening",
      "section": "learn",
      "section_label": "Learn",
      "categories": [
        "Learn",
        "Voice"
      ],
      "threads": [
        "voice"
      ],
      "tags": [],
      "status": "confirmed",
      "strike": 7,
      "date": "2026-11-01",
      "what_happened": [
        "Barge-in is when a caller talks while the agent is speaking, and the agent stops to listen.",
        "Done well, three things stop at once: the audio, the text being generated, and any action not yet taken."
      ],
      "why_it_matters": "Stopping the audio but not the action is how a voice agent ends up booking the thing you just said no to.",
      "related": [
        "lumen-voice-barge"
      ],
      "sources": [
        {
          "title": "Lumen Voice docs — interruptions",
          "url": "https://example.com/lumen/docs/interruptions",
          "status": "VENDOR-REPORTED",
          "checked": "09:15 IST 1 Nov"
        }
      ],
      "body_path": "stories/learn-barge-in.html"
    },
    {
      "id": "build-cheap-draft-strong-check",
      "headline": "Build: draft with a small local model, check with a big one — and only pay the big one when the draft fails",
      "dek": "Suggestion · two-model pattern · cost per correct answer",
      "section": "build",
      "section_label": "Build",
      "categories": [
        "Build",
        "Pricing",
        "Agents"
      ],
      "threads": [
        "pricing"
      ],
      "tags": [
        "Agents"
      ],
      "status": "brief",
      "strike": 7,
      "date": "2026-11-02",
      "what_happened": [
        "Suggestion: run a small open model first, then send only its uncertain or failed answers to a large model.",
        "Measure cost per correct answer across 50 real inputs before and after."
      ],
      "why_it_matters": "With a cheap Mini and a cheaper flagship, the two-model setup can halve cost without losing accuracy — or not; measure it.",
      "related": [
        "northwind-kestrel-3",
        "tessellate-tess-cli-2"
      ],
      "sources": [
        {
          "title": "Kestrel 3 Mini model card",
          "url": "https://example.org/models/northwind/kestrel-3-mini",
          "status": "VENDOR-REPORTED",
          "checked": "14:05 IST 2 Nov"
        }
      ],
      "body_path": "stories/build-cheap-draft-strong-check.html"
    },
    {
      "id": "build-pocketful-kestrel-mini-router",
      "headline": "Build: let Kestrel 3 Mini sort Pocketful’s transactions on-device, and call the cloud only for the ones it can’t place",
      "dek": "Suggestion for Pocketful · private",
      "section": "build",
      "section_label": "Build",
      "categories": [
        "Build",
        "Pricing"
      ],
      "threads": [
        "pricing"
      ],
      "tags": [],
      "status": "brief",
      "strike": 8,
      "date": "2026-11-02",
      "what_happened": [
        "Suggestion: run Kestrel 3 Mini on-device to categorise Pocketful transactions, with a confidence cut-off.",
        "Below the cut-off, send the transaction to the hosted model; log both answers for a week."
      ],
      "why_it_matters": "Most student spending is the same ten merchants; paying a cloud model to categorise coffee is waste.",
      "related": [
        "northwind-kestrel-3"
      ],
      "sources": [
        {
          "title": "Kestrel 3 Mini model card",
          "url": "https://example.org/models/northwind/kestrel-3-mini",
          "status": "VENDOR-REPORTED",
          "checked": "14:05 IST 2 Nov"
        }
      ],
      "body_path": "stories/build-pocketful-kestrel-mini-router.html"
    },
    {
      "id": "build-pocketful-voice-interrupt",
      "headline": "Build: make Pocketful’s “can I afford this?” voice answer stop the moment the student speaks",
      "dek": "Suggestion for Pocketful · private",
      "section": "build",
      "section_label": "Build",
      "categories": [
        "Build",
        "Voice"
      ],
      "threads": [
        "voice"
      ],
      "tags": [],
      "status": "brief",
      "strike": 7,
      "date": "2026-11-01",
      "what_happened": [
        "Suggestion: when the student talks over the answer, stop the audio and cancel the pending reply in the same step.",
        "Test with five recorded interruptions and time how long the app keeps talking."
      ],
      "why_it_matters": "A budgeting assistant that talks over you feels like a lecture; one that yields feels like help.",
      "related": [
        "lumen-voice-barge"
      ],
      "sources": [
        {
          "title": "Lumen Voice docs — interruptions",
          "url": "https://example.com/lumen/docs/interruptions",
          "status": "VENDOR-REPORTED",
          "checked": "09:15 IST 1 Nov"
        }
      ],
      "body_path": "stories/build-pocketful-voice-interrupt.html"
    },
    {
      "id": "build-pocketful-memory-consent",
      "headline": "Build: show Pocketful users every fact the app remembers about them, with a delete button on each",
      "dek": "Suggestion for Pocketful · private",
      "section": "build",
      "section_label": "Build",
      "categories": [
        "Build",
        "Memory",
        "Safety"
      ],
      "threads": [
        "memory",
        "safety"
      ],
      "tags": [],
      "status": "brief",
      "strike": 7,
      "date": "2026-11-02",
      "what_happened": [
        "Suggestion: store what Pocketful learns (rent day, usual budget, savings goal) as plain entries on a “What I remember” screen.",
        "Each entry gets a source line and a delete button."
      ],
      "why_it_matters": "Money data is sensitive; visible, deletable memory is easier to trust and to explain.",
      "related": [
        "brightline-memory-seed"
      ],
      "sources": [
        {
          "title": "Brightline — seed announcement",
          "url": "https://example.com/brightline/seed",
          "status": "CONFIRMED",
          "checked": "13:55 IST 2 Nov"
        }
      ],
      "body_path": "stories/build-pocketful-memory-consent.html"
    },
    {
      "id": "people-mira-okafor-joins-tessellate",
      "headline": "Mira Okafor, who built Northwind’s agent mode, joins Tessellate to lead plugin security",
      "dek": "People · move",
      "section": "people",
      "section_label": "People",
      "categories": [
        "People",
        "Safety"
      ],
      "threads": [
        "safety"
      ],
      "tags": [],
      "status": "confirmed",
      "strike": 6,
      "date": "2026-11-02",
      "what_happened": [
        "Mira Okafor, who led agent mode at Northwind Labs, has joined Tessellate to run plugin security.",
        "She announced the move in a public post on Monday."
      ],
      "why_it_matters": "Tessellate is hiring for the problem its plugin incident exposed.",
      "related": [],
      "sources": [
        {
          "title": "Mira Okafor — public post",
          "url": "https://example.com/people/mira-okafor/post",
          "status": "CONFIRMED",
          "checked": "13:45 IST 2 Nov"
        }
      ],
      "body_path": "stories/people-mira-okafor-joins-tessellate.html"
    }
  ]
};
