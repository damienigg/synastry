import pytest
from tests.helpers.jpl import jpl_query, ang_diff, DATES_CORE, DATES_EARLY, INNER, OUTER, ALL_P
from tests.helpers.node_runner import engine_lon

pytestmark = pytest.mark.jpl


def _planet_date_params():
    params = []
    seen = set()
    for planet in ALL_P:
        dates = DATES_CORE + (DATES_EARLY if planet in INNER + ['Sun'] else [])
        for d in dates:
            key = (planet, d)
            if key not in seen:
                params.append(pytest.param(planet, d, id=f"{planet}@{d}"))
                seen.add(key)
    # Jupiter and Saturn early dates
    for planet in ['Jupiter', 'Saturn']:
        for d in DATES_EARLY:
            key = (planet, d)
            if key not in seen:
                params.append(pytest.param(planet, d, id=f"{planet}@{d}-early"))
                seen.add(key)
    return params


@pytest.mark.parametrize("planet,date_str", _planet_date_params())
def test_jpl_planet(planet, date_str, engine_js, node_bin, jpl_cache, tolerances, pytestconfig):
    if pytestconfig.getoption("--no-jpl"):
        pytest.skip("--no-jpl")
    app_data = engine_lon(node_bin, engine_js, planet, date_str)
    app_lon = app_data['lon']
    jpl_lon, _ = jpl_query(planet, date_str, jpl_cache)
    diff = ang_diff(app_lon, jpl_lon)
    tol = tolerances[planet]
    assert diff <= tol, f"app={app_lon:.3f} jpl={jpl_lon:.3f} d={diff:.2f} tol={tol:.1f}"
