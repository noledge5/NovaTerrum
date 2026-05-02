# Domain Docs

Single-context Repo. Vor dem Erkunden lesen:

- **`CONTEXT.md`** im Root — Domainsprache des Spiels
- **`docs/adr/`** im Root — Architekturentscheidungen

Falls diese Dateien noch nicht existieren, still weitermachen. `/grill-with-docs` legt sie lazy an wenn Begriffe oder Entscheidungen geklärt werden.

## Struktur

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
└── src/
```

## Hinweis: Migration zu Multi-context

Wenn das Projekt in klar getrennte Kontexte wächst (z.B. `engine/`, `story/`, `ui/`):
1. `CONTEXT-MAP.md` im Root anlegen
2. Pro Kontext ein eigenes `CONTEXT.md` + `docs/adr/`
3. Diese Datei aktualisieren
Die Skills erkennen `CONTEXT-MAP.md` automatisch.
