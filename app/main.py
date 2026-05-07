import asyncio
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import AsyncGenerator, Optional

import anthropic
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="NovaTerrum DM")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Paths — WIKI_PATH can be overridden via env var for Docker
BASE = Path(os.environ.get("WIKI_PATH", Path(__file__).parent.parent))
WIKI = BASE / "wiki"
DM_MD = BASE / "DM.md"
CURRENT_MD = WIKI / "gamestate" / "current.md"
CHARACTER_MD = WIKI / "gamestate" / "character.md"

APP_DIR = Path(__file__).parent
HISTORY_FILE = APP_DIR / "history.json"
SETTINGS_FILE = APP_DIR / "settings.json"

MODELS = [
    {"id": "claude-haiku-4-5-20251001", "label": "Haiku (schnell, günstig)"},
    {"id": "claude-sonnet-4-6", "label": "Sonnet (ausgewogen)"},
    {"id": "claude-opus-4-7", "label": "Opus (mächtig, langsam)"},
]

DEFAULT_SETTINGS = {"model": "claude-haiku-4-5-20251001", "context_mode": "smart"}


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


settings: dict = load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())
history: list = load_json(HISTORY_FILE, [])


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def build_system_prompt() -> str:
    dm = read_file(DM_MD)
    return f"""{dm}

--- TECHNISCHE ANWEISUNG (unsichtbar für Spieler) ---
Wenn sich der Spielzustand geändert hat, füge am Ende deiner Antwort exakt diesen Block an:
[STATE:key=value,key=value]

Gültige Keys:
- hp=X/Y          (z.B. hp=8/18)
- location=name   (Ortsname kleingeschrieben, z.B. location=hartfeld)
- gold=X          (z.B. gold=15)
- add_item=Name
- remove_item=Name
- add_status=Name
- remove_status=Name
- add_injury=Name
- remove_injury=Name

Nur geänderte Felder. Block weglassen wenn nichts geändert hat. Keine Leerzeichen im Block."""


def build_context(mode: str) -> str:
    parts = []

    current = read_file(CURRENT_MD)
    if current:
        parts.append(f"## Spielzustand\n{current}")

    char = read_file(CHARACTER_MD)
    if char:
        parts.append(f"## Charakter\n{char}")

    if mode == "minimal":
        return "\n\n".join(parts)

    # Smart: add current location
    loc_match = re.search(r"\[\[([^\]]+)\]\]", current)
    if loc_match:
        loc_raw = loc_match.group(1).strip()
        if loc_raw not in ("—", ""):
            slug = loc_raw.lower().replace(" ", "-")
            candidates = list(WIKI.glob(f"locations/{slug}*.md"))
            if candidates:
                parts.append(f"## Aktueller Ort\n{read_file(candidates[0])}")

    parts.append(f"## Kampf\n{read_file(WIKI / 'mechanics/combat.md')}")
    parts.append(f"## Skills\n{read_file(WIKI / 'mechanics/skills.md')}")

    if mode == "full":
        for section in ("lore", "nations", "factions"):
            for f in sorted((WIKI / section).glob("*.md")):
                parts.append(f"## {f.stem}\n{read_file(f)}")
        for f in sorted(WIKI.glob("mechanics/*.md")):
            parts.append(f"## {f.stem}\n{read_file(f)}")

    return "\n\n---\n\n".join(parts)


def parse_state_block(text: str):
    match = re.search(r"\[STATE:([^\]]*)\]", text)
    if not match:
        return {}, text
    updates = {}
    for part in match.group(1).split(","):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            updates[k.strip()] = v.strip()
    clean = (text[: match.start()] + text[match.end() :]).strip()
    return updates, clean


