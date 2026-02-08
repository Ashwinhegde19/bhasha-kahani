#!/usr/bin/env python3
"""
Bulbul V3 Voice Comparison Tool for Kannada Storytelling

Generates audio samples for all candidate voices across characters,
serves a local web page to compare them side-by-side, and lets you
pick the best voice for each character.

Usage:
    python test_voices.py generate   # Generate all audio samples (skips existing)
    python test_voices.py serve      # Serve comparison UI on http://localhost:9000
    python test_voices.py all        # Generate + serve
"""

import asyncio
import httpx
import base64
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dataclasses import dataclass, field, asdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_URL = "https://api.sarvam.ai/text-to-speech"
HEADERS = {
    "api-subscription-key": settings.sarvam_api_key,
    "Content-Type": "application/json",
}
OUTPUT_DIR = Path("voice_tests")
MAX_RETRIES = 3
CONCURRENCY = 4  # parallel API calls


@dataclass
class Character:
    name: str
    description: str
    text_kn: str
    text_en: str  # English gloss so you know what's being said
    current_voice: str
    candidate_voices: list[str]


CHARACTERS: list[Character] = [
    Character(
        name="Ajji (Narrator)",
        description="Warm grandmother storyteller narrating a folk tale",
        text_kn="ಒಂದಾನೊಂದು ಕಾಲದಲ್ಲಿ, ಒಂದು ದಟ್ಟವಾದ ಕಾಡಿನ ಅಂಚಿನಲ್ಲಿ, "
        "ಪುಣ್ಯಕೋಟಿ ಎಂಬ ಹಸು ತನ್ನ ಕರುವಿನ ಜೊತೆ ವಾಸಿಸುತ್ತಿದ್ದಳು.",
        text_en="Once upon a time, on the edge of a dense forest, "
        "a cow named Punyakoti lived with her calf.",
        current_voice="shubh",
        candidate_voices=[
            "shubh",
            "kavitha",
            "shruti",
            "suhani",
            "anand",
            "mani",
            "gokul",
            "manan",
        ],
    ),
    Character(
        name="Punyakoti (Cow)",
        description="Gentle, motherly cow speaking to her calf",
        text_kn="ನನ್ನ ಪ್ರೀತಿಯ ಕರುವೇ, ನಾನು ಬೆಳಿಗ್ಗೆ ಹುಲ್ಲು ಮೇಯಲು ಹೋಗಿ, ಸಂಜೆ ಮರಳಿ ಬರುತ್ತೇನೆ.",
        text_en="My dear calf, I will go to graze in the morning "
        "and return in the evening.",
        current_voice="priya",
        candidate_voices=["priya", "kavitha", "rupali", "suhani", "shruti", "kavya"],
    ),
    Character(
        name="Arbhuta (Tiger)",
        description="Fierce, commanding tiger threatening his prey",
        text_kn="ನಿಲ್ಲು! ನೀನು ನನ್ನ ಕಾಡಿನಲ್ಲಿ ಅತಿಕ್ರಮಿಸಿದ್ದೀಯ. ನೀನು ಈಗ ನನ್ನ ಆಹಾರ!",
        text_en="Stop! You have trespassed into my forest. You are now my food!",
        current_voice="aditya",
        candidate_voices=["aditya", "vijay", "gokul", "amit", "ashutosh", "kabir"],
    ),
    Character(
        name="Crow",
        description="Clever, energetic crow with a plan",
        text_kn="ಕಾ ಕಾ! ನನಗೆ ಒಂದು ಉಪಾಯ ಗೊತ್ತು! ಕೇಳಿ, ನಾನು ಹೇಳುತ್ತೇನೆ!",
        text_en="Caw caw! I know a trick! Listen, I will tell you!",
        current_voice="neha",
        candidate_voices=["neha", "ishita", "shreya", "rupali", "pooja"],
    ),
]

# ---------------------------------------------------------------------------
# Audio generation
# ---------------------------------------------------------------------------

sem: asyncio.Semaphore


async def synthesize(
    text: str, speaker: str, retries: int = MAX_RETRIES
) -> bytes | None:
    """Call Sarvam TTS with retry logic."""
    payload = {
        "text": text,
        "target_language_code": "kn-IN",
        "speaker": speaker,
        "model": "bulbul:v3",
        "pace": 0.95,
        "speech_sample_rate": "24000",
        "temperature": 0.8,
    }
    for attempt in range(1, retries + 1):
        async with sem:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        API_URL, headers=HEADERS, json=payload, timeout=60.0
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    if "audios" in data and data["audios"]:
                        return base64.b64decode(data["audios"][0])
                    return None
            except Exception as e:
                if attempt < retries:
                    wait = 2**attempt
                    print(
                        f"    retry {attempt}/{retries} for {speaker} in {wait}s ({e})"
                    )
                    await asyncio.sleep(wait)
                else:
                    print(f"    FAILED {speaker} after {retries} attempts: {e}")
                    return None


