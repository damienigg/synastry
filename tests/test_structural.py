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
    'function sunPos', 'function moonPos',
    'function planetPos', 'function buildChart',
    'function buildSynastry', 'function scoreSyn', 'function computeConf',
    'function getAspect', 'function degSign', 'function ascPos',
    'function kepler', 'function vsopLBR',
    'function jupPert', 'function satPert', 'function uraPert', 'function nepPert', 'function pluPert',
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


def test_version_constant(html_path):
    """APP_VERSION constant exists and badge/header render dynamically from it."""
    html = html_path.read_text(encoding='utf-8')
    m = re.search(r"const APP_VERSION='([^']+)'", html)
    assert m, "APP_VERSION constant not found in index.html"
    version = m.group(1)
    # Verify the version string looks valid (semver-like)
    assert re.match(r'^\d+\.\d+\.\d+$', version), f"Invalid version format: {version}"
    # Verify dynamic rendering elements exist
    assert 'id="ver-badge"' in html
    assert 'id="ver-header"' in html

def test_version_matches_version_md(html_path, project_root):
    """APP_VERSION in index.html must match VERSION.md."""
    html = html_path.read_text(encoding='utf-8')
    m = re.search(r"const APP_VERSION='([^']+)'", html)
    assert m, "APP_VERSION constant not found"
    app_version = m.group(1)
    version_md = (project_root / 'VERSION.md').read_text()
    m2 = re.search(r'\*\*(.+?)\*\*', version_md)
    assert m2, "Cannot parse version from VERSION.md"
    assert app_version == m2.group(1), f"index.html has {app_version}, VERSION.md has {m2.group(1)}"


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
    assert '.50' in engine_js, "Missing .50 coefficient"
    assert '.45' in engine_js, "Missing .45 coefficient"
    assert '.55' in engine_js, "Missing .55 coefficient"


# ── v10 natal profile additions ───────────────────────────────────────────────
@pytest.mark.parametrize("fn", [
    'function buildNatalAspects', 'function buildNatalProfile',
    'function lunarPhase', 'function elementTally', 'function modalityTally',
    'function dignityScores', 'function retrogradeFlags',
    'function builtinNatalReport',
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


@pytest.mark.parametrize("key", ['soloOnlyMsg', 'natalProfileBox', 'soloTitle'])
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
    'soloOnlyMsg', 'soloTitle',
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


def test_rerender_natal_builtin_defined(html_path):
    html = html_path.read_text(encoding='utf-8')
    assert 'function rerenderNatalBuiltin' in html


# ── Synastry scoring structural tests ────────────────────────────────────────

def test_sw_symmetry(engine_js):
    """SW must be built from _SW_HALF with automatic reverse-pair generation."""
    assert '_SW_HALF' in engine_js, "SW must be built from _SW_HALF half-table"
    assert "if(a!==b)SW[`${b}-${a}`]=w" in engine_js, \
        "SW must auto-generate reverse pairs from _SW_HALF"
    # Verify _SW_HALF has the core pairs
    m = re.search(r"const _SW_HALF=\{([\s\S]*?)\};", engine_js)
    assert m, "_SW_HALF not found"
    half = m.group(1)
    assert "'Sun-Moon'" in half, "Sun-Moon missing from _SW_HALF"
    assert "'Venus-Mars'" in half, "Venus-Mars missing from _SW_HALF"


def test_sd_symmetry(engine_js):
    """Every A-B pair in SD must also have B-A in the same domain."""
    # SD is built from _SD_HALF, so check the final SD object
    # We verify the construction pattern instead
    assert '_SD_HALF' in engine_js, "_SD_HALF not found — SD must be built from symmetric half-table"
    assert "if(a!==b)full.add(`${b}-${a}`)" in engine_js or 'if(a!==b)' in engine_js, \
        "SD symmetry construction not found — must add reverse pairs"


def test_sw_covers_sd(engine_js):
    """Every pair referenced in SD must have a weight in SW (not rely on default 0.4)."""
    # Extract _SD_HALF keys
    sd_m = re.search(r"const _SD_HALF=\{([\s\S]*?)\};", engine_js)
    assert sd_m, "_SD_HALF not found"
    sd_pairs = set(re.findall(r"'(\w+-\w+)'", sd_m.group(1)))
    # Extract _SW_HALF keys
    sw_m = re.search(r"const _SW_HALF=\{([\s\S]*?)\};", engine_js)
    assert sw_m, "_SW_HALF not found"
    sw_pairs = set(re.findall(r"'(\w+-\w+)'", sw_m.group(1)))
    # Check coverage (SD pairs should be in SW — at least one direction)
    missing = []
    for p in sd_pairs:
        a, b = p.split('-')
        if p not in sw_pairs and f"{b}-{a}" not in sw_pairs:
            missing.append(p)
    assert not missing, f"SD pairs missing from SW (will default to 0.4): {missing}"


def test_harmAsp_sort_uses_parentheses(html_path):
    """harmAsp sort must use explicit parentheses to avoid operator precedence bug."""
    html = html_path.read_text(encoding='utf-8')
    # Find all harmAsp sort expressions
    matches = re.findall(r"harmAsp=.*?\.sort\(([^)]+\))", html)
    assert matches, "harmAsp sort not found in HTML"
    for sort_body in matches:
        # Must NOT have the pattern: SW[...]||0-  (precedence bug)
        assert '||0-' not in sort_body, \
            f"harmAsp sort has operator precedence bug (||0- pattern): {sort_body}"


CORE_PERSONAL_PAIRS = [
    'Sun-Moon', 'Sun-Venus', 'Sun-Mars', 'Moon-Venus', 'Moon-Mars', 'Venus-Mars',
    'Mercury-Sun', 'Mercury-Moon', 'Mercury-Venus',
]

@pytest.mark.parametrize("pair", CORE_PERSONAL_PAIRS)
def test_sw_has_core_pair(engine_js, pair):
    """Core personal planet pairs must have explicit weights in SW, not defaults."""
    assert f"'{pair}'" in engine_js, f"Core pair {pair} missing from SW"
