#!/usr/bin/env python3
"""
Fit Neptune perturbation terms by comparing secular-element predictions
against JPL Horizons geocentric ecliptic longitudes.

Strategy:
  1. Query JPL Horizons for Neptune at ~50 dates spanning 1920-2050
  2. Compute Neptune's position using the app's secular elements (no perturbation)
  3. Compute residuals (JPL - secular)
  4. Fit a Fourier series to the residuals using candidate angular arguments
     derived from the mean longitudes of Jupiter, Saturn, Uranus, Neptune
  5. Report the best-fit terms for review before applying to the JS engine

Usage:
    python3 scripts/fit_neptune_pert.py              # run full fit
    python3 scripts/fit_neptune_pert.py --no-fetch    # use cached JPL data only
"""

import sys
import math
import json
import argparse
from pathlib import Path

# ── Reuse project helpers ────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tests'))
from helpers.jpl import jpl_query, load_cache, save_cache

# ── Secular elements (must match index.html exactly) ─────────────────────────
SECULAR = {
    'Jupiter': {'L': [34.351519, 3034.905675, -8.721e-4, 0], 'w': [14.331207, 1.612635, 1.030e-3, 0], 'e': [0.048498, 1.63e-4, -4.67e-6, 0], 'a': [5.202603, 1.4e-6, 0, 0]},
    'Saturn':  {'L': [50.077444, 1222.113777, 2.177e-4, 0],  'w': [93.056787, 1.963534, 8.32e-4, 0],  'e': [0.055546, -3.46e-4, -6.44e-7, 0], 'a': [9.554909, -2.1e-6, 0, 0]},
    'Uranus':  {'L': [314.055005, 428.466998, -3.5e-6, 0],   'w': [173.005291, 1.486379, 0, 0],        'e': [0.046381, -2.7e-5, -3.58e-8, 0],  'a': [19.218446, -3.72e-5, 0, 0]},
    'Neptune': {'L': [304.348665, 218.459991, 3.026e-4, 0],  'w': [48.123691, 1.426296, 0, 0],         'e': [0.008988, 6.0e-5, -5.18e-8, 0],   'a': [30.110387, -1.6e-6, 0, 0]},
}

def eval_poly(c, T):
    r = 0
    for i in range(len(c) - 1, -1, -1):
        r = r * T + c[i]
    return r

def m360(x):
    return ((x % 360) + 360) % 360

def get_sec(name, T):
    s = SECULAR[name]
    return {
        'L': m360(eval_poly(s['L'], T)),
        'w': m360(eval_poly(s['w'], T)),
        'e': eval_poly(s['e'], T),
        'a': eval_poly(s['a'], T),
    }

def kepler(M_deg, e, tol=1e-10, max_iter=60):
    M = math.radians(M_deg)
    E = M
    for _ in range(max_iter):
        dE = (M - E + e * math.sin(E)) / (1 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return math.degrees(E)

def neptune_secular_lon(T):
    """Compute Neptune geocentric ecliptic longitude using secular elements only."""
    s = get_sec('Neptune', T)
    M = m360(s['L'] - s['w'])
    E = math.radians(kepler(M, s['e']))
    v = 2 * math.atan2(
        math.sqrt(1 + s['e']) * math.sin(E / 2),
        math.sqrt(1 - s['e']) * math.cos(E / 2)
    )
    r = s['a'] * (1 - s['e'] * math.cos(E))
    helio_lon = v + math.radians(s['w'])
    px = r * math.cos(helio_lon)
    py = r * math.sin(helio_lon)

    # Earth position (simplified — use mean longitude for consistency)
    # We use the same approach as the JS engine: approximate Earth at 1 AU
    # For a proper fit we need Earth's actual position, but since we're fitting
    # residuals against the JS engine's own output, we replicate its logic.
    # The JS engine uses vsopLBR('Earth',T) but we don't have VSOP data here.
    # Instead, compute Earth's mean longitude from Sun's secular formula.
    sun_L0 = m360(280.46646 + 36000.76983 * T)
    sun_M = m360(357.52911 + 35999.05029 * T - 1.537e-4 * T * T)
    Mr = math.radians(sun_M)
    sun_C = (1.914602 - .004817 * T) * math.sin(Mr) + .019993 * math.sin(2 * Mr)
    earth_lon_rad = math.radians(m360(sun_L0 + sun_C + 180))  # opposite Sun
    ex = math.cos(earth_lon_rad)
    ey = math.sin(earth_lon_rad)

    geo_lon = m360(math.degrees(math.atan2(py - ey, px - ex)))
    return geo_lon

def jd(y, m, d, h=12, tz=0):
    ut = h - tz
    yr = y - 1 if m <= 2 else y
    mo = m + 12 if m <= 2 else m
    A = math.floor(yr / 100)
    B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (yr + 4716)) + math.floor(30.6001 * (mo + 1)) + d + B - 1524.5 + ut / 24

