# Synastria v10.4.1

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

No internet connection is required for calculation or interpretation. Internet is used only for city search (Open-Meteo geocoding API).

---

## Astronomy engine

Planetary positions are computed entirely in JavaScript, client-side, using classical algorithms from *Astronomical Algorithms* (Jean Meeus, 2nd ed.).

| Component | Method | Verified accuracy |
|---|---|---|
| Sun | VSOP87 geometric mean + aberration | ≤ 0.5° vs JPL |
| Moon | Brown 16-term simplified series | ≤ 0.1° vs JPL |
| Mercury, Venus, Mars | VSOP87 truncated L/B/R, heliocentric → geocentric | ≤ 0.5° vs JPL |
| Jupiter, Saturn | Secular elements + mutual perturbation terms | ≤ 2-3° vs JPL |
| Uranus | Secular elements + Saturn-Neptune perturbation terms | ≤ 1.5° vs JPL |
| Neptune, Pluto | Secular elements (Meeus Table 31.b) | ≤ 2° vs JPL |
| Ascendant | GMST + obliquity + latitude | ≤ 0.01° vs Swiss Ephemeris |

All accuracy figures are verified by the automated test suite against JPL Horizons (1920-2050) and Swiss Ephemeris (Kerykeion/pyswisseph, JPL DE431). Position errors for outer planets rarely affect sign placement (signs are 30° wide); they matter only for tight aspects (orb ≤ 2°), which the Confidence Index flags.

Retrograde detection uses a 1-day finite difference. Direction detection is reliable even for outer planets — positional uncertainty (≤ 2°) is orders of magnitude larger than daily motion (~0.01-0.04°/day), but the sign of the motion is unaffected.

---

## Interpretation engine

Rule-based interpreter with **100% coverage** — all 330 possible planet-pair × aspect combinations have bespoke, psychologically-grounded interpretations in all 3 languages (990 entries total). No generic fallbacks needed.

| Coverage | Count |
|---|---|
| Planet pairs | 55/55 (all combinations of 11 celestial points) |
| Aspects per pair | 6 (Conjunction, Trine, Sextile, Square, Opposition, Quincunx) |
| Interpretations per language | 330 |
| Total across EN/FR/IT | 990 |

Each interpretation is:
- **Psychologically grounded** — describes how the aspect manifests in behavior, emotions, and relationships
- **Plain language** — no unexplained jargon, readable by anyone
- **Aspect-specific** — each aspect type has distinct meaning (merging, flow, opportunity, friction, polarity, adjustment)

Additional interpretation data:
- 12 Sun sign descriptions × 3 languages
- 12 Moon sign descriptions × 3 languages
- 12 Ascendant sign descriptions × 3 languages
- 10 planet dignity interpretations (domicile, exaltation, detriment, fall) × 3 languages
- 8 lunar phase names × 3 languages

No external API or internet connection is needed for interpretation. Everything runs locally.

---

## Confidence Index

Every output includes a Confidence Index measuring calculation reliability, not relationship strength. Only warnings are shown — no "everything OK" clutter.

**Natal:** Astronomical Precision (45%) + Birth Time (55%)

**Synastry:** Astronomical Precision (50%) + Domain Coherence (50%)

Warnings appear only when relevant: unknown birth time, tight outer-planet aspects (orb ≤2°), high domain variance.

---

## Test suite

The project includes a comprehensive pytest-based test suite validated against authoritative external sources.

### Quick start

```bash
pip install -r requirements.txt
pytest -v                          # run all 540 tests
pytest -m structural               # HTML/engine inspection tests
pytest -m unit                     # unit tests (single Node.js batch)
pytest -m jpl                      # JPL Horizons validation tests
pytest -m ascendant                # Swiss Ephemeris ascendant tests
pytest --no-jpl                    # skip external API tests
pytest --clear-cache               # clear JPL response cache
```

### What's tested

| Category | Tests | Reference | Tolerance |
|---|---|---|---|
| Structural (HTML/engine) | ~100 | Static inspection | N/A |
| Unit (all engine functions) | ~275 | Self-consistent + JPL refs | Various |
| Edge cases | 5 | Leap year, boundaries, timezones | N/A |
| JPL Horizons (planet positions) | 142 | JPL DE441 | 0.5°-3° per planet |
| Swiss Ephemeris (ascendant) | 17 | JPL DE431 via Kerykeion | 2° (actual max: 0.01°) |

