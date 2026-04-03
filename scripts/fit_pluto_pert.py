#!/usr/bin/env python3
"""
Fit Pluto perturbation terms by comparing secular-element predictions
against JPL Horizons geocentric ecliptic longitudes.

Pluto has no existing Meeus perturbation — comparison is baseline only.

Usage:
    python3 scripts/fit_pluto_pert.py
    python3 scripts/fit_pluto_pert.py --no-fetch
"""

import sys, math, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'scripts'))

from helpers.jpl import jpl_query, load_cache
from secular import (get_sec, geocentric_lon, T_from_date, ang_diff,
                     build_candidates, fit_fourier, generate_dates)

PLANET = 'Pluto'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-fetch', action='store_true')
    args = parser.parse_args()

    dates = generate_dates()
    cache = load_cache()
    data = []

    print(f"Fitting {PLANET} perturbation from ~{len(dates)} dates (1920-2050)\n")

    for ds in dates:
        y, m, d = map(int, ds.split('-'))
        T = T_from_date(y, m, d)
        key = f"{PLANET}@{ds}"
        if key in cache:
            jpl_lon = cache[key]
        elif args.no_fetch:
            continue
        else:
            try:
                jpl_lon, _ = jpl_query(PLANET, ds, cache, verbose=True)
            except Exception as e:
                print(f"  Skip {ds}: {e}")
                continue

        sec_lon = geocentric_lon(PLANET, T)
        residual = ang_diff(jpl_lon, sec_lon)
        candidates = build_candidates(T)
        data.append((T, residual, candidates, ds, jpl_lon, sec_lon))

    if len(data) < 10:
        print(f"Only {len(data)} data points. Run without --no-fetch.")
        return

    residuals = [d[1] for d in data]
    n = len(data)
    base_rms = math.sqrt(sum(r**2 for r in residuals) / n)
    base_max = max(abs(r) for r in residuals)

    print(f"\nData points: {n}")
    print(f"\n{'Method':<25} {'RMS':>8} {'Max':>8}")
    print("-" * 43)
    print(f"{'No perturbation':<25} {base_rms:>8.4f} {base_max:>8.4f}")

    # JPL fit
    selected, final_res = fit_fourier(data, list(build_candidates(0).keys()))
    fit_rms = math.sqrt(sum(r**2 for r in final_res) / n)
    fit_max = max(abs(r) for r in final_res)
    print(f"{'JPL-fitted':<25} {fit_rms:>8.4f} {fit_max:>8.4f}")

    print(f"\n{'='*60}")
    print(f"FITTED TERMS ({len(selected)})")
    print(f"{'='*60}")
    for i, t in enumerate(selected):
        print(f"  {i+1}. {t['name']:20s}  A={t['A']:.4f}°  a·sin={t['a_sin']:+.4f}  b·cos={t['b_cos']:+.4f}  (RMS→{t['new_rms']:.4f}°)")

    print(f"\n{'='*60}")
    if fit_rms < base_rms * 0.5:  # significant improvement
        print(f"VERDICT: JPL-fitted IMPROVES on baseline ({base_rms:.4f}° → {fit_rms:.4f}°)")
        print(f"\nPROPOSED JS:")
        _print_js(selected)
    else:
        print(f"VERDICT: Fit insufficient ({base_rms:.4f}° → {fit_rms:.4f}°). Secular elements may be the limiting factor.")

    # Per-date table
    print(f"\n{'Date':<14} {'JPL':>10} {'Secular':>10} {'Fitted':>10} {'Residual':>10}")
    print("-" * 60)
    for i, (T, orig_res, cands, ds, jpl_lon, sec_lon) in enumerate(data):
        correction = sum(t['a_sin']*math.sin(math.radians(cands[t['name']])) +
                         t['b_cos']*math.cos(math.radians(cands[t['name']])) for t in selected)
        fit_lon = geocentric_lon(PLANET, T, correction)
        fe = ang_diff(jpl_lon, fit_lon)
        flag = ' !' if abs(fe) > 2.0 else ''
        print(f"{ds:<14} {jpl_lon:>10.3f} {sec_lon:>10.3f} {fit_lon:>10.3f} {fe:>+10.3f}{flag}")


def _print_js(terms):
    used = set()
    for t in terms:
        for p in ['Lj', 'Ls', 'Lu', 'Ln']:
            if p[1:] in t['name'] or p in t['name']:
                used.add(p)
    decls = []
    if 'Lj' in used: decls.append("Lj=getSec('Jupiter',T).L")
    if 'Ls' in used: decls.append("Ls=getSec('Saturn',T).L")
    if 'Lu' in used: decls.append("Lu=getSec('Uranus',T).L")
    if 'Ln' in used: decls.append("Ln=getSec('Neptune',T).L")
    parts = []
    for t in terms:
        if abs(t['a_sin']) > 0.0005:
            parts.append(f"{t['a_sin']:+.3f}*Math.sin(r({t['name']}))")
        if abs(t['b_cos']) > 0.0005:
            parts.append(f"{t['b_cos']:+.3f}*Math.cos(r({t['name']}))")
    print(f"function pluPert(T){{const {','.join(decls)},r=x=>x*Math.PI/180;return{''.join(parts)};}}")


if __name__ == '__main__':
    main()
