# Contributing

Thanks for helping. A few ground rules keep the kit easy to fork:

- **Standard library only.** The scripts must run on Python 3.9+ with nothing to install.
- **Scripts do mechanics, agents do judgement.** Fetching, layout, checks and bookkeeping go in `scripts/`. Editorial decisions go in `AGENTS.md`, `skills/` or `handbook/`.
- **Keep the docs and scripts in step.** If you change a field, command or status, update every place that names it (AGENTS.md, the skills, the handbook).
- **Add a test** in `tests/test_kit.py` for any bug you fix, then run:
  ```bash
  python3 -m unittest discover -s tests -v
  python3 scripts/build.py && python3 scripts/check.py
  python3 scripts/build.py --public && python3 scripts/check.py --public
  ```
- **If you change the theme or the sample data, rebuild the committed sample:** `python3 scripts/build.py --out examples/sample-edition`. CI checks that it matches a fresh build.
- **The sample stays fictional.** No real companies, people or numbers in `data/`.
- Commit messages: `area(scope): what changed`, lowercase, e.g. `scripts(check): fail on one-way related links`.

Reports from real runs are as useful as code: open an issue with what your agent did, where it got stuck, and the relevant `hunts/<run>/RESULT.md`. Remove anything private first.
