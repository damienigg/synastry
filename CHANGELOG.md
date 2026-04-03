# Changelog

All notable changes to Synastria are documented in this file.

---

## [10.5.0] — 2026-04-03

### Added
- **Neptune JPL-fitted perturbation** — custom perturbation term fitted against 88 JPL Horizons positions (1920-2050) using greedy Fourier regression (`scripts/fit_neptune_pert.py`). Identified the Neptune-Uranus 2:1 near-resonance (argument 2L♆−L♅) as the dominant gravitational interaction. Reduces Neptune RMS error from 0.67° to 0.03° (max residual 0.08°). Neptune tolerance tightened from 1.0° to 0.5°.
- **Uranus perturbation terms** — 7-term Saturn-Uranus-Neptune perturbation from Meeus Ch.36. Improves Uranus accuracy by ~0.5° across 1920-2050.
- **Full calculation trace transparency** — all 16 Moon Brown series terms shown individually, Moon fundamental arguments (D, M, M', F) with T² terms, inner planet VSOP87 heliocentric coordinates, outer planet Kepler elements (L, M, E, v) and perturbation values, UTC offset as explicit trace row, Sun M and Sun C formulas fully expanded.
- **In-app trilingual help modal** — Guide, Astrology, and About tabs with full EN/FR/IT translations via the I18N system. Includes per-planet accuracy tables. Opens as overlay (no navigation), closes via button/ESC/click-outside. Re-renders on language switch.
- **`scripts/fit_neptune_pert.py`** — Neptune perturbation fitting script.
- **`scripts/clean.sh`** — removes `__pycache__`, `.pytest_cache`, test reports, and optionally `.jpl_cache.json`.

### Changed
- **Consolidated translation tables** — `SIGN_TR`, `PLANET_TR`, `ELEM_TR`, `MOD_TR`, `ASP_VERB` extracted to module-level constants with shared helper functions (`trSign`, `trPlanet`, `trElem`, `trMod`, `trAspVerb`). Removes 6 duplicate definitions.
- **Optimized synastry scoring** — pre-built `SD_MAP` (Map) replaces `Array.includes()` loop for O(1) domain lookup.
- **CSS chip consolidation** — aspect chip classes use CSS custom properties instead of repeating declarations.
- **Solo mode** — Calculation Traces now shows only the Natal Charts tab; synastry/scores/raw tabs hidden. Stale content from prior dual-mode runs is cleared.
- **`bump_version.py`** moved to `scripts/` folder.
- Removed dead `vsopGeoLon`/`outerGeoLon`/`helioXY` functions (inlined into `planetPos` for richer trace data).
- Fixed `elementTally` side-effect expression that mutated `ELEM_MAP`.

### Fixed
- **Multilingual interpolation bugs** — calculated variables (element names, zodiac signs, modalities, planet names, aspect verbs) were rendered in English inside French and Italian sentences. Affected both the synastry report (`builtinReport`) and the natal report (`builtinNatalReport`). All interpolated variables now pass through language-aware translators:
  - Element names: Fire→Feu/Fuoco, Water→Eau/Acqua, Earth→Terre/Terra, Air→Air/Aria
  - Zodiac signs: Aries→Bélier/Ariete, Taurus→Taureau/Toro, etc.
  - Modalities: Fixed→Fixe/Fisso, Mutable→Mutable/Mutevole, Cardinal→Cardinal/Cardinale
  - Planet names: Venus→Vénus/Venere, Saturn→Saturne/Saturno, etc.
  - Aspect verbs: conjunct→conjonction/congiunzione, trine→trigone/trigono, etc.

---

## [10.4.0] — 2026-04-03

### Added
- **100% interpretation coverage** — all 55 planet-pair × 6 aspect combinations now have bespoke, psychologically-grounded interpretations in English, French, and Italian. Total: 990 entries (was 567 at 57% coverage). The generic aspect fallback is no longer needed.
- **New planet pairs added:** Ascendant-Uranus, Jupiter-Mercury, Neptune-Venus, Pluto-Saturn, Pluto-Uranus, Pluto-Venus, Uranus-Venus (all 6 aspects × 3 languages = 126 entries), plus Trine/Sextile/Quincunx for 15 previously incomplete pairs (45 entries × 3 languages = 135 entries), plus 9 fully new outer-planet pairs (54 entries × 3 languages = 162 entries).
- **Test suite enrichment** — 5 new edge-case tests (leap year, 1920/2050 boundaries, midnight UTC, extreme timezones), 3 Moon reference values vs JPL, 3 timezone unit tests, 4 synastry domain range checks, 4 new extreme-latitude ascendant cases (Tromso 69.6°N, Reykjavik 64.1°N, Cape Town, Singapore). Total: 540 tests.

### Removed
- **All LLM functionality** — removed Anthropic, OpenAI, Gemini, and Ollama integrations entirely. No more Oracle Configuration panel, API key fields, provider selection, system prompts, or LLM confidence scoring. The app now runs purely on the built-in interpreter (~360 lines of code removed).
- Removed `callLLM()`, `callLLMWithSystem()`, `buildPrompt()`, `buildNatalPrompt()`, `extractJson()`, `stripJson()`, `updateProviderUI()`, `curProvider` global.
- Removed ~60 I18N keys across 3 languages (LLM labels, tooltips, system prompts, confidence descriptions).
- Removed LLM-specific CSS (.pills, .pill, .llm-grid, .llmcard).

### Changed
- Confidence engine simplified: no longer includes LLM self-assessment weighting. Synastry formula now uses astronomical precision (45%), aspect coverage (25%), domain coherence (30%). Natal formula uses astronomical precision (35%), birth time (40%), dignity reliability (15%), retrograde reliability (10%).

---

## [10.3.0] — 2026-04-02

### Added
- **pytest-based test suite** — complete restructure from monolithic `tests.py` into modular `tests/` folder:
  - `tests/test_structural.py` — 105 HTML/engine inspection tests
  - `tests/test_unit.py` — 265 batch unit tests via single Node.js invocation
  - `tests/test_jpl.py` — 142 parametrized JPL Horizons validation tests
  - `tests/test_ascendant.py` — 13 Swiss Ephemeris ascendant validation tests
  - `tests/helpers/` — shared infrastructure (engine extraction, Node runner, JPL client)
  - `tests/conftest.py` — session-scoped fixtures, custom CLI options, report plugin
- **Swiss Ephemeris ascendant validation** — 13 test cases comparing app output against Kerykeion/pyswisseph (JPL DE431, ±0.001° accuracy). All pass within 0.01°. Covers equator, mid/high latitudes, southern hemisphere, and 1950-2020 date range.
- **planetPos reference value tests** — all 8 planets at J2000 validated against JPL Horizons data, not just range checks.
- **Configurable tolerances** — `tolerances.json` file at project root controls JPL/SwissEph comparison thresholds per planet. Falls back to built-in defaults if missing.
- **Test report logging** — every test run saves a timestamped plain-text report to `reports/`.
- `requirements.txt` and `pyproject.toml` for proper dependency management.

### Changed
- Test suite now uses pytest with markers (`structural`, `unit`, `jpl`, `ascendant`) instead of custom argparse CLI.
- Replaced `--suite` flags with `pytest -m <marker>` and `--no-jpl` / `--clear-cache` custom options.

### Fixed
- **Critical: ascPos test shim argument mismatch** — tests were calling `ascPos(T, hour, tz, lat)` instead of `ascPos(T, lat, lon)`. Tests never actually validated the ascendant with correct coordinates. This is why the v10.1.0 ascendant bug was not caught.
- **buildChart shims missing lon parameter** — all test shims (buildChart, buildSynastry, scoreSyn, computeConf, natal profile functions) now correctly pass geographic longitude.
- **builtinNatalReport args misordered** — language parameter was being interpreted as longitude.

### Removed
- Monolithic `tests.py` replaced by `tests/` folder.

---

## [10.2.0] — 2026-04-02

### Added
- **Reset button** — clears all inputs, outputs, and state; scrolls to top. Rose-themed.
- **Export PDF button** — expands all collapsed sections, triggers browser print with `@media print` stylesheet (white background, no truncation, page-break-inside: avoid). Azure-themed.
- I18N labels for both buttons in English, French, and Italian.
- Responsive layout: buttons stack vertically on mobile.

### Fixed
- **OpenAI GPT-5 compatibility** — replaced deprecated `max_tokens` with `max_completion_tokens` in both LLM call functions. GPT-5 series rejects the old parameter.

### Changed
- Default model placeholders: OpenAI `gpt-4o` → `gpt-5.4`, Anthropic `claude-opus-4-5` → `claude-sonnet-4-6`.

---

## [10.1.0] — 2026-04-02

### Fixed
- **Ascendant calculation** — corrected a bug in the ascendant position computation that produced incorrect results in certain latitude/longitude combinations.

---

## [10.0.0] — 2026-04-02

### Added
- Initial public release of Synastria v10.
- **Solo mode (Natal Profile)** — full natal chart: 10 planets + Ascendant, natal aspects, lunar phase, elemental/modality balance, essential dignities, retrograde detection. 9-section oracle report.
- **Duo mode (Synastry)** — 11x11 synastry grid (121 planet pairs), weighted scoring across 6 domains (Overall, Love, Passion, Harmony, Mental, Karmic), compatibility categories.
- **Astronomy engine** — VSOP87 for inner planets, secular elements + perturbation terms for outer planets, Brown 16-term Moon series, Kepler solver, Ascendant via GMST/LST/obliquity. JPL Horizons-validated across 1950-2050.
- **Built-in interpreter** — 192 bespoke planet-pair interpretations, ~58% of all possible pairings, with generic aspect-type fallbacks.
- **LLM integration** — Anthropic, OpenAI, Google Gemini, Ollama.
- **Confidence Index** — weighted composite with diagnostic flags.
- **Calculation traces** — full transparency of every intermediate step.
- **Trilingual UI** — English, French, Italian.
- **Zero dependencies** — single HTML file, works offline.
