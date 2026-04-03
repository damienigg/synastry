"""
Shared secular-element computation for perturbation fitting scripts.
Replicates the JS engine's orbital mechanics in Python so we can compute
baseline (unperturbed) positions and compare against JPL Horizons.

Must stay in exact sync with index.html SECULAR constants and formulas.
"""

import math

# ── Secular elements (must match index.html exactly) ─────────────────────────
SECULAR = {
    'Jupiter': {'L': [34.351519, 3034.905675, -8.721e-4, 0], 'w': [14.331207, 1.612635, 1.030e-3, 0], 'e': [0.048498, 1.63e-4, -4.67e-6, 0], 'a': [5.202603, 1.4e-6, 0, 0]},
    'Saturn':  {'L': [50.077444, 1222.113777, 2.177e-4, 0],  'w': [93.056787, 1.963534, 8.32e-4, 0],  'e': [0.055546, -3.46e-4, -6.44e-7, 0], 'a': [9.554909, -2.1e-6, 0, 0]},
    'Uranus':  {'L': [314.055005, 428.466998, -3.5e-6, 0],   'w': [173.005291, 1.486379, 0, 0],        'e': [0.046381, -2.7e-5, -3.58e-8, 0],  'a': [19.218446, -3.72e-5, 0, 0]},
    'Neptune': {'L': [304.348665, 218.459991, 3.026e-4, 0],  'w': [48.123691, 1.426296, 0, 0],         'e': [0.008988, 6.0e-5, -5.18e-8, 0],   'a': [30.110387, -1.6e-6, 0, 0]},
    'Pluto':   {'L': [238.92904, 145.20780, 0, 0],           'w': [224.06891, 0, 0, 0],                 'e': [0.24883, 0, 0, 0],                 'a': [39.48169, 0, 0, 0]},
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


def geocentric_lon(name, T, pert_deg=0):
    """Compute geocentric ecliptic longitude using secular elements + optional perturbation."""
    s = get_sec(name, T)
    M = m360(s['L'] - s['w'])
    E = math.radians(kepler(M, s['e']))
    v = 2 * math.atan2(
        math.sqrt(1 + s['e']) * math.sin(E / 2),
        math.sqrt(1 - s['e']) * math.cos(E / 2)
    )
    r = s['a'] * (1 - s['e'] * math.cos(E))
    helio_lon = v + math.radians(s['w']) + math.radians(pert_deg)
    px = r * math.cos(helio_lon)
    py = r * math.sin(helio_lon)

    # Earth approximation (same as JS engine for outer planets)
    sun_L0 = m360(280.46646 + 36000.76983 * T)
    sun_M = m360(357.52911 + 35999.05029 * T - 1.537e-4 * T * T)
    Mr = math.radians(sun_M)
    sun_C = (1.914602 - .004817 * T) * math.sin(Mr) + .019993 * math.sin(2 * Mr)
    earth_lon_rad = math.radians(m360(sun_L0 + sun_C + 180))
    ex = math.cos(earth_lon_rad)
    ey = math.sin(earth_lon_rad)

    return m360(math.degrees(math.atan2(py - ey, px - ex)))


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


# ── Current Meeus perturbation functions (must match index.html) ─────────────
def jup_pert_meeus(T):
    Lj = get_sec('Jupiter', T)['L']
    Ls = get_sec('Saturn', T)['L']
    r = math.radians
    return (+0.332 * math.sin(r(2*Lj - 5*Ls - 67.6))
            + 0.056 * math.sin(r(2*Lj - 2*Ls + 21))
            + 0.042 * math.sin(r(3*Lj - 5*Ls + 21))
            - 0.036 * math.sin(r(Lj - 2*Ls))
            + 0.022 * math.cos(r(Lj - Ls))
            + 0.023 * math.sin(r(2*Lj - 3*Ls + 52))
            - 0.016 * math.sin(r(Lj - 5*Ls - 69)))


def sat_pert_meeus(T):
    Lj = get_sec('Jupiter', T)['L']
    Ls = get_sec('Saturn', T)['L']
    r = math.radians
    return (+0.812 * math.sin(r(2*Lj - 5*Ls - 67.6))
            + 0.229 * math.cos(r(2*Lj - 4*Ls - 2))
            + 0.119 * math.cos(r(Lj - 2*Ls - 3))
            + 0.046 * math.cos(r(2*Lj - 6*Ls - 69))
            + 0.014 * math.sin(r(Lj - 3*Ls + 32))
            - 0.056 * math.sin(r(2*Lj - 2*Ls - 22))
            + 0.024 * math.sin(r(2*Lj - 3*Ls + 52)))


def ura_pert_meeus(T):
    Ls = get_sec('Saturn', T)['L']
    Lu = get_sec('Uranus', T)['L']
    Ln = get_sec('Neptune', T)['L']
    r = math.radians
    return (+0.664 * math.sin(r(Ls - 2*Lu + 75.0))
            + 0.348 * math.sin(r(Ls - 3*Lu + 70.7))
            + 0.261 * math.sin(r(2*Ls - 6*Lu + 105))
            + 0.198 * math.sin(r(2*Ls - 7*Lu + 108))
            - 0.114 * math.sin(r(3*Ls - 7*Lu + 55))
            + 0.049 * math.sin(r(Ln - Lu))
            - 0.044 * math.sin(r(Ls - 4*Lu + 68)))


MEEUS_PERT = {
    'Jupiter': jup_pert_meeus,
    'Saturn':  sat_pert_meeus,
    'Uranus':  ura_pert_meeus,
    'Neptune': None,  # currently using JPL-fitted
    'Pluto':   None,
}


# ── Candidate angular arguments ──────────────────────────────────────────────
def build_candidates(T):
    Lj = get_sec('Jupiter', T)['L']
    Ls = get_sec('Saturn', T)['L']
    Lu = get_sec('Uranus', T)['L']
    Ln = get_sec('Neptune', T)['L']
    return {
        # Jupiter-Saturn resonances
        '2Lj-5Ls':    2*Lj - 5*Ls,
        'Lj-2Ls':     Lj - 2*Ls,
        'Lj-Ls':      Lj - Ls,
        '2Lj-2Ls':    2*Lj - 2*Ls,
        '2Lj-3Ls':    2*Lj - 3*Ls,
        '2Lj-4Ls':    2*Lj - 4*Ls,
        '3Lj-5Ls':    3*Lj - 5*Ls,
        'Lj-3Ls':     Lj - 3*Ls,
        '2Lj-6Ls':    2*Lj - 6*Ls,
        'Lj-5Ls':     Lj - 5*Ls,
        # Saturn-Uranus
        'Ls-2Lu':     Ls - 2*Lu,
        'Ls-3Lu':     Ls - 3*Lu,
        '2Ls-6Lu':    2*Ls - 6*Lu,
        '2Ls-7Lu':    2*Ls - 7*Lu,
        '3Ls-7Lu':    3*Ls - 7*Lu,
        'Ls-4Lu':     Ls - 4*Lu,
        'Ls-Lu':      Ls - Lu,
        # Uranus-Neptune
        'Lu-Ln':      Lu - Ln,
        'Ln-Lu':      Ln - Lu,
        '2Ln-Lu':     2*Ln - Lu,
        'Ln-2Lu':     Ln - 2*Lu,
        '2Ln-4Lu':    2*Ln - 4*Lu,
        '2Ln-3Lu':    2*Ln - 3*Lu,
        '3Ln-5Lu':    3*Ln - 5*Lu,
        'Ln-3Lu':     Ln - 3*Lu,
        '2Ln-2Lu':    2*Ln - 2*Lu,
        # Jupiter-Neptune, Jupiter-Uranus
        'Lj-Ln':      Lj - Ln,
        'Lj-Lu':      Lj - Lu,
        'Lj-2Lu':     Lj - 2*Lu,
        '2Lj-Lu':     2*Lj - Lu,
        # Saturn-Neptune
        'Ls-Ln':      Ls - Ln,
        'Ls-2Ln':     Ls - 2*Ln,
        '2Ls-3Ln':    2*Ls - 3*Ln,
        '2Ls-Lu-Ln':  2*Ls - Lu - Ln,
        # Mixed
        'Lj-2Ls+Ln':  Lj - 2*Ls + Ln,
        'Ls-3Lu+2Ln': Ls - 3*Lu + 2*Ln,
        # Secular drift
        'T':           T * 360,
    }


# ── Fourier fitting engine ───────────────────────────────────────────────────
def fit_fourier(data, candidate_names, max_terms=8, min_rms=0.05, min_improvement=0.001):
    """
    Greedy forward selection of Fourier terms.

    data: list of (T, residual, candidates_dict)
    Returns: (selected_terms, final_residuals)
    """
    current_residuals = [d[1] for d in data]
    selected = []
    available = list(candidate_names)

    for iteration in range(max_terms):
        current_rms = math.sqrt(sum(r**2 for r in current_residuals) / len(current_residuals))
        if current_rms < min_rms:
            break

        best = None
        for cname in available:
            sins = [math.sin(math.radians(d[2][cname])) for d in data]
            coss = [math.cos(math.radians(d[2][cname])) for d in data]

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
            new_res = [r - a*s - b*c for r, s, c in zip(current_residuals, sins, coss)]
            new_rms = math.sqrt(sum(r**2 for r in new_res) / len(new_res))
            reduction = current_rms - new_rms

            if best is None or reduction > best['reduction']:
                best = {
                    'name': cname, 'a_sin': a, 'b_cos': b,
                    'A': math.sqrt(a**2 + b**2),
                    'phi': math.degrees(math.atan2(b, a)),
                    'reduction': reduction, 'new_rms': new_rms,
                    'new_residuals': new_res,
                }

        if best is None or best['reduction'] < min_improvement:
            break

        selected.append(best)
        current_residuals = best['new_residuals']
        available.remove(best['name'])

    return selected, current_residuals


# ── Sample dates ─────────────────────────────────────────────────────────────
def generate_dates(step_years=3):
    dates = []
    for y in range(1920, 2051, step_years):
        for m in [3, 9]:
            if y == 2051 and m == 9:
                break
            dates.append(f"{y}-{m:02d}-15")
    return dates
