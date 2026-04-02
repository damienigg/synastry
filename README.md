# Synastria v10

**Astrological Oracle — Natal Profiles & Traceable Synastral Analysis**

A self-contained, single-file HTML astrological application. Open it in any modern browser — no build step, no server, no dependencies to install. Everything runs locally in your browser.

---

## What it does

Synastria computes astrological charts from birth data and generates human-readable psychological interpretations. It operates in two modes:

**Solo (Natal Profile) — one person**
- Computes full natal chart: 10 planets + Ascendant
- Calculates natal aspects, elemental/modality balance, lunar phase, essential dignities, retrograde flags
- Generates a 9-section natal oracle report covering: Core Identity, Inner World, Persona, Planetary Strengths & Challenges, Harmonious and Dynamic Aspects, Retrograde Planets, Synthesis
- Displays a Confidence Index with natal-specific metrics

**Duo (Synastry) — two people**
- Computes natal charts for both partners
- Builds a full 11×11 synastry grid (121 planet pairs)
- Scores compatibility across 6 domains: Overall, Love, Passion, Harmony, Mental, Karmic
- Generates an oracle compatibility report with evidence cards and domain rings
- Both natal profiles are available collapsed alongside the compatibility analysis

---

## Usage

1. Open `synastria-v10.html` in any modern browser (Chrome, Firefox, Safari, Edge)
2. Enter a birth date (type `DD/MM/YYYY` or use the calendar picker)
3. Optionally enter birth time (improves Moon accuracy and enables Ascendant calculation)
4. Optionally select a birth city (for UTC offset and latitude)
5. For synastry, fill in a second person's data
6. Click **Calculate**

No internet connection is required for the core calculation. Internet is used only for city search (open-meteo geocoding API) and LLM calls if an API key is configured.

---

## Astronomy engine

The planetary positions are computed entirely in JavaScript, client-side, using classical astronomical algorithms from *Astronomical Algorithms* (Jean Meeus, 2nd ed.).

| Planet group | Method | JPL Horizons accuracy |
|---|---|---|
| Sun | VSOP87 geometric mean + aberration | ≤ 0.5° |
| Moon | Brown 16-term simplified series | ≤ 5.0° |
| Mercury, Venus, Mars | VSOP87 truncated L/B/R series, heliocentric → geocentric | ≤ 0.5° |
| Jupiter, Saturn | Secular elements + perturbation terms | ≤ 2–3° |
| Uranus, Neptune | Secular elements (Meeus Table 31.b) | ≤ 2°, ≤ 1° |
| Pluto | Secular elements | ≤ 2° |
| Ascendant | GMST + obliquity + latitude | Depends on birth time accuracy |

All accuracy figures are verified against JPL Horizons for dates 1950–2050. Position errors for outer planets rarely affect sign placement (signs are 30° wide); they matter only for tight aspects (orb ≤ 2°), which is flagged in the Confidence Index.

Retrograde detection uses a 1-day finite difference on the computed longitude. Direction detection is reliable even for outer planets — the positional uncertainty (≤ 2°) is orders of magnitude larger than the daily motion (~0.01–0.04°/day), but the sign of the motion (direct vs retrograde) is unaffected.

---

## Interpretation engine

### Built-in mode (no API key required)

When no LLM provider is configured, the app uses a rule-based built-in interpreter.

**Coverage:**
- **100%** of personal planet combinations: all 6 aspect types × every pair among Sun, Moon, Mercury, Venus, Mars, and the Ascendant (60 bespoke interpretations)
- **100%** of personal × social hard aspects: Conjunction, Square, Opposition for Sun/Moon/Venus/Mars × Jupiter/Saturn (48 entries)
- **100%** of personal × outer hard aspects: Conjunction, Square, Opposition for personal planets × Uranus/Neptune/Pluto (60 entries)
- **~58%** of all 330 possible planet × aspect combinations overall
- Remaining combinations (outer × outer; personal × outer harmonics) fall back to a generic aspect-type explanation that describes what a Square, Trine, Sextile, etc. means in plain language

All interpretations are plain-language psychological prose — jargon is always explained. Sign names are translated in French and Italian. Planet names are translated in French and Italian.

### LLM mode

Connect any of the following providers for AI-generated reports:

| Provider | Notes |
|---|---|
| **Anthropic** | API key required; recommended model `claude-opus-4-5` |
| **OpenAI** | API key required; recommended model `gpt-4o` |
| **Google Gemini** | API key required; recommended model `gemini-2.0-flash` |
| **Ollama** | Local, no API key; run `OLLAMA_ORIGINS=* ollama serve`; recommended model `llama3` |

