import pytest
import json
from tests.helpers.engine import NODE_UNIT_SHIM, T_from
from tests.helpers.node_runner import run_node

pytestmark = pytest.mark.unit


class TestDateEdgeCases:
    """Test date handling edge cases."""

    def test_leap_year_feb_29(self, engine_js, node_bin):
        """Feb 29 on a leap year should produce valid JD."""
        cases = [{'fn':'toJD','args':[2000,2,29,12,0],'name':'leap year'}]
        raw = run_node(node_bin, engine_js, NODE_UNIT_SHIM, [json.dumps(cases)])
        result = json.loads(raw)[0]
        assert result.get('error') is None
        jd = float(result['got'])
        assert 2451000 < jd < 2452000  # reasonable range

    def test_year_1920_boundary(self, engine_js, node_bin):
        """Dates near 1920 (earliest JPL-validated) should still compute."""
        cases = [{'fn':'sunPos','args':[T_from('1920-01-01')],'name':'1920 sun'}]
        raw = run_node(node_bin, engine_js, NODE_UNIT_SHIM, [json.dumps(cases)])
        result = json.loads(raw)[0]
        assert result.get('error') is None
        lon = float(result['got'])
        assert 0 <= lon < 360

    def test_year_2050_boundary(self, engine_js, node_bin):
        """Dates near 2050 (latest JPL-validated) should still compute."""
        cases = [{'fn':'sunPos','args':[T_from('2050-12-31')],'name':'2050 sun'}]
        raw = run_node(node_bin, engine_js, NODE_UNIT_SHIM, [json.dumps(cases)])
        result = json.loads(raw)[0]
        assert result.get('error') is None
        lon = float(result['got'])
        assert 0 <= lon < 360

    def test_midnight_utc(self, engine_js, node_bin):
        """Birth at midnight UTC should not produce NaN or errors."""
        cases = [{'fn':'buildChart','args':['2000-01-01','00:00',0,False,42,0],'name':'midnight'}]
        raw = run_node(node_bin, engine_js, NODE_UNIT_SHIM, [json.dumps(cases)])
        result = json.loads(raw)[0]
        assert result.get('error') is None
        p = json.loads(result['got'])
        assert p['nPositions'] == 11
        # All positions should be valid numbers, not NaN
        for planet, data in p['pos'].items():
            assert 0 <= data['lon'] < 360, f"{planet} lon={data['lon']}"

    def test_extreme_timezone_offset(self, engine_js, node_bin):
        """UTC+12 and UTC-12 should produce valid results."""
        for tz in [12, -12]:
            cases = [{'fn':'buildChart','args':['2000-06-15','12:00',tz,False,42,0],'name':f'tz={tz}'}]
            raw = run_node(node_bin, engine_js, NODE_UNIT_SHIM, [json.dumps(cases)])
            result = json.loads(raw)[0]
            assert result.get('error') is None, f"tz={tz} error: {result.get('error')}"
