# Examples

Small, intentional fixtures — not real production apps.

| Example | Idea |
|---------|------|
| [mini-shop](mini-shop/) | Tiny HTTP shop: catalog → checkout → orders |
| [sample-story.json](sample-story.json) | Standalone story graph you can render |

## Render the sample story

From the repo root (with OKAD installed):

```bash
mkdir -p /tmp/okad-sample/okad-out
cp examples/sample-story.json /tmp/okad-sample/okad-out/story.json
# quick render via Python
python -c "
from pathlib import Path
from okad.merge import load_story
from okad.viz import render_html
g = load_story(Path('examples/sample-story.json'))
print(render_html(g, Path('/tmp/okad-sample-story.html')))
"
open /tmp/okad-sample-story.html
```

Or run the mini-shop through the real pipeline — see that folder’s README.