In LLM mode, all planet positions, aspects, dignities, element balance, and lunar phase are sent as pre-computed, annotated data. The LLM is instructed to interpret — not recalculate — and to write in plain psychological language for a general audience. Each placement's astrological meaning is included in the prompt, anchoring the LLM to consistent vocabulary. The LLM's self-reported confidence is parsed from a structured JSON block appended to each response and displayed in the Confidence Index.

---

## Confidence Index

Every output includes a Confidence Index that measures the reliability of the calculations and interpretation, not the strength of the astrological relationship.

**Natal mode metrics:**
- **Astronomical Precision** — penalised for outer planet simplified formulas
- **Birth Time** — 100% if known; 55% if unknown (Moon ±6°, Ascendant unavailable)
- **Dignity Reliability** — reduced if outer-planet dignities are present (generational, not personal)
- **Retrograde Reliability** — reduced if slow-planet retrogrades are detected (directional accuracy is reliable; noted for completeness)
- **Oracle Assessment** — LLM self-reported confidence (LLM mode only)

**Synastry mode metrics:**
- **Astronomical Precision** — penalised for unknown birth times and tight outer-planet aspects
- **Aspect Coverage** — found aspects as a percentage of 121 possible pairs
- **Domain Coherence** — low variance across the 5 domain scores = consistent picture
- **Oracle Assessment** — LLM self-reported confidence (LLM mode only)

---

## Languages

The full interface and all generated content (built-in interpreter reports, section headings, tooltips, confidence flags, sign names, planet names, aspect descriptions, dignity explanations, retrograde meanings, lunar phase names) are available in:

- 🇬🇧 English
- 🇫🇷 French
- 🇮🇹 Italian

Language can be switched at any time from the top-right selector. Built-in reports re-render immediately in the new language.

---

## City search

Birth city lookup uses the [open-meteo Geocoding API](https://geocoding-api.open-meteo.com) — free, no API key required. City selection automatically populates the UTC offset and latitude used for Ascendant calculation.

If birth time is unknown, city selection is still used for latitude (which affects several planetary calculations). Check the "Birth time unknown" box to indicate this.

---

## Architecture

The entire application is a **single HTML file** (~3,450 lines). There are no build tools, no npm packages, no external JavaScript files, and no backend. Everything — astronomical engine, interpretation rules, UI, i18n — is embedded inline.

```
synastria-v10.html
├── CSS (inline <style>)
├── HTML structure
└── JavaScript (inline <script>)
    ├── Astronomical engine
    │   ├── VSOP87 series coefficients
    │   ├── Planetary position functions
    │   ├── Chart builder (buildChart)
    │   ├── Natal profile (buildNatalProfile)
    │   └── Synastry builder (buildSynastry, scoreSyn)
    ├── Interpretation engine
    │   ├── Built-in natal report (builtinNatalReport)
    │   ├── Built-in synastry report (builtinReport)
    │   ├── LLM prompt builders
    │   └── ASP_PAIR_INTERP lookup table (192 bespoke entries, 3 languages)
    ├── Confidence engine
    │   ├── computeNatalConf
    │   └── computeConf (synastry)
    ├── UI / rendering
    │   ├── Calendar widget
    │   ├── City search (open-meteo API)
    │   ├── Collapsible panels
    │   └── Output renderers
    └── i18n (EN / FR / IT)
```

---

## Privacy

- All astronomical calculations happen **entirely in your browser** — no birth data is ever sent to any server by the app itself
- City search sends only the typed city name to the open-meteo geocoding API (no birth data)
- If an LLM provider is configured, the computed chart data (planet positions, aspects, scores) is sent to that provider's API along with the interpretation request — **no raw birth dates or times are transmitted**, only derived astronomical data
- API keys are stored only in the browser session (in-memory input field) and are never persisted

---

## Astrological approach

Synastria uses **Western tropical astrology** throughout:

- The zodiac is anchored to the vernal equinox (tropical, not sidereal)
- House system: Ascendant only (whole-sign interpretation implied); no house cusps are computed
- Essential dignities: domicile, exaltation, detriment, fall for all 10 planets
- Aspects: Conjunction (8° orb), Sextile (6°), Square (8°), Trine (8°), Quincunx (3°), Opposition (8°)
- Synastry scoring uses a weighted aspect model across 5 domains with 86 pair-weight entries

The interpretations are written for a general audience — every astrological term is explained in plain psychological language, and readers are not expected to know any astrology to understand the output.