def apply_state_updates(updates: dict):
    if not updates:
        return
    content = read_file(CURRENT_MD)
    if not content:
        return

    if "hp" in updates:
        content = re.sub(r"\*\*HP:\*\*[^\n]+", f"**HP:** {updates['hp']}", content)

    if "location" in updates:
        content = re.sub(r"\[\[[^\]]*\]\]", f"[[{updates['location']}]]", content, count=1)

    if "gold" in updates:
        content = re.sub(r"Gold:\s*\d+", f"Gold: {updates['gold']}", content)

    if "add_status" in updates:
        s = updates["add_status"]
        m = re.search(r"\*\*Statuseffekte:\*\*\s*(.+)", content)
        if m:
            cur = m.group(1).strip()
            new = s if cur in ("keine", "—") else f"{cur}, {s}"
            content = re.sub(r"\*\*Statuseffekte:\*\*[^\n]+", f"**Statuseffekte:** {new}", content)

    if "remove_status" in updates:
        s = re.escape(updates["remove_status"])
        content = re.sub(rf"(?:,\s*)?{s}(?:,\s*)?", "", content)
        content = re.sub(r"\*\*Statuseffekte:\*\*\s*,?\s*$", "**Statuseffekte:** keine", content, flags=re.MULTILINE)

    if "add_injury" in updates:
        inj = updates["add_injury"]
        m = re.search(r"\*\*Aktive Verletzungen:\*\*\s*(.+)", content)
        if m:
            cur = m.group(1).strip()
            new = inj if cur in ("keine", "—") else f"{cur}, {inj}"
            content = re.sub(r"\*\*Aktive Verletzungen:\*\*[^\n]+", f"**Aktive Verletzungen:** {new}", content)

    if "remove_injury" in updates:
        inj = re.escape(updates["remove_injury"])
        content = re.sub(rf"(?:,\s*)?{inj}(?:,\s*)?", "", content)

    if "add_item" in updates:
        item = updates["add_item"]
        if "*(leer)*" in content:
            content = content.replace("*(leer)*", f"- {item}", 1)
        else:
            content = re.sub(
                r"(## Inventar\n)((?:- .+\n)*)",
                lambda m: m.group(1) + m.group(2) + f"- {item}\n",
                content,
            )

    if "remove_item" in updates:
        item = re.escape(updates["remove_item"])
        content = re.sub(rf"^- {item}\n?", "", content, flags=re.MULTILINE)

    CURRENT_MD.write_text(content, encoding="utf-8")


