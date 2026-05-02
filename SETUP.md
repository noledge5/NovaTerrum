# Setup-Guide: NovaTerrum mit Claude Code

## Was dieses Repo ist

Ein persistentes Markdown-Wiki, das einen Dungeon Master ersetzt — gepflegt von Claude. Claude baut aktiv ein strukturiertes Wiki auf und ab, statt klassisches RAG zu nutzen.

## Tool: Claude Code

Claude Code ist das empfohlene Tool für dieses Repo.

### Installation

```bash
npm install -g @anthropic-ai/claude-code
```

### Starten

```bash
cd NovaTerrum
claude
```

Claude Code liest `CLAUDE.md` und `DM.md` automatisch als Kontext.

### Empfohlener Workflow

#### Erste Session

```
Lies DM.md, dann lies wiki/rules/character-creation.md,
und führe mich durch die Charaktererstellung.
```

#### Während des Spiels

Schreibe einfach was dein Charakter tut. Claude:
- Beschreibt Konsequenzen narrativ
- Würfelt im Hintergrund
- Zeigt Würfe transparent nach der Szene
- Updated `gamestate/current.md` inline

#### Session-Ende

```
Session-Ende, fasse zusammen.
```

Claude schreibt das Session-Protokoll, updated `index.md` und `log.md`.

Danach committen:

```bash
git add -A && git commit -m "Session N — Kurztitel"
```

## Obsidian als Live-View

Öffne das Repo als Obsidian-Vault für eine schöne Ansicht des Wikis während Claude Code im Terminal läuft. Graph View zeigt die Verbindungen zwischen Wiki-Seiten visuell.

## Git als Spielstand

Jede Session committen — dann kannst du später zurückspringen oder branchen ("was wäre wenn ich diese Quest abgelehnt hätte?").

## Inspirationsquellen in `raw/`

Lege Weltbau-Material, Auszüge, Bilder-Beschreibungen etc. in `raw/`. Dann:

```
Verarbeite raw/meine-datei.md
```

Claude liest die Quelle, bespricht Kernpunkte mit dir, und integriert sie ins Wiki.

## DM.md anpassen

`DM.md` ist deine Datei. Editiere Regeln, Ton, Mechaniken wann immer du willst. Das System co-evolviert mit dir.
