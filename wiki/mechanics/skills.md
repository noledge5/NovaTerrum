---
type: mechanic
created: 2026-05-02
updated: 2026-05-02
tags: [skills, progression, mechanics]
---

# Skill-System

## Grundprinzip

Jede Handlung bei der ein Skill oder Attribut relevant ist gibt Erfahrung — egal ob Erfolg oder Misserfolg. Kompetenz entsteht durch Tun.

## Würfelprobe

```
1d20 + Attribut-Mod + Skill-Bonus vs. DC
```

**Skill-Bonus:** `⌊Skill-Level ÷ 5⌋`

| Skill-Level | Bonus |
|-------------|-------|
| 0–4         | +0    |
| 5–9         | +1    |
| 10–14       | +2    |
| 15–19       | +3    |
| 20–24       | +4    |
| 25–29       | +5    |
| …           | …     |

Kein hartes Cap — hohe Boni sind theoretisch erreichbar, aber durch exponentiell steigende XP-Kosten natürlich gebremst.

## Untrainierte Skills (Level 0)

Jeder Skill ist von Anfang an nutzbar. Bei Level 0 entfällt der Skill-Bonus:

```
1d20 + Attribut-Mod (kein Skill-Bonus)
```

XP fließt trotzdem — der erste Wurf ist der Beginn des Lernens.

## Skill-XP

**XP pro Aktion:** `max(1, DC - 5)`

| DC | XP |
|----|-----|
| 5  | 1   |
| 10 | 5   |
| 15 | 10  |
| 20 | 15  |
| 25 | 20  |

Erfolg und Misserfolg geben gleich viel XP — man lernt auch aus Fehlern.

## Aufstiegskosten

**XP für Skill-Level n:** `n² × 10`

| Aufstieg | Kosten |
|----------|--------|
| 0 → 1    | 10 XP  |
| 1 → 2    | 40 XP  |
| 5 → 6    | 360 XP |
| 10 → 11  | 1.000 XP |
| 20 → 21  | 4.000 XP |

## Skill-Liste

### STR — Stärke
- Nahkampf
- Waffenloser Kampf
- Athletik
- Blockieren
- Schwerarbeit
- Einschüchtern

### DEX — Geschicklichkeit
- Fernkampf
- Ausweichen
- Schleichen
- Schlösserknacken
- Taschendiebstahl
- Akrobatik

### KON — Konstitution
- Ausdauer
- Zähigkeit
- Giftresistenz
- Wildnisüberleben
- Schmerztoleranz

### INT — Intelligenz
- Arkana
- Heilkunde
- Handwerk
- Alchemie
- Geschichte
- Mechanik

### WIS — Weisheit
- Wahrnehmung
- Tierkunde
- Naturkunde
- Spurenlesen
- Intuition
- Meditation

### CHA — Charisma
- Überreden
- Täuschen
- Auftreten
- Handel
- Führung
- Verführen

## Meilenstein-Perks

Bei Skill-Level **10, 25, 50, 100** schaltet sich ein Perk frei — Wahl aus 2–3 skill-spezifischen Optionen.

Perk-Listen: `wiki/mechanics/perks/` *(wird bei Charaktererstellung befüllt)*

## Änderungshistorie

- 2026-05-02 — Seite angelegt