def char_dir(char: Character) -> Path:
    slug = char.name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    return OUTPUT_DIR / slug


async def generate_for_character(char: Character):
    """Generate all voice samples for one character, skipping existing files."""
    d = char_dir(char)
    d.mkdir(parents=True, exist_ok=True)

    tasks = []
    for voice in char.candidate_voices:
        wav = d / f"{voice}.wav"
        if wav.exists() and wav.stat().st_size > 1000:
            print(
                f"  [{char.name}] {voice:12s} -- cached ({wav.stat().st_size // 1024} KB)"
            )
            continue
        tasks.append((voice, wav))

    if not tasks:
        print(f"  [{char.name}] all voices already generated")
        return

    async def _gen(voice: str, path: Path):
        print(f"  [{char.name}] {voice:12s} -- generating...", end="", flush=True)
        audio = await synthesize(char.text_kn, voice)
        if audio:
            path.write_bytes(audio)
            print(f" OK ({len(audio) // 1024} KB)")
        else:
            print(" FAILED")

    await asyncio.gather(*[_gen(v, p) for v, p in tasks])


async def generate_all():
    global sem
    sem = asyncio.Semaphore(CONCURRENCY)

    print("=" * 60)
    print("Generating Kannada voice samples (Bulbul V3)")
    print("=" * 60)

    for char in CHARACTERS:
        print(f"\n>> {char.name}: {char.description}")
        print(f"   Kannada : {char.text_kn}")
        print(f"   English : {char.text_en}")
        print(f"   Voices  : {', '.join(char.candidate_voices)}")
        await generate_for_character(char)

    # Write metadata for the HTML player
    meta = []
    for char in CHARACTERS:
        d = char_dir(char)
        voices = []
        for v in char.candidate_voices:
            wav = d / f"{v}.wav"
            if wav.exists():
                voices.append(
                    {
                        "name": v,
                        "path": str(wav),
                        "size_kb": round(wav.stat().st_size / 1024, 1),
                        "is_current": v == char.current_voice,
                    }
                )
        meta.append(
            {
                "name": char.name,
                "description": char.description,
                "text_kn": char.text_kn,
                "text_en": char.text_en,
                "current_voice": char.current_voice,
                "voices": voices,
            }
        )

    meta_path = OUTPUT_DIR / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    total = sum(
        1
        for c in CHARACTERS
        for v in c.candidate_voices
        if (char_dir(c) / f"{v}.wav").exists()
    )
    expected = sum(len(c.candidate_voices) for c in CHARACTERS)
    print(f"\n{'=' * 60}")
    print(f"Done: {total}/{expected} samples generated")
    print(f"Metadata: {meta_path}")
    print(f"{'=' * 60}")