def parse_current_state() -> dict:
    current = read_file(CURRENT_MD)
    char = read_file(CHARACTER_MD)

    state: dict = {
        "hp_current": None, "hp_max": None,
        "location": "—",
        "injuries": [], "status_effects": [],
        "inventory": [], "gold": 0, "quests": [],
        "attributes": {}, "skills": {}, "character_name": None,
    }

    m = re.search(r"\*\*HP:\*\*\s*(\d+)\s*/\s*(\d+)", current)
    if m:
        state["hp_current"] = int(m.group(1))
        state["hp_max"] = int(m.group(2))

    m = re.search(r"\[\[([^\]]+)\]\]", current)
    if m and m.group(1) not in ("—", ""):
        state["location"] = m.group(1)

    m = re.search(r"Gold:\s*(\d+)", current)
    if m:
        state["gold"] = int(m.group(1))

    m = re.search(r"\*\*Statuseffekte:\*\*\s*(.+)", current)
    if m and m.group(1).strip() not in ("keine", "—"):
        state["status_effects"] = [s.strip() for s in m.group(1).split(",") if s.strip() not in ("keine", "—")]

    m = re.search(r"\*\*Aktive Verletzungen:\*\*\s*(.+)", current)
    if m and m.group(1).strip() not in ("keine", "—"):
        state["injuries"] = [i.strip() for i in m.group(1).split(",") if i.strip() not in ("keine", "—")]

    m = re.search(r"## Inventar\n(.*?)\n## Gold", current, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip().lstrip("- ").strip()
            if line and line != "*(leer)*":
                state["inventory"].append(line)

    m = re.search(r"## Aktive Quests\n(.*?)(?=\n##|\Z)", current, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip().lstrip("- ").strip()
            if line and line != "*(keine)*":
                state["quests"].append(line)

    if char:
        m = re.search(r"^# (.+)$", char, re.MULTILINE)
        if m:
            state["character_name"] = m.group(1)
        for attr in ("STR", "DEX", "KON", "INT", "WIS", "CHA"):
            m = re.search(rf"{attr}:\s*(\d+)", char)
            if m:
                state["attributes"][attr] = int(m.group(1))
        m = re.search(r"## Skills\n(.*?)(?=\n##|\Z)", char, re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                sm = re.match(r"(.+?):\s*(\d+)", line.strip())
                if sm:
                    state["skills"][sm.group(1).strip()] = int(sm.group(2))

    return state


def get_map_data() -> list:
    locations = []
    current_state = parse_current_state()
    current_loc = current_state.get("location", "").lower().strip()

    for f in sorted(WIKI.glob("locations/*.md")):
        content = read_file(f)
        ym = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not ym:
            continue
        try:
            meta = yaml.safe_load(ym.group(1))
            coords = meta.get("koordinaten", [])
            if not coords or len(coords) != 2:
                continue
            nm = re.search(r"^# (.+)$", content, re.MULTILINE)
            display = nm.group(1) if nm else f.stem
            is_current = current_loc and (f.stem == current_loc or current_loc in f.stem)
            locations.append({
                "id": f.stem,
                "name": display,
                "x": coords[0],
                "y": coords[1],
                "region": meta.get("region", "mitte"),
                "current": bool(is_current),
            })
        except Exception:
            pass
    return locations


# --- API Routes ---

class ChatRequest(BaseModel):
    message: str

class SettingsUpdate(BaseModel):
    model: Optional[str] = None
    context_mode: Optional[str] = None

class CharacterCreate(BaseModel):
    name: str
    archetype: str
    attributes: dict
    skills: dict
    region: str
    start_location: str

class OpenSceneRequest(BaseModel):
    name: str
    archetype: str
    region: str


@app.get("/api/state")
async def get_state():
    return parse_current_state()


@app.get("/api/map")
async def get_map():
    return get_map_data()


@app.get("/api/models")
async def get_models():
    return MODELS


@app.get("/api/settings")
async def get_settings_route():
    return settings


@app.post("/api/settings")
async def update_settings(body: SettingsUpdate):
    if body.model:
        settings["model"] = body.model
    if body.context_mode:
        settings["context_mode"] = body.context_mode
    save_json(SETTINGS_FILE, settings)
    return settings


@app.get("/api/history")
async def get_history():
    return history


@app.delete("/api/history")
async def clear_history():
    global history
    history = []
    save_json(HISTORY_FILE, history)
    return {"ok": True}


@app.post("/api/chat")
async def chat(body: ChatRequest):
    global history
    msg = body.message.strip()
    if not msg:
        raise HTTPException(400, "Leere Nachricht")

    history.append({"role": "user", "content": msg})

    context = build_context(settings["context_mode"])
    system = build_system_prompt()
    if context:
        system += f"\n\n---\n\nKONTEXT:\n{context}"

    client = anthropic.Anthropic()

    async def stream() -> AsyncGenerator[str, None]:
        global history
        full = ""
        try:
            with client.messages.stream(
                model=settings["model"],
                max_tokens=2048,
                system=system,
                messages=history,
            ) as s:
                for chunk in s.text_stream:
                    full += chunk
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            history.pop()
            return

        updates, clean = parse_state_block(full)
        apply_state_updates(updates)
        history.append({"role": "assistant", "content": clean})
        save_json(HISTORY_FILE, history)

        new_state = parse_current_state()
        yield f"data: {json.dumps({'done': True, 'clean': clean, 'state': new_state})}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/create-character")
async def create_character(body: CharacterCreate):
    global history
    kon_mod = (body.attributes.get("KON", 10) - 10) // 2
    hp = max(1, 8 + kon_mod)

    lines = [f"# {body.name}", "", "## Attribute"]
    for attr in ["STR", "DEX", "KON", "INT", "WIS", "CHA"]:
        lines.append(f"{attr}: {body.attributes.get(attr, 10)}")
    lines += ["", "## Modifikatoren"]
    mods = []
    for attr in ["STR", "DEX", "KON", "INT", "WIS", "CHA"]:
        val = body.attributes.get(attr, 10)
        mod = (val - 10) // 2
        mods.append(f"{attr}: {'+' if mod >= 0 else ''}{mod}")
    lines.append(" | ".join(mods))
    lines += ["", "## HP", f"Max: {hp}", "", "## Skills"]
    for skill, level in sorted(body.skills.items(), key=lambda x: -x[1]):
        if level > 0:
            lines.append(f"{skill}: {level}")
    lines += ["", "## Archetyp", body.archetype, "", "## Hintergrund", "*(wird vom DM generiert)*", "", "## Notizen", "*(leer)*"]
    CHARACTER_MD.write_text("\n".join(lines), encoding="utf-8")

    today = date.today().isoformat()
    current = f"""---
type: gamestate
updated: {today}
---

# Aktueller Spielzustand

## In-Game Datum & Zeit

Datum: 1. Hartmond, Jahr 412
Uhrzeit: Früher Morgen

## Aufenthaltsort

[[{body.start_location}]]

## PC-Status

**HP:** {hp} / {hp}
**Aktive Verletzungen:** keine
**Statuseffekte:** keine

## Inventar

*(leer)*

## Gold & Wertgegenstände

Gold: 15

## Aktive Quests

*(keine)*

## Offene Fäden

*(keine)*

## Wer weiß was über mich?

*(unbekannt)*"""
    CURRENT_MD.write_text(current, encoding="utf-8")
    history = []
    save_json(HISTORY_FILE, history)
    return {"ok": True, "hp": hp}


@app.post("/api/open-scene")
async def open_scene(body: OpenSceneRequest):
    global history
    context = build_context(settings["context_mode"])
    system = build_system_prompt()
    if context:
        system += f"\n\n---\n\nKONTEXT:\n{context}"

    opening_msg = f"Charakter erstellt: {body.name}, {body.archetype}, Startregion: {body.region}. Starte direkt mit einer atmosphärischen Einstiegsszene. Keine Begrüßung, kein Meta-Kommentar. Zweite Person Präsens. Kurze Absätze. Sinneseindrücke zuerst."

    client = anthropic.Anthropic()

    async def stream() -> AsyncGenerator[str, None]:
        global history
        full = ""
        try:
            with client.messages.stream(
                model=settings["model"],
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": opening_msg}],
            ) as s:
                for chunk in s.text_stream:
                    full += chunk
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        updates, clean = parse_state_block(full)
        apply_state_updates(updates)
        history = [{"role": "user", "content": opening_msg}, {"role": "assistant", "content": clean}]
        save_json(HISTORY_FILE, history)
        new_state = parse_current_state()
        yield f"data: {json.dumps({'done': True, 'clean': clean, 'state': new_state})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.delete("/api/character")
async def delete_character():
    global history
    history = []
    save_json(HISTORY_FILE, history)
    CHARACTER_MD.write_text("# —\n", encoding="utf-8")
    CURRENT_MD.write_text("---\ntype: gamestate\nupdated: —\n---\n\n# Aktueller Spielzustand\n\n## Aufenthaltsort\n\n[[—]]\n\n## PC-Status\n\n**HP:** — / —\n**Aktive Verletzungen:** keine\n**Statuseffekte:** keine\n\n## Inventar\n\n*(leer)*\n\n## Gold & Wertgegenstände\n\nGold: 0\n\n## Aktive Quests\n\n*(keine)*\n\n## Offene Fäden\n\n*(keine)*\n\n## Wer weiß was über mich?\n\n*(unbekannt)*", encoding="utf-8")
    return {"ok": True}


# Static files (must be last)
static_dir = APP_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
