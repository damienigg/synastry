import pytest
import datetime
import re
from pathlib import Path


def pytest_addoption(parser):
    parser.addoption("--app", default=None, help="Path to the HTML app file")
    parser.addoption("--no-jpl", action="store_true", help="Skip JPL/external validation tests")
    parser.addoption("--clear-cache", action="store_true", help="Clear JPL cache before run")


@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def html_path(project_root, pytestconfig):
    app_opt = pytestconfig.getoption("--app")
    p = Path(app_opt) if app_opt else project_root / "index.html"
    if not p.exists():
        pytest.skip(f"App HTML not found: {p}")
    return p


@pytest.fixture(scope="session")
def engine_js(html_path):
    from tests.helpers.engine import extract_engine
    return extract_engine(html_path)


@pytest.fixture(scope="session")
def node_bin():
    from tests.helpers.node_runner import find_node
    return find_node()


@pytest.fixture(scope="session")
def tolerances():
    from tests.helpers.jpl import load_tolerances
    return load_tolerances()


@pytest.fixture(scope="session")
def jpl_cache(project_root, pytestconfig):
    from tests.helpers.jpl import load_cache, CACHE_FILE
    if pytestconfig.getoption("--clear-cache") and CACHE_FILE.exists():
        CACHE_FILE.unlink()
    return load_cache()


# ── Report plugin ─────────────────────────────────────────────────────────────
_ANSI_RE = re.compile(r'\033\[[0-9;]*m')


class ReportPlugin:
    def __init__(self, report_dir):
        self.lines = []
        self.report_dir = report_dir
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.report_path = report_dir / f"test_report_{ts}.txt"

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            status = "PASS" if report.passed else "FAIL" if report.failed else "SKIP"
            self.lines.append(f"  {status}  {report.nodeid}")
            if report.failed and report.longreprtext:
                for line in report.longreprtext.split('\n')[:5]:
                    self.lines.append(f"         {line}")

    def pytest_sessionfinish(self, session, exitstatus):
        self.report_dir.mkdir(exist_ok=True)
        with open(self.report_path, 'w') as f:
            f.write(f"Synastria Test Report -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 72}\n\n")
            for line in self.lines:
                clean = _ANSI_RE.sub('', line)
                f.write(clean + '\n')
            n_pass = sum(1 for l in self.lines if l.strip().startswith('PASS'))
            n_fail = sum(1 for l in self.lines if l.strip().startswith('FAIL'))
            f.write(f"\n{'=' * 72}\n")
            f.write(f"{n_pass} passed, {n_fail} failed\n")
        print(f"\n  Report saved to: {self.report_path.resolve()}")


def pytest_configure(config):
    report_dir = Path(config.rootdir) / "reports"
    config.pluginmanager.register(ReportPlugin(report_dir), "report_plugin")
