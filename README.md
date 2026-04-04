# Synastria v10.6.2

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

Planetary positions are computed entirely in JavaScript, client-side, using secular orbital elements from *Astronomical Algorithms* (Jean Meeus, 2nd ed.) with **custom perturbation corrections fitted against JPL Horizons data**.

| Component | Method | Verified accuracy |
|---|---|---|
| Sun | VSOP87 geometric mean + aberration | ≤ 0.5° vs JPL |
| Moon | Brown 16-term simplified series | ≤ 0.1° vs JPL |
| Mercury, Venus, Mars | VSOP87 truncated L/B/R, heliocentric → geocentric | ≤ 0.5° vs JPL |
| Jupiter | Secular elements + JPL-fitted perturbation (7 terms) | ≤ 0.25° vs JPL |
| Saturn | Secular elements + JPL-fitted perturbation (8 terms) | ≤ 0.25° vs JPL |
| Uranus | Secular elements + JPL-fitted perturbation (4 terms) | ≤ 0.12° vs JPL |
| Neptune | Secular elements + JPL-fitted perturbation (1 term) | ≤ 0.09° vs JPL |
| Pluto | Secular elements + JPL-fitted perturbation (5 terms) | ≤ 0.17° vs JPL |
| Ascendant | GAST (nutation-corrected) + Laskar obliquity | ≤ 0.01° vs Swiss Ephemeris (≤ 0.64° at extreme latitudes) |

All accuracy figures are verified by the automated test suite against 88 JPL Horizons positions per planet spanning 1920-2050 (total: 440+ reference points), plus Swiss Ephemeris for the Ascendant. All outer planets now achieve ≤ 0.25° accuracy — well within the 0.5° test tolerance.

### JPL-fitted perturbation corrections

The original Meeus perturbation terms were fitted to different secular elements and epochs. When applied to our Meeus Table 31.b elements, they actually **worsened** accuracy for Jupiter (+0.13° RMS increase) and Saturn (+0.48° increase). We replaced all outer-planet perturbations with custom terms fitted directly against JPL Horizons data using greedy Fourier regression.

Each planet has its own fitting script (`scripts/fit_<planet>_pert.py`) that:
1. Queries JPL Horizons for 88 geocentric ecliptic longitudes (every 3 years, 1920-2050)
2. Computes residuals against the unperturbed secular formula
3. Fits Fourier terms from a pool of candidate angular arguments (mean longitude combinations)
4. Selects terms greedily by maximum RMS reduction, stopping when improvement < 0.001°

The dominant term across all outer planets is **2L♆−L♅** — the Neptune-Uranus 2:1 near-resonance, the strongest gravitational interaction in the outer solar system.

| Planet | No pert (RMS) | Meeus (RMS) | JPL-fitted (RMS) | Max error | Terms |
|---|---|---|---|---|---|
| Jupiter | 0.49° | 0.62° (worse) | **0.07°** | 0.24° | 7 |
| Saturn | 0.82° | 1.30° (worse) | **0.07°** | 0.25° | 8 |
| Uranus | 1.18° | 1.04° | **0.05°** | 0.11° | 4 |
| Neptune | 0.67° | — | **0.03°** | 0.08° | 1 |
| Pluto | 1.09° | — | **0.05°** | 0.17° | 5 |

Retrograde detection uses a 1-day finite difference. Direction detection is reliable even for outer planets — positional uncertainty is orders of magnitude larger than daily motion (~0.01-0.04°/day), but the sign of the motion is unaffected.

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

python3 scripts/fit_jupiter_pert.py        # fit Jupiter perturbation from JPL data
python3 scripts/fit_saturn_pert.py         # fit Saturn perturbation
python3 scripts/fit_uranus_pert.py         # fit Uranus perturbation
python3 scripts/fit_neptune_pert.py        # fit Neptune perturbation
python3 scripts/fit_pluto_pert.py          # fit Pluto perturbation
# All accept --no-fetch to refit using cached JPL data only
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
│   ├── clean.sh             # remove caches and temp files
│   ├── secular.py           # shared secular-element computation for fitting scripts
│   ├── fit_jupiter_pert.py  # fit Jupiter perturbation from JPL Horizons data
│   ├── fit_saturn_pert.py   # fit Saturn perturbation
│   ├── fit_uranus_pert.py   # fit Uranus perturbation
│   ├── fit_neptune_pert.py  # fit Neptune perturbation
│   └── fit_pluto_pert.py    # fit Pluto perturbation
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
