# NovaTerrum

Grimdark Solo-RPG mit Claude als Dungeon Master. FastAPI-Backend + mobil-optimiertes HTML/JS-Frontend. Kein Build-Schritt.

## Projekt-Überblick

- **Claude** spielt den DM (Dungeon Master) — Ton: Witcher / First Law, d20-System
- **Wiki** ist der persistente Weltzustand (Markdown-Dateien, Obsidian-kompatibel)
- **App** streamt DM-Antworten per SSE, liest/schreibt Wiki automatisch
- **STATE-Block**: DM hängt `[STATE:hp=X/Y,location=name,add_item=Name,...]` ans Ende — Backend strippt und schreibt in Wiki

## Dateistruktur

```
NovaTerrum/
├── DM.md                        # DM-Systemanweisung + Wiki-Konventionen
├── wiki/
│   ├── gamestate/
│   │   ├── current.md           # DYNAMISCH: HP, Ort, Inventar, Gold, Quests
│   │   └── character.md         # DYNAMISCH: Charakter-Stats, Skills, Hintergrund
│   ├── mechanics/
│   │   ├── skills.md            # Skill-System, XP-Formel, Bonus-Tabelle
│   │   ├── combat.md            # Kampfregeln
│   │   ├── progression.md       # Attribut-Progression
│   │   └── magic.md             # Arkana-System
│   ├── locations/               # Orte mit YAML-Frontmatter (koordinaten: [x, y])
│   ├── characters/              # NPCs und PC
│   ├── nations/                 # 7 Nationen
│   ├── factions/                # Fraktionen
│   ├── lore/                    # Weltbeschreibung, Ökosystem, aktuelle Ära
│   ├── creatures/               # Kreaturen-Statblöcke
│   └── sessions/                # Session-Protokolle (YYYY-MM-DD-titel.md)
└── app/
    ├── main.py                  # FastAPI-Backend
    ├── static/index.html        # Komplettes Frontend (ein File)
    ├── requirements.txt
    └── Dockerfile
```

## App lokal starten

```bash
cd app
pip install -r requirements.txt
python main.py
# → http://localhost:3000
```

Env-Var: `ANTHROPIC_API_KEY` muss gesetzt sein.

## App-Architektur (main.py)

- `build_system_prompt()` — DM.md als System-Prompt
- `build_context(mode)` — "minimal" | "smart" | "full" — smart lädt current.md + aktuellen Ort + combat.md + skills.md
- `parse_state_block(text)` — extrahiert `[STATE:...]` aus DM-Antwort
- `apply_state_updates(updates)` — schreibt HP/Ort/Gold/Items in current.md
- `GET /api/state` — gibt current.md + character.md als JSON
- `GET /api/map` — gibt Koordinaten aller Locations für SVG-Karte
- `POST /api/chat` — SSE-Stream, am Ende `done`-Event mit neuem State
- `GET /api/history`, `DELETE /api/history`
- `GET/POST /api/settings` — model (haiku/sonnet/opus) + context_mode

## Was noch fehlt / nächste Schritte

- **Wiki-Updates für NPCs/Locations**: DM legt neue NPC-Seiten nur manuell an — braucht Automatisierung (STATE-Block erweitern um `add_npc`, `add_location`?)
- **Synology-Deployment**: Dockerfile vorhanden, Wiki als Volume einbinden
- **Session-Ende-Flow**: Kein automatisches Session-Protokoll — muss manuell ausgelöst werden
- **XP-Tracking**: Wird in Sessionprotokoll notiert aber nicht in character.md geschrieben

## Git

Branch: `claude/pull-claude-skills-g8QFH` auf `noledge5/NovaTerrum`

## Agent skills

Issues leben als GitHub Issues in `noledge5/NovaTerrum`.
Standard-Labels: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix.
