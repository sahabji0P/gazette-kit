# Saves

- Every story has **Save**: on front cards, story pages and in the reader. Saves live only in the reader's browser (`localStorage`, key `<paper.slug>.saved.v1`). Nothing leaves the machine.
- `saved.html` lists them, with category filters. Unsaving only removes the story from the shelf.
- **Agent saves:** when the owner says "save X for me", add the story id to `gazette.config.json` → `saves.agent_saved`. Each id is seeded into the shelf once (`<slug>.agentSeeded.v1`), so if the owner later unsaves it, it stays unsaved.
- Saves are per browser. Clearing site data clears them. Moving them between machines is not built in.
