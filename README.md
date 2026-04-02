# Synastria v10.3.0

**Astrological Oracle — Natal Profiles & Traceable Synastral Analysis**

A self-contained, single-file HTML astrological application. Open it in any modern browser — no build step, no server, no dependencies. Everything runs locally in your browser.

---

## What it does

Synastria computes astrological charts from birth data and generates human-readable psychological interpretations. It operates in two modes:

**Solo (Natal Profile) — one person**
- Full natal chart: 10 planets + Ascendant
- Natal aspects, elemental/modality balance, lunar phase, essential dignities, retrograde flags
- 9-section oracle report: Core Identity, Inner World, Persona, Planetary Strengths & Challenges, Harmonious and Dynamic Aspects, Retrograde Planets, Synthesis
- Confidence Index with natal-specific metrics

**Duo (Synastry) — two people**
- Natal charts for both partners
- Full 11x11 synastry grid (121 planet pairs)
- Compatibility scores across 6 domains: Overall, Love, Passion, Harmony, Mental, Karmic
- Oracle compatibility report with evidence cards and domain rings
- Both natal profiles available alongside the compatibility analysis

---

## Usage

1. Open `index.html` in any modern browser (Chrome, Firefox, Safari, Edge)
2. Enter a birth date (type `DD/MM/YYYY` or use the calendar picker)
3. Optionally enter birth time (improves Moon accuracy and enables Ascendant)
4. Optionally select a birth city (for UTC offset and latitude)
5. For synastry, fill in a second person's data
6. Click **Cast the Charts**
7. Use **Reset** to clear everything, or **Export PDF** to save a print-ready report

No internet connection is required for the core calculation. Internet is used only for city search (open-meteo geocoding API) and optional LLM calls.

---

## Astronomy engine

Planetary positions are computed entirely in JavaScript, client-side, using classical algorithms from *Astronomical Algorithms* (Jean Meeus, 2nd ed.).

| Component | Method | Verified accuracy |
|---|---|---|
| Sun | VSOP87 geometric mean + aberration | ≤ 0.5° vs JPL |
| Moon | Brown 16-term simplified series | ≤ 0.1° vs JPL |
| Mercury, Venus, Mars | VSOP87 truncated L/B/R, heliocentric → geocentric | ≤ 0.5° vs JPL |
| Jupiter, Saturn | Secular elements + perturbation terms | ≤ 2-3° vs JPL |
| Uranus, Neptune, Pluto | Secular elements (Meeus Table 31.b) | ≤ 2° vs JPL |
| Ascendant | GMST + obliquity + latitude | ≤ 0.01° vs Swiss Ephemeris |

All accuracy figures are verified by the automated test suite against JPL Horizons (1920-2050) and Swiss Ephemeris (Kerykeion/pyswisseph, JPL DE431). Position errors for outer planets rarely affect sign placement (signs are 30° wide); they matter only for tight aspects (orb ≤ 2°), which the Confidence Index flags.

Retrograde detection uses a 1-day finite difference. Direction detection is reliable even for outer planets — positional uncertainty (≤ 2°) is orders of magnitude larger than daily motion (~0.01-0.04°/day), but the sign of the motion is unaffected.

---

## Interpretation engine

### Built-in mode (no API key required)

Rule-based interpreter with 192 bespoke planet-pair interpretations:

- **100%** of personal planet combinations (Sun, Moon, Mercury, Venus, Mars, Ascendant)
- **100%** of personal × social/outer hard aspects (Conjunction, Square, Opposition)
- **~58%** of all 330 possible planet × aspect combinations
- Remaining combinations fall back to generic aspect-type explanations

All interpretations are plain-language psychological prose — no astrology knowledge required.

### LLM mode

Connect any of these providers for AI-generated reports:

| Provider | Model | Notes |
|---|---|---|
| **Anthropic** | `claude-sonnet-4-6` | API key required |
| **OpenAI** | `gpt-5.4` | API key required, uses `max_completion_tokens` |
| **Google Gemini** | `gemini-2.0-flash` | API key required |
| **Ollama** | `llama3` | Local, no API key; run `OLLAMA_ORIGINS=* ollama serve` |

The LLM receives pre-computed positions, aspects, dignities, and scores as structured data. It interprets — never recalculates. Self-reported confidence is parsed from a JSON block and displayed in the Confidence Index.

