import pytest
import re

from tests.helpers.engine import START_MARKER, END_MARKER

pytestmark = pytest.mark.structural


def test_engine_block(html_path, engine_js):
    html = html_path.read_text(encoding='utf-8')
    assert START_MARKER in html, f"'{START_MARKER}' not found in HTML"
    assert END_MARKER in html, f"'{END_MARKER}' not found in HTML"
    assert len(engine_js) > 1000, f"Engine too short: {len(engine_js):,} chars"


@pytest.mark.parametrize("fn", [
    'function sunPos', 'function moonPos', 'function vsopGeoLon',
    'function outerGeoLon', 'function planetPos', 'function buildChart',
    'function buildSynastry', 'function scoreSyn', 'function computeConf',
    'function getAspect', 'function degSign', 'function ascPos',
    'function helioXY', 'function kepler', 'function vsopLBR',
    'function jupPert', 'function satPert',
    'const toJD', 'const toT', 'const m360',
    'const VSOP', 'const SECULAR', 'const ASPECTS',
    'const ZSIGNS', 'const ZSYMS', 'const SLOW_P', 'const SW', 'const SD',
])
def test_core_functions(engine_js, fn):
    assert fn in engine_js, f"Missing: {fn}"


@pytest.mark.parametrize("body", ['Mercury', 'Venus', 'Earth', 'Mars'])
def test_vsop87_data(engine_js, body):
    assert f"'{body}'" in engine_js, f"VSOP87 data for {body} not found"


def test_city_search_api(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'geocoding-api.open-meteo.com' in html


def test_city_time_unknown_i18n(html_path):
    html = html_path.read_text(encoding='utf-8')
    n_ctu = html.count('cityTimeUnknown')
    assert n_ctu >= 3, f"cityTimeUnknown: {n_ctu} occurrences (expected >= 3)"


def test_no_hardcoded_llmscore_fallback(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'llmScore??70' not in html
    assert 'llmScore ?? 70' not in html


def test_version_badge(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'ver-badge">v10.2.0' in html


def test_buildchart_returns_time_unknown(engine_js):
    assert re.search(r'return\{JD,T,pos,trace,timeUnknown', engine_js)


def test_aspects_table_6_entries(engine_js):
    n_asp = len(re.findall(r'\{name:', engine_js))
    assert n_asp == 6, f"ASPECTS table has {n_asp} entries (expected 6)"


def test_sw_weight_table_size(engine_js):
    sw_keys = re.findall(r"'[A-Za-z]+-[A-Za-z]+':", engine_js)
    assert len(sw_keys) >= 80, f"SW weight table has {len(sw_keys)} keys (expected >= 80)"


@pytest.mark.parametrize("domain", ['love', 'harmony', 'passion', 'mental', 'karmic'])
def test_sd_domain_defined(engine_js, domain):
    assert re.search(r'\b' + domain + r'\s*:', engine_js), f"SD domain '{domain}' not found"


def test_computeconf_formula_coefficients(engine_js):
    assert '.45' in engine_js, "Missing .45 coefficient"
    assert '.25' in engine_js, "Missing .25 coefficient"
    assert '.30' in engine_js, "Missing .30 coefficient"


# ── v10 natal profile additions ───────────────────────────────────────────────
@pytest.mark.parametrize("fn", [
    'function buildNatalAspects', 'function buildNatalProfile',
    'function lunarPhase', 'function elementTally', 'function modalityTally',
    'function dignityScores', 'function retrogradeFlags',
    'function builtinNatalReport', 'function buildNatalPrompt',
    'const ELEM_MAP', 'const MOD_MAP', 'const DIGNITY', 'const PHASE_NAMES',
])
def test_natal_profile_functions(engine_js, html_path, fn):
    html = html_path.read_text(encoding='utf-8')
    assert fn in engine_js or fn in html, f"Missing: {fn}"


@pytest.mark.parametrize("planet", [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
])
def test_dignity_table_entries(engine_js, planet):
    assert f"'{planet}'" in engine_js or f"{planet}:" in engine_js, \
        f"DIGNITY has no entry for {planet}"


@pytest.mark.parametrize("lang", ['en', 'fr', 'it'])
def test_phase_names_languages(engine_js, lang):
    assert re.search(r'\bPHASE_NAMES\b.*?' + lang + r'\s*:', engine_js, re.DOTALL), \
        f"PHASE_NAMES missing '{lang}' key"


@pytest.mark.parametrize("key", ['soloOnlyMsg', 'natalProfileBox', 'natalSystemPrompt', 'soloTitle'])
def test_natal_i18n_keys(html_path, key):
    html = html_path.read_text(encoding='utf-8')
    n = html.count(key)
    assert n >= 3, f"i18n key '{key}': {n} occurrences (expected >= 3)"


@pytest.mark.parametrize("sign", [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
])
def test_elem_map_covers_sign(engine_js, sign):
    assert re.search(sign + r"\s*:", engine_js), f"ELEM_MAP missing {sign}"


def test_buildnatalprofile_returns_aspects(engine_js):
    assert 'aspects:' in engine_js and 'buildNatalAspects' in engine_js


def test_buildnatalprofile_returns_retrogrades(engine_js):
    assert 'retrogrades:' in engine_js and 'retrogradeFlags' in engine_js


def test_buildnatalprofile_returns_lunar_phase(engine_js):
    assert 'lunarPhase:' in engine_js and 'lunarPhase(' in engine_js


def test_solo_mode_detection(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'soloMode' in html


@pytest.mark.parametrize("key", [
    'soloOnlyMsg', 'natalSystemPrompt', 'soloTitle',
    'natalOracleReport', 'natalDataTitle', 'natalProfileBox',
])
def test_solo_i18n_keys(html_path, key):
    html = html_path.read_text(encoding='utf-8')
    n = html.count(key)
    assert n >= 3, f"i18n key '{key}': {n} occurrences (expected >= 3)"


def test_solo_notice_element(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'solo-notice' in html


@pytest.mark.parametrize("element_id", [
    'natal-report-A-sec', 'natal-data-A-sec',
    'natal-report-B-sec', 'natal-data-B-sec',
])
def test_natal_split_boxes(html_path, element_id):
    html = html_path.read_text(encoding='utf-8')
    assert element_id in html, f"{element_id} not found in HTML"


def test_call_llm_with_system_defined(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'function callLLMWithSystem' in html


def test_rerender_natal_builtin_defined(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'function rerenderNatalBuiltin' in html
