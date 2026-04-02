# Changelog

All notable changes to Synastria are documented in this file.

---

## [10.2.0] — 2026-04-02

### Added
- **Reset button** — clears all inputs (names, dates, times, cities), outputs, and internal state back to initial values; scrolls to top. Styled in rose to match the cosmic theme.
- **Export PDF button** — appears after a calculation completes. Expands all collapsed sections, triggers the browser print dialog with a dedicated `@media print` stylesheet: white background, no truncation, `page-break-inside: avoid` on all panels, all tabs rendered at once, SVG rings and gauges preserve colors. Styled in azure.
- I18N labels for both buttons in English, French, and Italian.
- Responsive layout: buttons stack vertically on mobile.

### Fixed
- **OpenAI GPT-5 compatibility** — replaced deprecated `max_tokens` parameter with `max_completion_tokens` in both `callLLM()` and `callLLMWithSystem()`. GPT-5 series models reject the old parameter, causing API errors. GPT-4o remains compatible with the new parameter.

### Changed
- Default model placeholders updated: OpenAI `gpt-4o` → `gpt-5.4`, Anthropic `claude-opus-4-5` → `claude-sonnet-4-6`.

---

## [10.1.0] — 2026-04-02

### Fixed
- **Ascendant calculation** — corrected a bug in the ascendant position computation that produced incorrect results in certain latitude/longitude combinations. Multiple iterations of fixes applied and verified.

---

## [10.0.0] — 2026-04-02

### Added
- Initial public release of Synastria v10.
- **Solo mode (Natal Profile)** — full natal chart for one person: 10 planets + Ascendant, natal aspects, lunar phase (8 phases), elemental and modality balance, essential dignities (domicile, exaltation, detriment, fall), retrograde detection.
- **Duo mode (Synastry)** — relationship compatibility analysis: 11x11 synastry grid (121 planet pairs), weighted scoring across 6 domains (Overall, Love, Passion, Harmony, Mental, Karmic), compatibility categories (Stellar Union through Deep Tension).
- **Astronomy engine** — VSOP87 for inner planets, secular elements + perturbation terms for outer planets, Brown 16-term Moon series, Kepler solver, Ascendant via GMST/LST/obliquity. JPL Horizons-validated across 1950-2050.
- **Built-in interpreter** — 192 bespoke planet-pair interpretations covering 100% of personal planet combinations and ~58% of all possible pairings, with generic aspect-type fallbacks.
- **LLM integration** — optional oracle reports via Anthropic, OpenAI, Google Gemini, or local Ollama. Structured prompts with pre-computed data; LLM interprets, never recalculates.
- **Confidence Index** — weighted composite score (astronomical precision, aspect coverage, domain coherence, optional LLM self-assessment) with diagnostic flags for uncertainty sources.
- **Calculation traces** — full transparency: every intermediate step (JD, T, formulas, results) exposed in tabbed trace tables.
- **Trilingual UI** — complete English, French, and Italian support for all labels, tooltips, interpretations, and oracle prompts.
- **City geocoding** — autocomplete search via open-meteo API with timezone and DST-aware offset detection.
- **Custom calendar picker** — date input with day/month/year views and DD/MM/YYYY text entry.
- **Zero dependencies** — single HTML file, no build step, no frameworks, works offline.
- **Privacy-first** — all calculations local; only optional city geocoding and LLM API calls leave the browser.
- **Animated cosmic UI** — dark theme with starfield canvas, gold accents, serif typography (Cinzel, Cormorant Garamond, EB Garamond), SVG score rings and confidence gauge.
- **Comprehensive test suite** (`test_synastria_v10.py`) — structural tests, ~100 unit tests, ~130 JPL Horizons validation queries with caching.
