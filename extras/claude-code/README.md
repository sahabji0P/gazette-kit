# Claude Code extras

Optional. Copy these into your paper's folder so Claude Code picks up the instructions and skills, and scheduled runs don't stop at permission prompts.

```bash
cp extras/claude-code/CLAUDE.md ./CLAUDE.md          # imports AGENTS.md
mkdir -p .claude && cp extras/claude-code/settings.json .claude/settings.json
ln -s ../skills .claude/skills                        # skills become /gazette-* in Claude Code
```

Read `settings.json` before you copy it. It allows the kit's four scripts, web fetch and search, edits under `data/`, `notes/` and `hunts/`, and the few git commands a cloud run needs to save its state (`git add data notes hunts`, `git commit -m`, `git pull --rebase`, `git push`). Drop the git lines if your runs are local only. Tighten it further if you like.
