import pytest
import json
from tests.helpers.engine import NODE_ASC_SHIM
from tests.helpers.node_runner import run_node
from tests.helpers.jpl import ang_diff

pytestmark = pytest.mark.ascendant

ASC_CASES = [
    # (label, date_str, hour, lat, lon, sweph_asc)
    ('Equator/Greenwich',  '2000-01-01', 12,   0.0,    0.0,   11.3739),
    ('lat=42 lon=0',       '2000-01-01', 12,  42.0,    0.0,   18.4469),
    ('Paris',              '2000-01-01', 12,  48.9,    2.35,  26.8059),
    ('London summer',      '2000-06-15', 12,  51.5,   -0.12, 175.7353),
    ('Sydney summer',      '2000-06-15', 12, -33.9,  151.2,  330.8498),
    ('Stockholm',          '2000-01-01', 12,  59.3,   18.07,  74.0809),
    ('Buenos Aires',       '2000-01-01', 12, -34.6,  -58.38, 320.1481),
    ('Rome 1980',          '1980-04-21', 12,  41.9,   12.5,  142.7298),
    ('Paris 1990 spring',  '1990-03-21', 12,  48.9,    2.35, 115.3455),
    ('NYC 1950 spring',    '1950-03-21', 12,  40.7,  -74.0,   24.5306),
    ('Tokyo 2020 autumn',  '2020-09-22', 12,  35.7,  139.7,   69.9746),
    ('lat=42 lon=30',      '2000-01-01', 12,  42.0,   30.0,   62.3479),
    ('lat=42 lon=90',      '2000-01-01', 12,  42.0,   90.0,  118.0809),
]


@pytest.mark.parametrize("label,date_str,hour,lat,lon,sweph_asc", ASC_CASES,
                         ids=[c[0] for c in ASC_CASES])
def test_ascendant_vs_swisseph(label, date_str, hour, lat, lon, sweph_asc,
                                engine_js, node_bin, tolerances, pytestconfig):
    if pytestconfig.getoption("--no-jpl"):
        pytest.skip("--no-jpl")
    tol = tolerances.get('Ascendant', 2.0)
    raw = run_node(node_bin, engine_js, NODE_ASC_SHIM,
                   [date_str, str(hour), str(lat), str(lon)])
    data = json.loads(raw)
    app_asc = data['asc']
    diff = ang_diff(app_asc, sweph_asc)
    assert diff <= tol, f"app={app_asc:.4f} sweph={sweph_asc:.4f} d={diff:.4f}"