# ---------------------------------------------------------------------------
# Web-based comparison player
# ---------------------------------------------------------------------------

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bulbul V3 - Kannada Voice Comparison</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: #0f0f0f; color: #e0e0e0; padding: 2rem;
  }
  h1 { text-align: center; margin-bottom: .5rem; font-size: 1.8rem; color: #fff; }
  .subtitle { text-align: center; color: #888; margin-bottom: 2rem; }
  .character {
    background: #1a1a1a; border-radius: 12px; padding: 1.5rem;
    margin-bottom: 1.5rem; border: 1px solid #333;
  }
  .character h2 { font-size: 1.3rem; margin-bottom: .25rem; color: #f0f0f0; }
  .character .desc { color: #999; font-size: .85rem; margin-bottom: .75rem; }
  .text-block {
    background: #111; border-radius: 8px; padding: .75rem 1rem;
    margin-bottom: 1rem; border-left: 3px solid #555;
  }
  .text-block .kn { font-size: 1.1rem; line-height: 1.6; color: #ddd; }
  .text-block .en { font-size: .8rem; color: #777; margin-top: .25rem; font-style: italic; }
  .voices { display: flex; flex-wrap: wrap; gap: .75rem; }
  .voice-card {
    background: #222; border: 2px solid #333; border-radius: 10px;
    padding: .75rem 1rem; min-width: 140px; cursor: pointer;
    transition: all .15s ease; position: relative;
  }
  .voice-card:hover { border-color: #666; background: #2a2a2a; }
  .voice-card.playing { border-color: #4ade80; background: #1a2e1a; }
  .voice-card.current { border-color: #f59e0b; }
  .voice-card .vname { font-weight: 600; font-size: 1rem; text-transform: capitalize; }
  .voice-card .vsize { font-size: .75rem; color: #666; }
  .voice-card .badge {
    position: absolute; top: -8px; right: -8px; font-size: .65rem;
    padding: 2px 6px; border-radius: 4px; font-weight: 600;
  }
  .badge.current-badge { background: #f59e0b; color: #000; }
  .play-icon { display: inline-block; margin-right: .4rem; }
  .controls {
    display: flex; gap: 1rem; align-items: center; margin-top: 1rem;
    padding-top: .75rem; border-top: 1px solid #333;
  }
  .btn {
    background: #333; color: #fff; border: none; padding: .5rem 1rem;
    border-radius: 6px; cursor: pointer; font-size: .85rem;
    transition: background .15s;
  }
  .btn:hover { background: #444; }
  .btn.stop { background: #7f1d1d; }
  .btn.stop:hover { background: #991b1b; }
  .btn.auto { background: #1e3a5f; }
  .btn.auto:hover { background: #264d7a; }
  .now-playing { font-size: .85rem; color: #4ade80; }
</style>
</head>
<body>

<h1>Kannada Voice Comparison</h1>
<p class="subtitle">Bulbul V3 &middot; Click any voice to play &middot; Yellow border = current voice</p>

<div id="app"></div>

<script>
let audio = null;
let playingId = null;

function stop() {
  if (audio) { audio.pause(); audio = null; }
  document.querySelectorAll('.voice-card').forEach(c => c.classList.remove('playing'));
  document.querySelectorAll('.now-playing').forEach(el => el.textContent = '');
  playingId = null;
}

function play(path, cardId, charIdx) {
  stop();
  audio = new Audio('/' + path);
  playingId = cardId;
  const card = document.getElementById(cardId);
  const np = document.getElementById('np-' + charIdx);
  card.classList.add('playing');
  np.textContent = 'Playing: ' + cardId.split('-').pop();
  audio.onended = () => {
    card.classList.remove('playing');
    np.textContent = '';
    playingId = null;
  };
  audio.play();
}

async function autoPlay(charIdx, voices) {
  for (const v of voices) {
    const cardId = 'card-' + charIdx + '-' + v.name;
    play(v.path, cardId, charIdx);
    await new Promise(resolve => {
      audio.onended = () => {
        document.getElementById(cardId).classList.remove('playing');
        resolve();
      };
    });
    // short gap between voices
    await new Promise(r => setTimeout(r, 600));
  }
  document.getElementById('np-' + charIdx).textContent = 'Done!';
}

fetch('/meta.json').then(r => r.json()).then(data => {
  const app = document.getElementById('app');
  data.forEach((char, ci) => {
    const div = document.createElement('div');
    div.className = 'character';
    div.innerHTML = `
      <h2>${char.name}</h2>
      <div class="desc">${char.description}</div>
      <div class="text-block">
        <div class="kn">${char.text_kn}</div>
        <div class="en">${char.text_en}</div>
      </div>
      <div class="voices">
        ${char.voices.map(v => `
          <div class="voice-card ${v.is_current ? 'current' : ''}"
               id="card-${ci}-${v.name}"
               onclick="play('${v.path}', 'card-${ci}-${v.name}', ${ci})">
            ${v.is_current ? '<span class="badge current-badge">current</span>' : ''}
            <div class="vname"><span class="play-icon">&#9654;</span>${v.name}</div>
            <div class="vsize">${v.size_kb} KB</div>
          </div>
        `).join('')}
      </div>
      <div class="controls">
        <button class="btn auto" onclick="autoPlay(${ci}, ${JSON.stringify(char.voices).replace(/"/g, '&quot;')})">
          Auto-play all
        </button>
        <button class="btn stop" onclick="stop()">Stop</button>
        <span class="now-playing" id="np-${ci}"></span>
      </div>
    `;
    app.appendChild(div);
  });
});
</script>
</body>
</html>"""


def serve(port: int = 9000):
    """Serve voice_tests/ with the comparison HTML player."""
    # Write the HTML page
    index = OUTPUT_DIR / "index.html"
    index.write_text(HTML_PAGE)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(OUTPUT_DIR), **kwargs)

        def log_message(self, format, *args):
            pass  # quiet

    print(f"\nServing voice comparison at http://localhost:{port}")
    print("Open in your browser and click voices to compare.")
    print("Press Ctrl+C to stop.\n")
    HTTPServer(("", port), Handler).serve_forever()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd == "generate":
        asyncio.run(generate_all())
    elif cmd == "serve":
        serve()
    elif cmd == "all":
        asyncio.run(generate_all())
        serve()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
