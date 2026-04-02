"""Node.js execution helpers."""

import os
import json
import subprocess
import tempfile

from tests.helpers.formatting import col, C_DIM
from tests.helpers.engine import NODE_QUERY_SHIM


def find_node():
    import shutil
    for name in ('node', 'nodejs', 'node20', 'node18', 'node16'):
        p = shutil.which(name)
        if p:
            return p
    for p in ('/usr/bin/node', '/usr/bin/nodejs', '/usr/local/bin/node', '/opt/homebrew/bin/node'):
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    raise FileNotFoundError(
        "Node.js not found. Install it with:\n"
        "  Ubuntu/Debian : sudo apt install nodejs\n"
        "  macOS         : brew install node\n"
        "  or download   : https://nodejs.org")


def run_node(node_bin, engine_js, shim, argv_extra, timeout=30):
    script = engine_js + "\n" + shim
    with tempfile.NamedTemporaryFile(suffix='.js', mode='w', encoding='utf-8', delete=False) as f:
        f.write(script)
        tmp = f.name
    try:
        result = subprocess.run([node_bin, tmp] + argv_extra,
                                capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(f"Node.js error:\nstdout: {result.stdout}\nstderr: {result.stderr}")
        return result.stdout.strip()
    finally:
        os.unlink(tmp)


def engine_lon(node_bin, engine_js, planet, date_str, verbose=False):
    if verbose:
        print(f"  {col(C_DIM, 'Node:')} {planet} @ {date_str}", flush=True)
    return json.loads(run_node(node_bin, engine_js, NODE_QUERY_SHIM, [planet, date_str]))
