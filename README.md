# NovaTerrum

Ein textbasiertes Grimdark-Rollenspiel, geführt von Claude Code als Dungeon Master.

## Schnellstart

1. `SETUP.md` lesen — Claude Code einrichten
2. `DM.md` lesen — DM-Regeln und Wiki-Konventionen
3. Session starten: Claude Code öffnen, `DM.md` als Kontext laden

## Struktur

```
NovaTerrum/
├── CLAUDE.md          # Agent-Konfiguration (Issue Tracker, Labels, Domain Docs)
├── DM.md              # DM-Schema: Ton, Mechaniken, Wiki-Konventionen
├── SETUP.md           # Claude Code Einrichtung
├── index.md           # Wiki-Katalog (alle Seiten)
├── log.md             # Append-only Spiellog
└── wiki/
    ├── templates/     # Vorlagen: character.md, location.md
    ├── gamestate/     # Aktueller Zustand, Quests
    ├── rules/         # Charaktererstellung, Regelwerk
    ├── mechanics/     # Kampf, Magie, etc.
    ├── characters/    # NPCs & PCs
    ├── locations/     # Orte & Karten
    ├── factions/      # Fraktionen & Organisationen
    ├── lore/          # Weltgeschichte & Mythos
    └── sessions/      # Sitzungsnotizen
```

## Regeln auf einen Blick

- **System:** Leichtes d20-System, grimdark, verletzungsschwer
- **Attribute:** STR, DEX, KON, INT, WIS, CHA (Modifikator: `(Wert-10)/2`)
- **HP-Start:** 8 + KON-Mod
- **AC:** 10 + DEX-Mod (ohne Rüstung)
- **Kampf:** 1d20 + Mod vs. AC → Treffer → Schaden
- **Verletzungen:** Wurf bei <25% HP oder Krit — 1d12-Tabelle
- **Tod:** 3 Sterbenswürfe (1d20+KON vs. DC 10)

Details: `wiki/rules/character-creation.md`, `wiki/mechanics/combat.md`

## DM-Modi

| Modus | Zweck |
|-------|-------|
| **Dungeon Master** | Narrativ, Szenen beschreiben, Würfe auflösen |
| **Wiki-Maintainer** | Wiki-Dateien anlegen/aktualisieren |

## Tools

- **Claude Code CLI** — Haupt-Interface
- **GitHub Issues** (`noledge5/NovaTerrum`) — Aufgaben & Bugs
- **Obsidian** (optional) — Wiki lesen/navigieren
