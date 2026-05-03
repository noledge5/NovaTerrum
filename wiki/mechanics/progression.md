---
type: mechanic
created: 2026-05-02
updated: 2026-05-02
tags: [progression, attributes, level, mechanics]
---

# Progression & Attribut-Aufstieg

## Charakter-Level

Es gibt kein separates XP-Level. Das effektive Charakter-Level ergibt sich aus der Summe aller Skill-Aufstiege:

```
Charakter-Level = Summe aller Skill-Level ÷ 10 (abgerundet)
```

Rein informativ — für Skalierung und Einschätzung der Kampfstärke.

## Attribut-Aufstieg

Skill-Aufstiege füllen einen Zähler pro Attribut. Sobald der Zähler voll ist, gibt es einen verteilbaren Attributspunkt.

**Kosten für Attributspunkt bei Attributwert n:** `⌊n² ÷ 2⌋` Skill-Aufstiege im zugehörigen Attribut

| Attributwert | Aufstiege für nächsten Punkt |
|--------------|------------------------------|
| 8            | 32                           |
| 10           | 50                           |
| 12           | 72                           |
| 14           | 98                           |
| 16           | 128                          |
| 18           | 162                          |
| 20           | 200                          |

**Bindung:** Aufstiege in STR-Skills zählen nur für STR, DEX-Skills nur für DEX usw.

### Beispiel

Charakter hat STR 12. Hat 72 Aufstiege in STR-Skills (Nahkampf, Athletik…) angesammelt → erhält 1 Punkt auf STR → STR wird 13. Nächster Punkt kostet nun `⌊13² ÷ 2⌋ = 84` Aufstiege.

## Soft Cap durch Kostenexplosion

Kein hartes Limit auf Attributwerte oder Skill-Level. Die quadratisch steigenden Kosten machen sehr hohe Werte zu echten Langzeitzielen:

- Skill von 0 auf 10 leveln: **385 XP gesamt**
- Skill von 10 auf 20 leveln: **2.850 XP zusätzlich**
- Skill von 20 auf 30 leveln: **7.550 XP zusätzlich**

Attribut von 10 auf 15 bringen: **~430 Skill-Aufstiege** in zugehörigen Skills.

## Änderungshistorie

- 2026-05-02 — Seite angelegt
