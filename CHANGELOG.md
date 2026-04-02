# Changelog

All notable changes to Synastria are documented in this file.

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
