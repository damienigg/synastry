"""JPL Horizons client, tolerances, and shared test data."""

import json
import urllib.request
import urllib.parse
from pathlib import Path

# ── JPL HORIZONS ──────────────────────────────────────────────────────────────
JPL_CODES = {
    'Sun': '10', 'Moon': '301', 'Mercury': '199', 'Venus': '299', 'Mars': '499',
    'Jupiter': '599', 'Saturn': '699', 'Uranus': '799', 'Neptune': '899', 'Pluto': '999',
}

CACHE_FILE = Path(__file__).parent.parent.parent / '.jpl_cache.json'


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def ang_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def jpl_query(planet, date_str, cache, verbose=False):
    key = f"{planet}@{date_str}"
    if key in cache:
        return cache[key], True
    if verbose:
        print(f"  JPL: {planet} @ {date_str}", flush=True)
    params = urllib.parse.urlencode({
        'format': 'json', 'COMMAND': f"'{JPL_CODES[planet]}'", 'OBJ_DATA': 'NO',
        'MAKE_EPHEM': 'YES', 'EPHEM_TYPE': 'OBSERVER', 'CENTER': "'500@399'",
        'START_TIME': f"'{date_str} 12:00'", 'STOP_TIME': f"'{date_str} 13:00'",
        'STEP_SIZE': "'1d'", 'QUANTITIES': "'31'", 'ANG_FORMAT': "'DEG'",
    })
    url = f"https://ssd.jpl.nasa.gov/api/horizons.api?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        text = json.loads(resp.read().decode()).get('result', '')
    soe = text.find('$$SOE')
    eoe = text.find('$$EOE')
    if soe < 0 or eoe < 0:
        raise ValueError(f"No SOE/EOE block in JPL response for {planet}@{date_str}")
    parts = text[soe + 5:eoe].strip().split('\n')[0].split()
    lon = float(parts[-2]) % 360
    cache[key] = lon
    save_cache(cache)
    return lon, False


# ── TEST RESULT ───────────────────────────────────────────────────────────────
class TestResult:
    def __init__(self, planet, date, app_lon, jpl_lon, diff, tol, passed, cached):
        self.planet = planet
        self.date = date
        self.app_lon = app_lon
        self.jpl_lon = jpl_lon
        self.diff = diff
        self.tol = tol
        self.passed = passed
        self.cached = cached


# ── TEST DATES ────────────────────────────────────────────────────────────────
DATES_CORE = [
    '1950-03-21', '1960-07-04', '1970-12-31',
    '1980-04-21', '1982-08-13', '1988-07-15', '1990-03-21', '1995-06-15',
    '2000-01-01', '2005-08-15', '2010-06-21', '2015-12-25', '2020-09-22',
]
DATES_EARLY = ['1920-01-01', '1935-06-15']
INNER = ['Mercury', 'Venus', 'Mars']
OUTER = ['Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
ALL_P = ['Sun', 'Moon'] + INNER + OUTER


# ── TOLERANCES ────────────────────────────────────────────────────────────────
_TOL_DEFAULTS = {
    'Ascendant': 2.0,
    'Sun':       0.5,
    'Moon':      0.5,
    'Mercury':   0.5,
    'Venus':     0.5,
    'Mars':      0.5,
    'Jupiter':   2.0,
    'Saturn':    3.0,
    'Uranus':    2.0,
    'Neptune':   1.0,
    'Pluto':     2.0,
}

_TOL_FILE = Path(__file__).parent.parent.parent / 'tolerances.json'


def load_tolerances():
    if _TOL_FILE.exists():
        try:
            data = json.loads(_TOL_FILE.read_text())
            merged = dict(_TOL_DEFAULTS)
            for k in merged:
                if k in data:
                    merged[k] = float(data[k])
            return merged
        except Exception as e:
            print(f"  Warning: could not parse {_TOL_FILE}: {e} -- using defaults")
    return dict(_TOL_DEFAULTS)
