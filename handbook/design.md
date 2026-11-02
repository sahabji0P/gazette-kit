# Design

The default look is **newsprint**: cream paper (`--newsprint`), ink, a scarlet rule, Playfair Display headlines and Newsreader body text. It's built to be read, not to look like a SaaS dashboard. It opens from `file://` with no server, and all links are relative.

## Pages (what `scripts/build.py` makes)
| Page | What |
|---|---|
| `index.html` | Front: masthead → nav → flash → tape → **one lead** (what happened / why it matters) → section blocks (top N each by strike) → strip sections → threads → one-line ticker of everything else |
| `reader.html?id=<id>` | Split reader: story list on one side, the story page (`?embed=1`) on the other. Close returns to the front |
| `stories/<id>.html` | Story page (template `theme/templates/story.html`) |
| `stories/section-<key>.html` | Every story in a section: live, then archived |
| `stories/thread-<key>.html` | Every story on a thread |
| `stories/glossary.html` | Terms; story pages link the first mention |
| `wire.html` | Thin ticks, rumors, watchlist, and every edition's log |
| `build.html` | The idea engine: Build section suggestions |
| `archive.html` | Cooled stories, newest cooled first |
| `saved.html` | The reader's Saved shelf (browser storage) |

## Restyling
- **Colours, fonts, spacing:** `theme/styles.css`. The `:root` variables at the top change most of the look. Fonts load from `theme.fonts_url` in the config. Set it to `""` for system fonts and fully offline pages.
- **Page structure:** `theme/templates/*.html` use `{{placeholders}}` that `build.py` fills. Keep every placeholder. `check.py` fails on any left unfilled.
- **Repeated blocks** (cards, lists) are built in `scripts/build.py`. Each page has its own method (`front`, `story_page`, `wire_page`, …).
- **Class contract:** use the classes that exist in `styles.css`. A new class with no CSS renders unstyled.

## Readability targets
Body ~18px serif, line height ~1.6, column ~68ch, strong contrast. `pre` blocks are dark with light monospace and scroll sideways. There's a print stylesheet. On phones, the layout stacks.

## Private vs public
The private build (`out/`) shows project stories and the dashed **For you · private** boxes. The public build (`out-public/`) drops them at build time. `check.py --public` then scans for any leftover private marker.
