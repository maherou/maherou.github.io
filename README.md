# maherou.github.io

Personal site for Michael A. Heroux. Plain Jekyll, no build tooling beyond Jekyll itself — edit
Markdown/HTML/CSS directly and push to `master`; GitHub Actions builds and deploys (see
`.github/workflows/pages.yml`).

## Structure

- `index.html` — homepage
- `bio.md`, `now.md`, `writing.md` — top-level pages (each sets its own `permalink`)
- `Projects/` — "Research & legacy projects" section; `_projects/*.md` are the individual
  project write-ups (Trilinos, HPCG, Mantevo, ECP, BSSw, E4S, RSS), rendered via the `projects`
  collection at `/Projects/<name>/`. `Projects/files/` holds the older docs/slides those pages
  link to.
- `files/` — CV and papers/presentations. `files/cv.md` is the canonical current CV page; older
  dated CV files are kept only because they're already linked/indexed — don't delete them, but
  don't add new ones there either, just update `files/cv.md` and the "current" PDF.
- `_layouts/`, `_includes/`, `assets/css/main.css` — site chrome and styling. One hand-written
  stylesheet, no Sass/build step.
- `2025HerouxFamilyAlbum.html` — shared privately by direct link only; not in the nav, not in
  `sitemap.xml` (excluded via the `defaults` entry in `_config.yml`, keyed to this exact path —
  deliberately kept as a plain static file with no front matter, so it's never run through
  Liquid), and marked `noindex`.

## Related sites on this domain

These are **separate repositories**, each with GitHub Pages enabled for its own path. They are
not part of this repo and are not built by this repo's workflow:

- [`maherou/Teaching`](https://github.com/maherou/Teaching) → `/Teaching/*` — the CS373/CS317
  course archive. Kept separate deliberately: it's a large (~400MB) archive of course materials
  (handbooks, schedules, sample papers, video), and folding it into this repo would bloat it for
  no benefit since it's no longer being actively taught.
- [`maherou/MJConnections`](https://github.com/maherou/MJConnections) → `/MJConnections/` —
  personal (wedding) site, unrelated to the professional content here. Shared privately by link;
  not linked from this site, and `noindex`/`robots.txt` were added there too.

If you ever need to fold `Teaching` in too, note that GitHub Pages ties a URL prefix to whichever
repo has Pages enabled for it — you'd need to disable Pages on the old repo once the new content
is live at the same path, not before.

## Local preview

```
bundle install
bundle exec jekyll serve
```