def T_from_date(y, m, d):
    return (jd(y, m, d, 12) - 2451545) / 36525

def ang_diff(a, b):
    """Signed angular difference a - b, in [-180, 180]."""
    d = (a - b) % 360
    if d > 180:
        d -= 360
    return d

# ── Candidate angular arguments ──────────────────────────────────────────────
def build_candidates(T):
    """Build candidate angular arguments from mean longitudes."""
    Lj = get_sec('Jupiter', T)['L']
    Ls = get_sec('Saturn', T)['L']
    Lu = get_sec('Uranus', T)['L']
    Ln = get_sec('Neptune', T)['L']

    # Candidate arguments: linear combinations of mean longitudes
    # Focus on slow-moving resonances involving Neptune
    return {
        'Ln-Lu':        Ln - Lu,
        'Ln-2Lu':       Ln - 2*Lu,
        '2Ln-4Lu':      2*Ln - 4*Lu,
        '2Ln-3Lu':      2*Ln - 3*Lu,
        '3Ln-5Lu':      3*Ln - 5*Lu,
        'Ln-3Lu':       Ln - 3*Lu,
        'Ls-Ln':        Ls - Ln,
        'Ls-2Ln':       Ls - 2*Ln,
        '2Ls-3Ln':      2*Ls - 3*Ln,
        'Lj-Ln':        Lj - Ln,
        'Lu-Ln':        Lu - Ln,
        '2Lu-3Ln':      2*Lu - 3*Ln,
        'Ln-Ls':        Ln - Ls,
        '2Ln-Lu':       2*Ln - Lu,
        '2Ln-2Lu':      2*Ln - 2*Lu,
        'Ls-3Lu+2Ln':   Ls - 3*Lu + 2*Ln,
        '2Ls-Lu-Ln':    2*Ls - Lu - Ln,
        'Lj-2Ls+Ln':    Lj - 2*Ls + Ln,
        'T':            T * 360,   # secular drift
    }

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-fetch', action='store_true', help='Use cached JPL data only')
    args = parser.parse_args()

    # Generate sample dates every ~2.5 years from 1920 to 2050
    dates = []
    for y in range(1920, 2051, 3):
        for m in [3, 9]:
            if y == 2051 and m == 9:
                break
            dates.append(f"{y}-{m:02d}-15")

    print(f"Fitting Neptune perturbation from {len(dates)} dates (1920-2050)\n")

    # Fetch JPL data
    cache = load_cache()
    data = []  # (T, residual, candidate_args)

    for ds in dates:
        y, m, d = map(int, ds.split('-'))
        T = T_from_date(y, m, d)

        key = f"Neptune@{ds}"
        if key in cache:
            jpl_lon = cache[key]
        elif args.no_fetch:
            continue
        else:
            try:
                jpl_lon, _ = jpl_query('Neptune', ds, cache, verbose=True)
            except Exception as e:
                print(f"  Skip {ds}: {e}")
                continue

        sec_lon = neptune_secular_lon(T)
        residual = ang_diff(jpl_lon, sec_lon)
        candidates = build_candidates(T)
        data.append((T, residual, candidates, ds, jpl_lon, sec_lon))

    if len(data) < 10:
        print(f"Only {len(data)} data points — need at least 10. Run without --no-fetch.")
        return

    print(f"\nCollected {len(data)} data points")
    residuals = [d[1] for d in data]
    print(f"Residual range: {min(residuals):.3f}° to {max(residuals):.3f}°")
    print(f"Residual mean:  {sum(residuals)/len(residuals):.3f}°")
    print(f"Residual RMS:   {math.sqrt(sum(r**2 for r in residuals)/len(residuals)):.3f}°")

    # ── Greedy forward selection of Fourier terms ────────────────────────────
    # For each candidate argument θ, fit A·sin(θ+φ) = a·sin(θ) + b·cos(θ)
    # using least squares. Select the term that reduces RMS the most,
    # subtract it, and repeat.

    candidate_names = list(build_candidates(0).keys())
    current_residuals = list(residuals)
    selected_terms = []
    MAX_TERMS = 8

    print(f"\n{'='*70}")
    print(f"GREEDY FOURIER FIT (up to {MAX_TERMS} terms)")
    print(f"{'='*70}")

    for iteration in range(MAX_TERMS):
        current_rms = math.sqrt(sum(r**2 for r in current_residuals) / len(current_residuals))
        if current_rms < 0.05:
            print(f"\nRMS {current_rms:.4f}° < 0.05° — stopping early")
            break

        best_name = None
        best_a = best_b = 0
        best_reduction = 0
        best_new_residuals = None

        for cname in candidate_names:
            # Build design matrix columns for this candidate
            sins = []
            coss = []
            for T, res, cands, *_ in data:
                theta = math.radians(cands[cname])
                sins.append(math.sin(theta))
                coss.append(math.cos(theta))

            # Least squares: minimize Σ(r - a·sin - b·cos)²
            # Normal equations: [ΣS² ΣSC] [a] = [ΣrS]
            #                   [ΣSC ΣC²] [b]   [ΣrC]
            n = len(current_residuals)
            SS = sum(s*s for s in sins)
            CC = sum(c*c for c in coss)
            SC = sum(s*c for s, c in zip(sins, coss))
            rS = sum(r*s for r, s in zip(current_residuals, sins))
            rC = sum(r*c for r, c in zip(current_residuals, coss))

            det = SS * CC - SC * SC
            if abs(det) < 1e-12:
                continue

            a = (CC * rS - SC * rC) / det
            b = (SS * rC - SC * rS) / det

            # Compute new residuals
            new_res = [r - a*s - b*c for r, s, c in zip(current_residuals, sins, coss)]
            new_rms = math.sqrt(sum(r**2 for r in new_res) / n)
            reduction = current_rms - new_rms

            if reduction > best_reduction:
                best_name = cname
                best_a = a
                best_b = b
                best_reduction = reduction
                best_new_residuals = new_res

        if best_name is None or best_reduction < 0.001:
            print(f"\nNo significant improvement — stopping at {iteration} terms")
            break

        # Convert a·sin(θ) + b·cos(θ) → A·sin(θ+φ)
        A = math.sqrt(best_a**2 + best_b**2)
        phi = math.degrees(math.atan2(best_b, best_a))

        selected_terms.append({
            'name': best_name,
            'A': A,
            'phi': phi,
            'a_sin': best_a,
            'b_cos': best_b,
        })

        new_rms = math.sqrt(sum(r**2 for r in best_new_residuals) / len(best_new_residuals))
        print(f"\n  Term {iteration+1}: {best_name}")
        print(f"    A = {A:.4f}°,  φ = {phi:.1f}°")
        print(f"    a·sin = {best_a:+.4f},  b·cos = {best_b:+.4f}")
        print(f"    RMS: {current_rms:.4f}° → {new_rms:.4f}° (Δ = {best_reduction:.4f}°)")

        current_residuals = best_new_residuals
        candidate_names.remove(best_name)

    # ── Summary ──────────────────────────────────────────────────────────────
    final_rms = math.sqrt(sum(r**2 for r in current_residuals) / len(current_residuals))
    max_err = max(abs(r) for r in current_residuals)

    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    print(f"  Terms selected: {len(selected_terms)}")
    print(f"  Original RMS:   {math.sqrt(sum(r**2 for r in residuals)/len(residuals)):.4f}°")
    print(f"  Final RMS:      {final_rms:.4f}°")
    print(f"  Max residual:   {max_err:.4f}°")
    print()

    # ── Generate JS code ─────────────────────────────────────────────────────
    print("PROPOSED JS FUNCTION:")
    print("-" * 70)

    # Build the argument expressions
    arg_map = {
        'Lj': "getSec('Jupiter',T).L",
        'Ls': "getSec('Saturn',T).L",
        'Lu': "getSec('Uranus',T).L",
        'Ln': "getSec('Neptune',T).L",
    }

    # Map candidate names to JS expressions
    def arg_to_js(name):
        replacements = {'Lj': 'Lj', 'Ls': 'Ls', 'Lu': 'Lu', 'Ln': 'Ln'}
        expr = name
        for k, v in replacements.items():
            expr = expr.replace(k, v)
        return expr

    # Print the function
    used_planets = set()
    for t in selected_terms:
        for p in ['Lj', 'Ls', 'Lu', 'Ln']:
            if p in t['name'] or p[1:] in t['name']:
                used_planets.add(p)

    var_decls = []
    if 'Lj' in used_planets: var_decls.append("Lj=getSec('Jupiter',T).L")
    if 'Ls' in used_planets: var_decls.append("Ls=getSec('Saturn',T).L")
    if 'Lu' in used_planets: var_decls.append("Lu=getSec('Uranus',T).L")
    if 'Ln' in used_planets: var_decls.append("Ln=getSec('Neptune',T).L")

    print(f"function nepPert(T){{const {','.join(var_decls)},r=x=>x*Math.PI/180;return ", end='')

    terms_js = []
    for i, t in enumerate(selected_terms):
        arg_expr = arg_to_js(t['name'])
        # Use A·sin(arg + phi) form
        a = t['a_sin']
        b = t['b_cos']
        # Express as a*sin(r(expr)) + b*cos(r(expr))
        if abs(a) >= abs(b):
            parts = []
            if abs(a) > 0.0005:
                parts.append(f"{a:+.3f}*Math.sin(r({arg_expr}))")
            if abs(b) > 0.0005:
                parts.append(f"{b:+.3f}*Math.cos(r({arg_expr}))")
            terms_js.extend(parts)
        else:
            parts = []
            if abs(b) > 0.0005:
                parts.append(f"{b:+.3f}*Math.cos(r({arg_expr}))")
            if abs(a) > 0.0005:
                parts.append(f"{a:+.3f}*Math.sin(r({arg_expr}))")
            terms_js.extend(parts)

    print(''.join(terms_js) + ';}')

    # ── Per-date breakdown ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"PER-DATE RESIDUALS (after fit)")
    print(f"{'='*70}")
    print(f"{'Date':<14} {'JPL':>10} {'Secular':>10} {'Fitted':>10} {'Residual':>10}")
    print("-" * 60)
    for i, (T, orig_res, cands, ds, jpl_lon, sec_lon) in enumerate(data):
        correction = 0
        for t in selected_terms:
            theta = math.radians(cands[t['name']])
            correction += t['a_sin'] * math.sin(theta) + t['b_cos'] * math.cos(theta)
        fitted_lon = sec_lon + correction
        final_res = ang_diff(jpl_lon, fitted_lon)
        flag = ' !' if abs(final_res) > 1.0 else ''
        print(f"{ds:<14} {jpl_lon:>10.3f} {sec_lon:>10.3f} {fitted_lon:>10.3f} {final_res:>+10.3f}{flag}")


if __name__ == '__main__':
    main()
