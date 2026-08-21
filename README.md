# Jiefu Zhang — Personal Website

This repository is organised by content type so it can grow without cluttering the project root.

```text
.
├── index.html                  # Main website entry point
├── assets/
│   ├── css/                    # Site-wide styles
│   └── documents/              # Public downloads, including the CV PDF
├── content/
│   └── cv/                     # Editable CV content
├── macro/
│   ├── EDITORIAL_CHECKLIST.md  # Publishing and quality-control standard
│   └── 2026/                   # Monthly Macro Views, grouped by year
└── tools/
    └── cv/
        ├── source/             # Source document used for CV export
        └── ...                 # CV generation and export scripts
```

## Adding a Macro View

1. Add the article to `macro/<year>/<month>.html`.
2. Add the issue to the homepage archive in reverse chronological order.
3. Follow `macro/EDITORIAL_CHECKLIST.md` before publication.

Keep `index.html` at the project root because GitHub Pages uses it as the site entry point.