---

## Confidence Index

Every output includes a Confidence Index measuring calculation reliability, not relationship strength.

**Natal metrics:** Astronomical Precision, Birth Time, Dignity Reliability, Retrograde Reliability, Oracle Assessment (LLM only)

**Synastry metrics:** Astronomical Precision, Aspect Coverage (out of 121 pairs), Domain Coherence, Oracle Assessment (LLM only)

---

## Test suite

The project includes a comprehensive pytest-based test suite validated against authoritative external sources.

### Quick start

```bash
pip install -r requirements.txt
pytest -v                          # run all 525 tests
pytest -m structural               # 105 HTML/engine inspection tests
pytest -m unit                     # 265 unit tests (single Node.js batch)
pytest -m jpl                      # 142 JPL Horizons validation tests
pytest -m ascendant                # 13 Swiss Ephemeris ascendant tests
pytest --no-jpl                    # skip external API tests
pytest --clear-cache               # clear JPL response cache
```

### What's tested

| Category | Tests | Reference | Tolerance |
|---|---|---|---|
| Structural (HTML/engine) | 105 | Static inspection | N/A |
| Unit (all engine functions) | 265 | Self-consistent | Various |
| JPL Horizons (planet positions) | 142 | JPL DE441 | 0.5°-3° per planet |
| Swiss Ephemeris (ascendant) | 13 | JPL DE431 via Kerykeion | 2° (actual max: 0.01°) |

Tolerances are configurable in `tolerances.json`.

### Requirements

- Python 3.9+
- Node.js 14+ (for executing the extracted JS engine)
- `pytest >= 8.0`
- `kerykeion >= 4.0` (Swiss Ephemeris bindings, for ascendant validation)

---

## Languages

Full interface and all generated content available in:

- English
- French
- Italian

Language can be switched at any time. Built-in reports re-render immediately.

---

## Architecture

The application is a **single HTML file** (~3,500 lines). No build tools, no npm, no backend.

```
index.html
├── CSS (inline <style>)
│   └── @media print stylesheet for PDF export
├── HTML structure
│   ├── Input panel (birth data, city search, calendar picker)
│   ├── Oracle configuration (LLM provider selection)
│   ├── Results (reports, confidence, traces)
│   └── Action buttons (Reset, Export PDF)
└── JavaScript (inline <script>)
    ├── I18N (EN/FR/IT — all labels, tooltips, interpretations)
    ├── Astronomy engine (VSOP87, Brown, secular elements, Kepler)
    ├── Natal profile (aspects, dignities, retrogrades, lunar phase)
    ├── Synastry engine (pair matrix, weighted scoring, 5 domains)
    ├── Interpretation engine (192 built-in + LLM prompt builders)
    ├── Confidence engine (natal + synastry composite scores)
    └── UI (calendar, city search, collapsible panels, SVG rings)
```

### Test suite structure

```
tests/
├── conftest.py              # session fixtures, CLI options, report plugin
├── test_structural.py       # HTML/engine structural inspection
├── test_unit.py             # batch engine tests via Node.js
├── test_jpl.py              # JPL Horizons planet validation
├── test_ascendant.py        # Swiss Ephemeris ascendant validation
└── helpers/
    ├── engine.py            # extract_engine(), JS shims
    ├── node_runner.py       # find_node(), run_node()
    ├── jpl.py               # JPL client, cache, tolerances
    └── formatting.py        # ANSI color helpers
```

---

## Privacy

- All calculations happen **entirely in your browser** — no birth data is sent to any server
- City search sends only the city name to open-meteo (no birth data)
- LLM mode sends computed chart data (positions, aspects, scores) to the selected provider — **no raw birth dates or times**, only derived astronomical data
- API keys are stored only in browser session memory, never persisted

---

## Astrological approach

Synastria uses **Western tropical astrology**:

- Zodiac anchored to the vernal equinox (tropical, not sidereal)
- House system: Ascendant only (whole-sign implied); no house cusps computed
- Essential dignities: domicile, exaltation, detriment, fall for all 10 planets
- Aspects: Conjunction (8°), Sextile (6°), Square (8°), Trine (8°), Quincunx (3°), Opposition (8°)
- Synastry scoring: weighted aspect model across 5 domains with 86 pair-weight entries

Interpretations are written for a general audience — every astrological term is explained in plain psychological language.