Tolerances are configurable in `tolerances.json`.

### Requirements

- Python 3.9+
- Node.js 14+ (for executing the extracted JS engine)
- `pytest >= 8.0`
- `kerykeion >= 4.0` (Swiss Ephemeris bindings, for ascendant validation)

---

## Scripts

```bash
python3 scripts/bump_version.py            # show current version
python3 scripts/bump_version.py patch      # 10.4.1 → 10.4.2
python3 scripts/bump_version.py minor      # 10.4.1 → 10.5.0
python3 scripts/bump_version.py major      # 10.4.1 → 11.0.0
python3 scripts/bump_version.py 10.5.0     # set explicit version

bash scripts/clean.sh                      # remove caches and test reports
bash scripts/clean.sh --all                # also remove .jpl_cache.json
```

---

## Languages

Full interface and all generated content available in:

- English
- French
- Italian

Language can be switched at any time. Built-in reports re-render immediately.

---

## Architecture

The application is a **single HTML file** (~3,700 lines). No build tools, no npm, no backend, no external APIs for interpretation.

```
synastry/
├── index.html               # the entire application (CSS + HTML + JS)
├── CHANGELOG.md             # version history
├── VERSION.md               # current version
├── README.md
├── tolerances.json          # JPL/Swiss Ephemeris comparison thresholds
├── requirements.txt         # Python test dependencies
├── pyproject.toml           # pytest configuration
├── .gitignore
├── scripts/
│   ├── bump_version.py      # version management utility
│   └── clean.sh             # remove caches and temp files
└── tests/
    ├── conftest.py           # session fixtures, CLI options, report plugin
    ├── test_structural.py    # HTML/engine structural inspection
    ├── test_unit.py          # batch engine tests via Node.js
    ├── test_edge_cases.py    # date/timezone/boundary edge cases
    ├── test_jpl.py           # JPL Horizons planet validation
    ├── test_ascendant.py     # Swiss Ephemeris ascendant validation
    └── helpers/
        ├── engine.py         # extract_engine(), JS shims
        ├── node_runner.py    # find_node(), run_node()
        ├── jpl.py            # JPL client, cache, tolerances
        └── formatting.py     # ANSI color helpers
```

### Inside index.html

```
index.html
├── CSS (inline <style>)
│   └── @media print stylesheet for PDF export
├── HTML structure
│   ├── Input panel (birth data, city search, calendar picker)
│   ├── Results (reports, confidence, traces)
│   └── Action buttons (Reset, Export PDF)
└── JavaScript (inline <script>)
    ├── I18N (EN/FR/IT — all labels, tooltips, interpretations)
    ├── Astronomy engine (VSOP87, Brown, secular elements, Kepler)
    ├── Natal profile (aspects, dignities, retrogrades, lunar phase)
    ├── Synastry engine (pair matrix, weighted scoring, 5 domains)
    ├── Interpretation engine (990 bespoke entries, 100% coverage)
    ├── Confidence engine (natal + synastry composite scores)
    └── UI (calendar, city search, collapsible panels, SVG rings)
```

---

## Privacy

- All calculations and interpretations happen **entirely in your browser** — no birth data is ever sent to any server
- City search sends only the typed city name to Open-Meteo (no birth data)
- No external APIs are used for interpretation — everything is built-in
- The app works fully offline (except for city geocoding)

---

## Astrological approach

Synastria uses **Western tropical astrology**:

- Zodiac anchored to the vernal equinox (tropical, not sidereal)
- House system: Ascendant only (whole-sign implied); no house cusps computed
- Essential dignities: domicile, exaltation, detriment, fall for all 10 planets
- Aspects: Conjunction (8°), Sextile (6°), Square (8°), Trine (8°), Quincunx (3°), Opposition (8°)
- Synastry scoring: weighted aspect model across 5 domains with 86 pair-weight entries

Interpretations are written for a general audience — every astrological term is explained in plain psychological language.
