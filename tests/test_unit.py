import pytest
import json
from tests.helpers.engine import NODE_UNIT_SHIM, T_from
from tests.helpers.node_runner import run_node
from tests.helpers.jpl import ang_diff

pytestmark = pytest.mark.unit


def _build_cases():
    T = T_from

    EXPECTED_ZSIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                       'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

    return [
        # ── 1. toJD ───────────────────────────────────────────────────────────
        {'fn':'toJD','args':[2000,1,1,12,0],'name':'toJD: J2000 = 2451545.0','exp':2451545.0,'tol':1e-4},
        {'fn':'toJD','args':[1987,4,10,0,0],'name':'toJD: 1987-04-10 = 2446895.5','exp':2446895.5,'tol':1e-4},
        {'fn':'toJD','args':[1900,1,1,0,0],'name':'toJD: 1900-01-01 = 2415020.5','exp':2415020.5,'tol':1e-4},
        {'fn':'toJD','args':[2000,1,1,0,0],'name':'toJD: 2000-01-01 00:00 = 2451544.5','exp':2451544.5,'tol':1e-4},
        {'fn':'toJD','args':[2000,1,1,12,5],'name':'toJD: tz+5 shifts JD by -5/24','exp':2451545.0-5/24,'tol':1e-4},
        # ── 2. toT ────────────────────────────────────────────────────────────
        {'fn':'toT','args':[2451545.0],'name':'toT: T=0 at J2000','exp':0.0,'tol':1e-9},
        {'fn':'toT','args':[2451545.0+36525],'name':'toT: T=1 one century later','exp':1.0,'tol':1e-9},
        # ── 3. m360 ───────────────────────────────────────────────────────────
        {'fn':'m360','args':[-90],    'name':'m360(-90)  = 270',     'exp':270,    'tol':1e-6},
        {'fn':'m360','args':[450],    'name':'m360(450)  = 90',      'exp':90,     'tol':1e-6},
        {'fn':'m360','args':[-360],   'name':'m360(-360) = 0',       'exp':0,      'tol':1e-6},
        {'fn':'m360','args':[0],      'name':'m360(0)    = 0',       'exp':0,      'tol':1e-6},
        {'fn':'m360','args':[360],    'name':'m360(360)  = 0',       'exp':0,      'tol':1e-6},
        {'fn':'m360','args':[-1],     'name':'m360(-1)   = 359',     'exp':359,    'tol':1e-6},
        {'fn':'m360','args':[359.999],'name':'m360(359.999) < 360',  'exp':359.999,'tol':1e-3},
        {'fn':'m360','args':[720],    'name':'m360(720)  = 0',       'exp':0,      'tol':1e-6},
        # ── 4. sunPos ─────────────────────────────────────────────────────────
        {'fn':'sunPos','args':[T('1992-10-13',0)],'name':'sunPos 1992-10-13 ≈ 199.9° (Meeus)','exp':199.9,'tol':1.0,'angle':True},
        {'fn':'sunPos','args':[T('2000-03-20',7.5)],'name':'sunPos vernal equinox 2000 ≈ 0°','exp':0,'tol':2.5,'angle':True},
        {'fn':'sunPos','args':[T('2000-06-21',1.5)],'name':'sunPos summer solstice 2000 ≈ 90°','exp':90,'tol':2.5,'angle':True},
        {'fn':'sunPos','args':[T('2000-09-22',17)],'name':'sunPos autumnal equinox 2000 ≈ 180°','exp':180,'tol':2.5,'angle':True},
        {'fn':'sunPos','args':[T('2000-12-21',13.5)],'name':'sunPos winter solstice 2000 ≈ 270°','exp':270,'tol':2.5,'angle':True},
        {'fn':'sunPos','args':[0.0],'name':'sunPos J2000 ∈ [0,360)','range':[0,360]},
        # ── 5. moonPos ────────────────────────────────────────────────────────
        {'fn':'moonPos','args':[0.0],'name':'moonPos J2000 ∈ [0,360)','range':[0,360]},
        {'fn':'moonPos','args':[T('1992-04-12',0)],'name':'moonPos 1992-04-12 ≈ 133.2° (Meeus)','exp':133.2,'tol':3.0,'angle':True},
        # ── 6. planetPos — all 8 planets in [0,360) ───────────────────────────
        *[{'fn':'planetPos','args':[p,0.0],'name':f'planetPos {p} at J2000 ∈ [0,360)','range':[0,360]}
          for p in ['Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']],
        # planetPos reference values at J2000 epoch (2000-01-01 12:00 TT)
        {'fn':'planetPos','args':['Mercury',0.0],'name':'planetPos Mercury J2000 ≈ 271.2°','exp':271.2,'tol':1.5,'angle':True},
        {'fn':'planetPos','args':['Venus',0.0],'name':'planetPos Venus J2000 ≈ 241.3°','exp':241.3,'tol':1.5,'angle':True},
        {'fn':'planetPos','args':['Mars',0.0],'name':'planetPos Mars J2000 ≈ 327.2°','exp':327.2,'tol':1.5,'angle':True},
        {'fn':'planetPos','args':['Jupiter',0.0],'name':'planetPos Jupiter J2000 ≈ 25.3°','exp':25.3,'tol':3.0,'angle':True},
        {'fn':'planetPos','args':['Saturn',0.0],'name':'planetPos Saturn J2000 ≈ 40.4°','exp':40.4,'tol':4.0,'angle':True},
        {'fn':'planetPos','args':['Uranus',0.0],'name':'planetPos Uranus J2000 ≈ 314.8°','exp':314.8,'tol':3.0,'angle':True},
        {'fn':'planetPos','args':['Neptune',0.0],'name':'planetPos Neptune J2000 ≈ 303.5°','exp':303.5,'tol':2.0,'angle':True},
        {'fn':'planetPos','args':['Pluto',0.0],'name':'planetPos Pluto J2000 ≈ 251.4°','exp':251.4,'tol':3.0,'angle':True},
        # ── 7. ASPECTS constant ───────────────────────────────────────────────
        {'fn':'getAspectsConst','args':[],'name':'ASPECTS: exactly 6 entries','check':'asp_count'},
        {'fn':'getAspectsConst','args':[],'name':'ASPECTS: names correct','check':'asp_names',
         'exp_names':['Conjunction','Sextile','Square','Trine','Quincunx','Opposition']},
        {'fn':'getAspectsConst','args':[],'name':'ASPECTS: angles correct [0,60,90,120,150,180]','check':'asp_angles',
         'exp_angles':[0,60,90,120,150,180]},
        {'fn':'getAspectsConst','args':[],'name':'ASPECTS: orbs correct [8,6,8,8,3,8]','check':'asp_orbs',
         'exp_orbs':[8,6,8,8,3,8]},
        {'fn':'getAspectsConst','args':[],'name':'ASPECTS: h values [1.0,0.7,-0.8,0.9,-0.3,-0.7]','check':'asp_h_vals',
         'exp_h':[1.0,0.7,-0.8,0.9,-0.3,-0.7]},
        {'fn':'getAspectsConst','args':[],'name':'ASPECTS: symbols [☌,⚹,□,△,⚻,☍]','check':'asp_syms',
         'exp_syms':['☌','⚹','□','△','⚻','☍']},
        # ── 8. ZSIGNS / ZSYMS ─────────────────────────────────────────────────
        {'fn':'getZSIGNS','args':[],'name':'ZSIGNS: 12 signs correct order','check':'zsigns'},
        {'fn':'getZSYMS','args':[],'name':'ZSYMS: 12 symbols','check':'zsyms_count'},
        # ── 9. degSign — all 12 sign boundaries ───────────────────────────────
        *[{'fn':'degSign','args':[i*30.0],'name':f'degSign({i*30}°) = {s}','check':'sign_exact','exp_sign':s}
          for i,s in enumerate(EXPECTED_ZSIGNS)],
        # Last degree of each sign still in sign
        *[{'fn':'degSign','args':[i*30+29.9],'name':f'degSign({i*30+29.9}°) still in {s}','check':'sign_exact','exp_sign':s}
          for i,s in enumerate(EXPECTED_ZSIGNS)],
        # Degree within sign
        {'fn':'degSign','args':[45.7],'name':'degSign(45.7°) deg = 15.7','check':'deg_exact','exp_deg':15.7},
        {'fn':'degSign','args':[0.0],'name':'degSign(0°) deg = 0','check':'deg_exact','exp_deg':0.0},
        {'fn':'degSign','args':[30.0],'name':'degSign(30°) deg = 0 (next sign)','check':'deg_exact','exp_deg':0.0},
        {'fn':'degSign','args':[359.9],'name':'degSign(359.9°) = Pisces','check':'sign_exact','exp_sign':'Pisces'},
        # sym pass-through
        {'fn':'degSign','args':[0.0],'name':'degSign(0°) sym = ♈','check':'sym_exact','exp_sym':'♈'},
        {'fn':'degSign','args':[30.0],'name':'degSign(30°) sym = ♉','check':'sym_exact','exp_sym':'♉'},
        {'fn':'degSign','args':[60.0],'name':'degSign(60°) sym = ♊','check':'sym_exact','exp_sym':'♊'},
        # lon pass-through
        {'fn':'degSign','args':[123.456],'name':'degSign(123.456°) lon = 123.456','check':'lon_exact','exp_lon':123.456},
        # ── 10. ascPos(T, lat, lon) ───────────────────────────────────────────
        {'fn':'ascPos','args':[0.0,42.0,0.0],'name':'ascPos GMST at J2000 ≈ 280.46°','check':'gmst_j2000'},
        {'fn':'ascPos','args':[0.0,42.0,0.0],'name':'ascPos obliquity ε at J2000 ≈ 23.44°','check':'eps_j2000'},
        {'fn':'ascPos','args':[T('2000-01-01'),48.9,2.35],'name':'ascPos lon ∈ [0,360) Paris','check':'asc_range'},
        {'fn':'ascPos','args':[T('2000-06-15'),51.5,-0.12],'name':'ascPos lon ∈ [0,360) London','check':'asc_range'},
        {'fn':'ascPos','args':[T('2000-06-15'),-33.9,151.2],'name':'ascPos lon ∈ [0,360) Sydney','check':'asc_range'},
        {'fn':'ascPos','args':[T('2000-06-15'),0.0,0.0],'name':'ascPos lon ∈ [0,360) equator/Greenwich','check':'asc_range'},
        {'fn':'ascPos','args':[0.0,51.5,-0.12],'name':'ascPos lat stored = 51.5','check':'asc_lat','exp_lat':51.5},
        {'fn':'ascPos','args':[0.0,42.0,30.0],'name':'ascPos lon=30° → LST = GMST+30','check':'asc_lst_offset','exp_lon':30.0},
        {'fn':'ascPos','args':[0.0,0.0,0.0],'name':'ascPos J2000 equator/Greenwich ≈ 11°','check':'asc_ref','exp_asc':11.38,'tol':2.0},
        {'fn':'ascPos','args':[0.0,48.9,2.35],'name':'ascPos J2000 Paris ≈ 26.8°','check':'asc_ref','exp_asc':26.8,'tol':2.0},
        {'fn':'ascPos','args':[0.0,59.3,18.07],'name':'ascPos J2000 Stockholm','check':'asc_range'},
        {'fn':'ascPos','args':[0.0,-34.6,-58.38],'name':'ascPos J2000 Buenos Aires','check':'asc_range'},
        {'fn':'ascPos','args':[0.0,42.0,0.0],'name':'ascPos lon=0 for diff test','check':'asc_store','store_key':'asc_lon0'},
        {'fn':'ascPos','args':[0.0,42.0,90.0],'name':'ascPos lon=90 differs from lon=0','check':'asc_diff_lon','ref_key':'asc_lon0'},
        # ── 11. SW weight table (all 26 keys) ─────────────────────────────────
        *[{'fn':'getSWVal','args':[k],'name':f'SW[{k}] = {v}','check':'sw_val','exp_sw':v}
          for k,v in [
              ('Sun-Moon',1.8),('Moon-Sun',1.8),('Venus-Mars',1.6),('Mars-Venus',1.6),
              ('Sun-Venus',1.5),('Venus-Sun',1.5),('Moon-Venus',1.4),('Venus-Moon',1.4),
              ('Sun-Mars',1.3),('Mars-Sun',1.3),('Ascendant-Moon',1.3),('Moon-Ascendant',1.3),
              ('Ascendant-Sun',1.2),('Sun-Ascendant',1.2),('Moon-Mars',1.2),('Mars-Moon',1.2),
              ('Venus-Venus',1.0),('Sun-Sun',0.9),('Moon-Moon',0.9),
              ('Mercury-Mercury',0.8),('Mars-Mars',0.7),('Jupiter-Sun',0.7),('Jupiter-Moon',0.7),
              ('Saturn-Venus',0.7),('Saturn-Sun',0.6),('Saturn-Moon',0.6),
          ]],
        # ── 12. SD domain keys ────────────────────────────────────────────────
        {'fn':'getSDDomains','args':[],'name':'SD: exactly 5 domains','check':'sd_domains'},
        {'fn':'getSDKeys','args':['love'],'name':'SD love includes Venus-Mars','check':'sd_has','exp_key':'Venus-Mars'},
        {'fn':'getSDKeys','args':['love'],'name':'SD love includes Sun-Moon','check':'sd_has','exp_key':'Sun-Moon'},
        {'fn':'getSDKeys','args':['harmony'],'name':'SD harmony includes Sun-Sun','check':'sd_has','exp_key':'Sun-Sun'},
        {'fn':'getSDKeys','args':['harmony'],'name':'SD harmony includes Jupiter-Moon','check':'sd_has','exp_key':'Jupiter-Moon'},
        {'fn':'getSDKeys','args':['passion'],'name':'SD passion includes Mars-Sun','check':'sd_has','exp_key':'Mars-Sun'},
        {'fn':'getSDKeys','args':['mental'],'name':'SD mental includes Mercury-Mercury','check':'sd_has','exp_key':'Mercury-Mercury'},
        {'fn':'getSDKeys','args':['mental'],'name':'SD mental includes Mercury-Moon','check':'sd_has','exp_key':'Mercury-Moon'},
        {'fn':'getSDKeys','args':['karmic'],'name':'SD karmic includes Saturn-Sun','check':'sd_has','exp_key':'Saturn-Sun'},
        {'fn':'getSDKeys','args':['karmic'],'name':'SD karmic includes Ascendant-Moon','check':'sd_has','exp_key':'Ascendant-Moon'},
        # New outer-planet SW weights
        {'fn':'getSWVal','args':['Pluto-Moon'],'name':'SW[Pluto-Moon] = 1.1','check':'sw_val','exp_sw':1.1},
        {'fn':'getSWVal','args':['Moon-Pluto'],'name':'SW[Moon-Pluto] = 1.1','check':'sw_val','exp_sw':1.1},
        {'fn':'getSWVal','args':['Pluto-Sun'],'name':'SW[Pluto-Sun] = 1.0','check':'sw_val','exp_sw':1.0},
        {'fn':'getSWVal','args':['Uranus-Moon'],'name':'SW[Uranus-Moon] = 0.9','check':'sw_val','exp_sw':0.9},
        {'fn':'getSWVal','args':['Neptune-Venus'],'name':'SW[Neptune-Venus] = 0.8','check':'sw_val','exp_sw':0.8},
        {'fn':'getSWVal','args':['Uranus-Uranus'],'name':'SW[Uranus-Uranus] = 0.3 (generational)','check':'sw_val','exp_sw':0.3},
        {'fn':'getSWVal','args':['Neptune-Neptune'],'name':'SW[Neptune-Neptune] = 0.3 (generational)','check':'sw_val','exp_sw':0.3},
        {'fn':'getSWVal','args':['Pluto-Pluto'],'name':'SW[Pluto-Pluto] = 0.3 (generational)','check':'sw_val','exp_sw':0.3},
        # New outer-planet SD domain entries
        {'fn':'getSDKeys','args':['love'],'name':'SD love includes Neptune-Venus','check':'sd_has','exp_key':'Neptune-Venus'},
        {'fn':'getSDKeys','args':['love'],'name':'SD love includes Neptune-Moon','check':'sd_has','exp_key':'Neptune-Moon'},
        {'fn':'getSDKeys','args':['harmony'],'name':'SD harmony includes Neptune-Sun','check':'sd_has','exp_key':'Neptune-Sun'},
        {'fn':'getSDKeys','args':['passion'],'name':'SD passion includes Pluto-Venus','check':'sd_has','exp_key':'Pluto-Venus'},
        {'fn':'getSDKeys','args':['mental'],'name':'SD mental includes Uranus-Mercury','check':'sd_has','exp_key':'Uranus-Mercury'},
        {'fn':'getSDKeys','args':['mental'],'name':'SD mental includes Uranus-Sun','check':'sd_has','exp_key':'Uranus-Sun'},
        {'fn':'getSDKeys','args':['karmic'],'name':'SD karmic includes Pluto-Moon','check':'sd_has','exp_key':'Pluto-Moon'},
        {'fn':'getSDKeys','args':['karmic'],'name':'SD karmic includes Pluto-Sun','check':'sd_has','exp_key':'Pluto-Sun'},
        {'fn':'getSDKeys','args':['karmic'],'name':'SD karmic includes Pluto-Ascendant','check':'sd_has','exp_key':'Pluto-Ascendant'},
        {'fn':'getSDKeys','args':['karmic'],'name':'SD karmic includes Saturn-Pluto','check':'sd_has','exp_key':'Saturn-Pluto'},
        # ── 13. getAspect — all 6 types ───────────────────────────────────────
        {'fn':'getAspect','args':[0.0,0.0],'name':'getAspect(0°,0°) = Conjunction','check':'asp_name','exp':'Conjunction'},
        {'fn':'getAspect','args':[0.0,60.0],'name':'getAspect(0°,60°) = Sextile','check':'asp_name','exp':'Sextile'},
        {'fn':'getAspect','args':[0.0,90.0],'name':'getAspect(0°,90°) = Square','check':'asp_name','exp':'Square'},
        {'fn':'getAspect','args':[0.0,120.0],'name':'getAspect(0°,120°) = Trine','check':'asp_name','exp':'Trine'},
        {'fn':'getAspect','args':[0.0,150.0],'name':'getAspect(0°,150°) = Quincunx','check':'asp_name','exp':'Quincunx'},
        {'fn':'getAspect','args':[0.0,180.0],'name':'getAspect(0°,180°) = Opposition','check':'asp_name','exp':'Opposition'},
        # h values for each aspect
        {'fn':'getAspect','args':[0.0,0.0],'name':'Conjunction h = 1.0','check':'asp_h','exp_h':1.0},
        {'fn':'getAspect','args':[0.0,60.0],'name':'Sextile h = 0.7','check':'asp_h','exp_h':0.7},
        {'fn':'getAspect','args':[0.0,90.0],'name':'Square h = -0.8','check':'asp_h','exp_h':-0.8},
        {'fn':'getAspect','args':[0.0,120.0],'name':'Trine h = 0.9','check':'asp_h','exp_h':0.9},
        {'fn':'getAspect','args':[0.0,150.0],'name':'Quincunx h = -0.3','check':'asp_h','exp_h':-0.3},
        {'fn':'getAspect','args':[0.0,180.0],'name':'Opposition h = -0.7','check':'asp_h','exp_h':-0.7},
        # sym values
        {'fn':'getAspect','args':[0.0,0.0],'name':'Conjunction sym = ☌','check':'asp_sym','exp_sym':'☌'},
        {'fn':'getAspect','args':[0.0,60.0],'name':'Sextile sym = ⚹','check':'asp_sym','exp_sym':'⚹'},
        {'fn':'getAspect','args':[0.0,90.0],'name':'Square sym = □','check':'asp_sym','exp_sym':'□'},
        {'fn':'getAspect','args':[0.0,120.0],'name':'Trine sym = △','check':'asp_sym','exp_sym':'△'},
        {'fn':'getAspect','args':[0.0,150.0],'name':'Quincunx sym = ⚻','check':'asp_sym','exp_sym':'⚻'},
        {'fn':'getAspect','args':[0.0,180.0],'name':'Opposition sym = ☍','check':'asp_sym','exp_sym':'☍'},
        # orb_actual precision
        {'fn':'getAspect','args':[0.0,3.5],'name':'Conjunction orb_actual = 3.50','check':'asp_orb_actual','exp_orb':3.5},
        {'fn':'getAspect','args':[0.0,122.0],'name':'Trine orb_actual = 2.00','check':'asp_orb_actual','exp_orb':2.0},
        {'fn':'getAspect','args':[0.0,57.5],'name':'Sextile orb_actual = 2.50','check':'asp_orb_actual','exp_orb':2.5},
        # diff field
        {'fn':'getAspect','args':[0.0,58.0],'name':'Sextile diff field = 58.0','check':'asp_diff','exp_diff':58.0},
        {'fn':'getAspect','args':[357.0,3.0],'name':'Conjunction diff via wrap (357°/3° → d=6°) = 6.0','check':'asp_diff','exp_diff':6.0},
        # Orb boundaries — inside
        {'fn':'getAspect','args':[0.0,7.99],'name':'Conjunction inside 8° orb','check':'asp_name','exp':'Conjunction'},
        {'fn':'getAspect','args':[0.0,62.99],'name':'Sextile inside 6° orb','check':'asp_name','exp':'Sextile'},
        {'fn':'getAspect','args':[0.0,152.99],'name':'Quincunx inside 3° orb','check':'asp_name','exp':'Quincunx'},
        # Orb boundaries — outside
        {'fn':'getAspect','args':[0.0,8.01],'name':'8.01° outside all orbs = null','check':'asp_null'},
        {'fn':'getAspect','args':[0.0,66.01],'name':'66.01° outside Sextile = null','check':'asp_null'},
        {'fn':'getAspect','args':[0.0,153.01],'name':'153.01° outside Quincunx = null','check':'asp_null'},
        # Symmetry (swap A↔B)
        {'fn':'getAspect','args':[120.0,0.0],'name':'Symmetric (120°,0°) = Trine','check':'asp_name','exp':'Trine'},
        {'fn':'getAspect','args':[180.0,0.0],'name':'Symmetric (180°,0°) = Opposition','check':'asp_name','exp':'Opposition'},
        # Wrap-around (across 0°/360°)
        {'fn':'getAspect','args':[350.0,10.0],'name':'Wrap 350°/10° → diff=20° → null','check':'asp_null'},
        {'fn':'getAspect','args':[356.0,3.0],'name':'Wrap 356°/3° → diff=7° → Conjunction','check':'asp_name','exp':'Conjunction'},
        {'fn':'getAspect','args':[358.0,2.0],'name':'Wrap 358°/2° → diff=4° → Conjunction','check':'asp_name','exp':'Conjunction'},
        {'fn':'getAspect','args':[1.0,359.0],'name':'Wrap 1°/359° → diff=2° → Conjunction','check':'asp_name','exp':'Conjunction'},
        # ── 14. buildChart ────────────────────────────────────────────────────
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,None],'name':'buildChart timeUnknown=false','check':'bc_tu','exp_tu':False},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,True,None],'name':'buildChart timeUnknown=true','check':'bc_tu','exp_tu':True},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,None],'name':'buildChart lat defaults to 42','check':'bc_lat','exp_lat':42},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,51.5],'name':'buildChart lat=51.5 stored','check':'bc_lat','exp_lat':51.5},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,None],'name':'buildChart: exactly 11 positions','check':'bc_n11'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: Ascendant in planets list','check':'bc_has_asc'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: Sun in Capricorn 2000-01-01','check':'bc_sun_sign','exp_sign':'Capricorn'},
        {'fn':'buildChart','args':['2000-03-21','12:00',0,False,42],'name':'buildChart: Sun in Aries 2000-03-21','check':'bc_sun_sign','exp_sign':'Aries'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: all 11 lons in [0,360)','check':'bc_lons_valid'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: all planets have lon/sign/deg/sym','check':'bc_pos_fields'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: trace has ≥ 10 rows','check':'bc_trace'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: JD ≈ 2451545','check':'bc_jd'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,42],'name':'buildChart: T ≈ 0','check':'bc_T'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,48.9,2.35],'name':'buildChart Paris (lon=2.35): Ascendant valid','check':'bc_lons_valid'},
        {'fn':'buildChart','args':['2000-01-01','12:00',0,False,-33.9,151.2],'name':'buildChart Sydney (lon=151.2): Ascendant valid','check':'bc_lons_valid'},
        # ── 15. buildSynastry ─────────────────────────────────────────────────
        {'fn':'buildSynastry','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'buildSynastry: exactly 121 pairs (11×11)','check':'syn_pairs'},
        {'fn':'buildSynastry','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'buildSynastry: all pairs have pA/pB/lA/lB/sA/sB/slowA/slowB','check':'syn_fields'},
        {'fn':'buildSynastry','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'buildSynastry: nAspects ∈ [0,121]','check':'syn_asp_range'},
        {'fn':'buildSynastry','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'buildSynastry: all aspect h values ∈ [-1,1]','check':'syn_h_range'},
        {'fn':'buildSynastry','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'buildSynastry: all orb_actual ≥ 0','check':'syn_orb_pos'},
        {'fn':'buildSynastry','args':['2000-01-01','12:00',0,42,0,'2000-01-01','12:00',0,42,0],
         'name':'buildSynastry self: 11 exact same-planet Conjunctions','check':'syn_self'},
        {'fn':'buildSynastry','args':['2000-01-01','12:00',0,42,0,'2000-01-01','12:00',0,42,0],
         'name':'buildSynastry self: same-planet Conjunction orb = 0.00','check':'syn_self_orb'},
        {'fn':'buildSynastry','args':['2000-01-01','12:00',0,42,0,'2000-01-01','12:00',0,42,0],
         'name':'buildSynastry: Uranus/Neptune/Pluto pairs carry slowA or slowB=true','check':'syn_slow_flag'},
        # ── 16. scoreSyn — all 6 domains ──────────────────────────────────────
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn couple A: overall=57 (frozen)','check':'score_val','domain':'overall','exp_score':57},
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn couple A: love=60 (frozen)','check':'score_val','domain':'love','exp_score':60},
        {'fn':'scoreSyn','args':['1990-03-21','12:00',0,42,0,'1988-07-15','12:00',0,42,0],
         'name':'scoreSyn couple B: all 6 domains in [0,100]','check':'scores_range'},
        {'fn':'scoreSyn','args':['1990-03-21','12:00',0,42,0,'1988-07-15','12:00',0,42,0],
         'name':'scoreSyn couple B: exactly 6 domain keys','check':'score_keys'},
        {'fn':'scoreSynFormula','args':[],'name':'scoreSyn self: harmony=100 (norm formula s==m)','check':'formula_harm'},
        {'fn':'scoreSynFormula','args':[],'name':'scoreSyn self: overall > 50 (conjunctions dominate)','check':'formula_ov'},
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn: details array non-empty','check':'score_details'},
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn: detail records have key/asp/h/w/c','check':'score_detail_fields'},
        # ── 17. computeConf ───────────────────────────────────────────────────
        {'fn':'computeConf','args':['1990-03-21','12:00',0,False,42,0,'1988-07-15','12:00',0,False,42,0],
         'name':'computeConf: global ∈ [0,100]','check':'conf_range','key':'global'},
        {'fn':'computeConf','args':['1990-03-21','12:00',0,False,42,0,'1988-07-15','12:00',0,False,42,0],
         'name':'computeConf: astro ∈ [0,100]','check':'conf_range','key':'astro'},
        {'fn':'computeConf','args':['1990-03-21','12:00',0,False,42,0,'1988-07-15','12:00',0,False,42,0],
         'name':'computeConf: coher ∈ [0,100]','check':'conf_range','key':'coher'},
        {'fn':'computeConf','args':['1990-03-21','12:00',0,True,42,0,'1988-07-15','12:00',0,False,42,0],
         'name':'computeConf: one TU → astro ≤ 85','check':'conf_one_tu'},
        {'fn':'computeConf','args':['1990-03-21','12:00',0,True,42,0,'1988-07-15','12:00',0,True,42,0],
         'name':'computeConf: both TU → astro ≤ 70','check':'conf_two_tu'},
        {'fn':'computeConf','args':['1990-03-21','12:00',0,False,42,0,'1988-07-15','12:00',0,False,42,0],
         'name':'computeConf: found ≥ 0','check':'conf_found'},
        {'fn':'computeConf','args':['1990-03-21','12:00',0,False,42,0,'1988-07-15','12:00',0,False,42,0],
         'name':'computeConf: global = round(astro×0.50 + coher×0.50)','check':'conf_formula'},

        # ── 18. buildNatalAspects ──────────────────────────────────────────────
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: returns list (≥0 aspects)','check':'nat_asp_range'},
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: all records have pA/pB/asp/lA/lB','check':'nat_asp_fields'},
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: all h values ∈ [-1,1]','check':'nat_asp_h'},
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: all orbs ≥ 0','check':'nat_asp_orb'},
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: no duplicate pairs (upper-triangle only)','check':'nat_asp_nodup'},
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: nAspects ≤ 55 (upper-triangle)','check':'nat_asp_max'},
        {'fn':'buildNatalAspects','args':['2000-01-01','12:00',0,False,42],
         'name':'buildNatalAspects: Uranus aspects have slowA or slowB=true','check':'nat_asp_slow'},

        # ── 19. lunarPhase ─────────────────────────────────────────────────────
        {'fn':'lunarPhase','args':['2000-03-06','12:00',0,42],
         'name':'lunarPhase: 2000-03-06 New Moon → idx=0','check':'lunar_idx','exp_idx':0},
        {'fn':'lunarPhase','args':['2000-01-21','12:00',0,42],
         'name':'lunarPhase: 2000-01-21 near Full Moon → idx=4','check':'lunar_idx','exp_idx':4},
        {'fn':'lunarPhase','args':['2000-06-15','12:00',0,42],
         'name':'lunarPhase: angle ∈ [0,360)','check':'lunar_angle_range'},
        {'fn':'lunarPhase','args':['2000-01-01','12:00',0,42],
         'name':'lunarPhase: EN/FR/IT names all non-empty','check':'lunar_langs'},
        {'fn':'lunarPhase','args':['1980-04-21','12:00',0,42],
         'name':'lunarPhase: idx ∈ [0,7]','check':'lunar_idx_range'},

        # ── 20. elementTally ───────────────────────────────────────────────────
        {'fn':'elementTally','args':['2000-01-01','12:00',0,42],
         'name':'elementTally: total = 11 (10 planets + Ascendant)','check':'elem_total'},
        {'fn':'elementTally','args':['2000-01-01','12:00',0,42],
         'name':'elementTally: has Fire/Earth/Air/Water keys','check':'elem_keys'},
        {'fn':'elementTally','args':['2000-01-01','12:00',0,42],
         'name':'elementTally: all counts ≥ 0','check':'elem_nonneg'},

        # ── 21. modalityTally ──────────────────────────────────────────────────
        {'fn':'modalityTally','args':['2000-01-01','12:00',0,42],
         'name':'modalityTally: total = 11','check':'mod_total'},
        {'fn':'modalityTally','args':['2000-01-01','12:00',0,42],
         'name':'modalityTally: has Cardinal/Fixed/Mutable keys','check':'mod_keys'},

        # ── 22. dignityScores ──────────────────────────────────────────────────
        {'fn':'dignityScores','args':['2000-01-01','12:00',0,42],
         'name':'dignityScores: returns 10 planet entries','check':'dig_count'},
        {'fn':'dignityScores','args':['2000-01-01','12:00',0,42],
         'name':'dignityScores: all scores ∈ {-2,-1,0,1,2}','check':'dig_scores'},
        {'fn':'dignityScores','args':['1990-03-21','12:00',0,42],
         'name':'dignityScores: Sun in Aries = exaltation (score=1)','check':'dig_sun_aries'},
        {'fn':'dignityScores','args':['1990-08-01','12:00',0,42],
         'name':'dignityScores: Sun in Leo = domicile (score=2)','check':'dig_sun_leo'},
        {'fn':'dignityScores','args':['2000-01-01','12:00',0,42],
         'name':'dignityScores: Sun in Capricorn/Aquarius boundary → score in {-2,0}','check':'dig_sun_cap'},
        {'fn':'dignityScores','args':['1990-03-21','12:00',0,42],
         'name':'dignityScores: non-zero entries have non-empty label','check':'dig_labels'},

        # ── 23. retrogradeFlags ────────────────────────────────────────────────
        {'fn':'retrogradeFlags','args':['2000-01-01','12:00',0,42],
         'name':'retrogradeFlags: returns 8 planet entries (no Sun/Moon)','check':'retro_count'},
        {'fn':'retrogradeFlags','args':['2000-01-01','12:00',0,42],
         'name':'retrogradeFlags: all values are boolean','check':'retro_bool'},
        {'fn':'retrogradeFlags','args':['2000-01-01','12:00',0,42],
         'name':'retrogradeFlags: Sun and Moon excluded','check':'retro_no_sun_moon'},
        {'fn':'retrogradeFlags','args':['1990-06-01','12:00',0,42],
         'name':'retrogradeFlags: Pluto retrograde 1990-06-01','check':'retro_pluto_1990'},
        {'fn':'retrogradeFlags','args':['2000-07-17','12:00',0,42],
         'name':'retrogradeFlags: Mercury retrograde 2000-07-17','check':'retro_mercury_2000'},

        # ── 24. buildNatalProfile (integration) ───────────────────────────────
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: returns all required fields','check':'profile_fields'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: element total = 11','check':'profile_elem_total'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: modality total = 11','check':'profile_mod_total'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: lunarPhase has EN/FR/IT names','check':'profile_lunar_langs'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: nAspects ≤ 55','check':'profile_asp_max'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: Sun in Aries dignity = exaltation','check':'profile_sun_dignity'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: JD matches buildChart JD','check':'profile_jd'},
        {'fn':'buildNatalProfile','args':['1990-03-21','14:30',1,False,48.9],
         'name':'buildNatalProfile: lat stored = 48.9','check':'profile_lat'},
        {'fn':'buildNatalProfile','args':['1990-03-21','12:00',0,True,48.9],
         'name':'buildNatalProfile: timeUnknown=true stored','check':'profile_tu'},

        # ── 25. builtinNatalReport ────────────────────────────────────────────
        {'fn':'builtinNatalReport','args':['1990-03-21','14:30',1,False,48.9,2.35,'en'],
         'name':'builtinNatalReport EN: non-empty text with ### headings','check':'natal_report_basic',
         'name_arg':'Aries'},
        {'fn':'builtinNatalReport','args':['1990-03-21','14:30',1,False,48.9,2.35,'fr'],
         'name':'builtinNatalReport FR: contains French language content','check':'natal_report_lang',
         'name_arg':'Bélier'},
        {'fn':'builtinNatalReport','args':['1990-03-21','14:30',1,False,48.9,2.35,'it'],
         'name':'builtinNatalReport IT: contains Italian language content','check':'natal_report_lang',
         'name_arg':'Ariete'},
        {'fn':'builtinNatalReport','args':['1990-03-21','12:00',0,True,48.9,2.35,'en'],
         'name':'builtinNatalReport: timeUnknown → warns about Moon/Ascendant','check':'natal_report_tu_warn',
         'name_arg':'TestTU'},

        # ── 26. More Moon reference values ────────────────────────────────────
        {'fn':'moonPos','args':[T('2000-01-01')],'name':'moonPos J2000 ≈ 223.3° (JPL)','exp':223.3,'tol':1.0,'angle':True},
        {'fn':'moonPos','args':[T('2010-06-21')],'name':'moonPos 2010-06-21 ≈ 209.9° (JPL)','exp':209.9,'tol':1.0,'angle':True},
        {'fn':'moonPos','args':[T('1980-04-21')],'name':'moonPos 1980-04-21 ≈ 114.3° (JPL)','exp':114.3,'tol':1.0,'angle':True},

        # ── 27. Timezone handling ─────────────────────────────────────────────
        {'fn':'toJD','args':[2000,1,1,12,-5],'name':'toJD: tz=-5 shifts JD by +5/24','exp':2451545.0+5/24,'tol':1e-4},
        {'fn':'toJD','args':[2000,1,1,0,0],'name':'toJD: midnight = JD - 0.5','exp':2451544.5,'tol':1e-4},
        {'fn':'toJD','args':[2000,1,1,23,0],'name':'toJD: 23:00 UTC','exp':2451545.0+11/24,'tol':1e-4},

        # ── 28. Additional synastry score domain range checks ─────────────────
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn couple A: harmony ∈ [0,100]','check':'score_val_range','domain':'harmony'},
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn couple A: passion ∈ [0,100]','check':'score_val_range','domain':'passion'},
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn couple A: mental ∈ [0,100]','check':'score_val_range','domain':'mental'},
        {'fn':'scoreSyn','args':['1980-04-21','12:00',0,42,0,'1982-08-13','12:00',0,42,0],
         'name':'scoreSyn couple A: karmic ∈ [0,100]','check':'score_val_range','domain':'karmic'},
    ]


_CASES = _build_cases()


@pytest.fixture(scope="module")
def unit_results(engine_js, node_bin):
    raw = run_node(node_bin, engine_js, NODE_UNIT_SHIM, [json.dumps(_CASES)])
    return list(zip(_CASES, json.loads(raw)))


@pytest.fixture(scope="module")
def asc_store(unit_results):
    store = {}
    for case, nr in unit_results:
        if case.get('check') == 'asc_store':
            got_raw = nr.get('got')
            if got_raw and got_raw != 'null':
                p = json.loads(got_raw)
                store[case.get('store_key', '')] = p.get('lon')
    return store


def evaluate_unit_case(case, nr, asc_store):
    """Evaluate a single unit test case. Returns (passed: bool, detail: str)."""
    got_raw = nr.get('got')
    check = case.get('check')

    def _p():
        return json.loads(got_raw) if got_raw and got_raw != 'null' else None

    # ── Numeric / range (no explicit check) ──────────────────────────────
    if check is None and case.get('range'):
        got = float(got_raw); lo, hi = case['range']
        return (lo <= got < hi, f"got {got:.3f}, [{lo},{hi})")
    elif check is None:
        got = float(got_raw); exp = case['exp']; tol = case.get('tol', 0.001)
        diff = ang_diff(got, exp) if case.get('angle') else abs(got - exp)
        return (diff <= tol, f"got {got:.5f}, exp {exp}, d={diff:.5f}")

    # ── Named checks ─────────────────────────────────────────────────────
    elif check == 'asp_count':
        p = _p(); ok = isinstance(p, list) and len(p) == 6; detail = f"len={len(p) if p else None}"
    elif check == 'asp_names':
        p = _p(); names = [a['name'] for a in (p or [])]; ok = names == case['exp_names']; detail = f"{names}"
    elif check == 'asp_angles':
        p = _p(); angles = [a['angle'] for a in (p or [])]; ok = angles == case['exp_angles']; detail = f"{angles}"
    elif check == 'asp_orbs':
        p = _p(); orbs = [a['orb'] for a in (p or [])]; ok = orbs == case['exp_orbs']; detail = f"{orbs}"
    elif check == 'asp_h_vals':
        p = _p(); hs = [a['h'] for a in (p or [])]
        ok = len(hs) == 6 and all(abs(hs[i] - case['exp_h'][i]) < 1e-9 for i in range(6)); detail = f"{hs}"
    elif check == 'asp_syms':
        p = _p(); syms = [a['sym'] for a in (p or [])]; ok = syms == case['exp_syms']; detail = f"{syms}"
    elif check == 'zsigns':
        p = _p(); exp = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
        ok = p == exp; detail = f"{p}"
    elif check == 'zsyms_count':
        p = _p(); ok = isinstance(p, list) and len(p) == 12; detail = f"len={len(p) if p else None}"
    elif check == 'sign_exact':
        p = _p(); sign = p.get('sign') if p else None; ok = sign == case['exp_sign']; detail = f"sign={sign!r}"
    elif check == 'deg_exact':
        p = _p(); deg = p.get('deg') if p else None; ok = deg is not None and abs(deg - case['exp_deg']) < 0.05; detail = f"deg={deg}"
    elif check == 'sym_exact':
        p = _p(); sym = p.get('sym') if p else None; ok = sym == case['exp_sym']; detail = f"sym={sym!r}"
    elif check == 'lon_exact':
        p = _p(); lon = p.get('lon') if p else None; ok = lon is not None and abs(lon - case['exp_lon']) < 0.001; detail = f"lon={lon}"
    elif check == 'gmst_j2000':
        p = _p(); gmst = p.get('gmst') if p else None; ok = gmst is not None and abs(gmst - 280.46) < 0.5; detail = f"GMST={gmst}"
    elif check == 'eps_j2000':
        p = _p(); eps = p.get('eps') if p else None; ok = eps is not None and abs(eps - 23.44) < 0.01; detail = f"eps={eps}"
    elif check == 'asc_range':
        p = _p(); lon = p.get('lon') if p else None; ok = lon is not None and 0 <= lon < 360; detail = f"lon={lon}"
    elif check == 'asc_lat':
        p = _p(); lat = p.get('lat') if p else None; ok = lat is not None and abs(lat - case['exp_lat']) < 0.001; detail = f"lat={lat}"
    elif check == 'asc_lst_offset':
        p = _p(); gmst = p.get('gmst'); lst = p.get('lst')
        exp_lon = case['exp_lon']
        if gmst is not None and lst is not None:
            diff = lst - gmst
            if diff < -180: diff += 360
            if diff > 180: diff -= 360
            ok = abs(diff - exp_lon) < 0.01; detail = f"LST={lst}, GMST={gmst}, diff={diff:.2f}, exp_lon={exp_lon}"
        else:
            ok = False; detail = "missing gmst/lst"
    elif check == 'asc_ref':
        p = _p(); lon = p.get('lon') if p else None; tol = case.get('tol', 2.0)
        ok = lon is not None and abs(lon - case['exp_asc']) < tol; detail = f"asc={lon}, exp~{case['exp_asc']}+/-{tol}"
    elif check == 'asc_store':
        p = _p(); lon = p.get('lon') if p else None; ok = lon is not None and 0 <= lon < 360; detail = f"stored lon={lon}"
    elif check == 'asc_diff_lon':
        p = _p(); lon = p.get('lon') if p else None; ref = asc_store.get(case.get('ref_key', ''))
        if lon is not None and ref is not None:
            ok = abs(lon - ref) > 1.0; detail = f"lon={lon}, ref={ref}, diff={abs(lon - ref):.2f} (expect >1)"
        else:
            ok = False; detail = f"lon={lon}, ref={ref}"
    elif check == 'sw_val':
        v = float(got_raw) if got_raw not in (None, 'null') else None; ok = v is not None and abs(v - case['exp_sw']) < 1e-6; detail = f"SW={v}, exp={case['exp_sw']}"
    elif check == 'sd_domains':
        p = _p(); ok = set(p or []) == {'love','harmony','passion','mental','karmic'}; detail = f"{p}"
    elif check == 'sd_has':
        p = _p(); ok = case['exp_key'] in (p or []); detail = f"{case['exp_key']} in {p}"
    elif check == 'asp_name':
        p = _p(); ng = p.get('name') if p else None; ok = ng == case['exp']; detail = f"asp={ng!r}"
    elif check == 'asp_null':
        ok = got_raw == 'null'; detail = f"got {got_raw!r}"
    elif check == 'asp_h':
        p = _p(); h = p.get('h') if p else None; ok = h is not None and abs(h - case['exp_h']) < 1e-9; detail = f"h={h}, exp={case['exp_h']}"
    elif check == 'asp_sym':
        p = _p(); sym = p.get('sym') if p else None; ok = sym == case['exp_sym']; detail = f"sym={sym!r}"
    elif check == 'asp_orb_actual':
        p = _p(); orb = p.get('orb_actual') if p else None; ok = orb is not None and abs(orb - case['exp_orb']) < 0.01; detail = f"orb_actual={orb}, exp={case['exp_orb']}"
    elif check == 'asp_diff':
        p = _p(); diff = p.get('diff') if p else None; ok = diff is not None and abs(diff - case['exp_diff']) < 0.01; detail = f"diff={diff}, exp={case['exp_diff']}"
    elif check == 'bc_tu':
        p = _p(); tu = p.get('timeUnknown') if p else None; ok = tu == case['exp_tu']; detail = f"timeUnknown={tu!r}"
    elif check == 'bc_lat':
        p = _p(); lat = p.get('lat') if p else None; ok = lat is not None and abs(lat - case['exp_lat']) < 0.001; detail = f"lat={lat}"
    elif check == 'bc_n11':
        p = _p(); n = p.get('nPositions', 0) if p else 0; ok = n == 11; detail = f"nPositions={n}"
    elif check == 'bc_has_asc':
        p = _p(); pl = p.get('planets', []) if p else []; ok = 'Ascendant' in pl; detail = f"planets={pl}"
    elif check == 'bc_sun_sign':
        p = _p(); sign = p.get('pos', {}).get('Sun', {}).get('sign') if p else None; ok = sign == case['exp_sign']; detail = f"Sun sign={sign!r}"
    elif check == 'bc_lons_valid':
        p = _p(); lons = [v['lon'] for v in (p.get('pos', {}) or {}).values()] if p else []; bad = [l for l in lons if not (0 <= l < 360)]; ok = len(bad) == 0; detail = f"bad lons={bad}"
    elif check == 'bc_pos_fields':
        p = _p(); pos = p.get('pos', {}) if p else {}; bad = [k for k, v in pos.items() if not all(f in v for f in ('lon','sign','deg','sym'))]; ok = len(bad) == 0; detail = f"missing fields in: {bad}"
    elif check == 'bc_trace':
        p = _p(); n = p.get('nTrace', 0) if p else 0; ok = n >= 10; detail = f"nTrace={n}"
    elif check == 'bc_jd':
        p = _p(); jd = p.get('JD') if p else None; ok = jd is not None and abs(jd - 2451545.0) < 0.01; detail = f"JD={jd}"
    elif check == 'bc_T':
        p = _p(); Tv = p.get('T') if p else None; ok = Tv is not None and abs(Tv) < 0.01; detail = f"T={Tv}"
    elif check == 'syn_pairs':
        p = _p(); ok = p is not None and p.get('nPairs') == 121; detail = f"nPairs={p.get('nPairs') if p else None}"
    elif check == 'syn_fields':
        p = _p(); ok = p is not None and p.get('allHavePairKeys', False); detail = f"allHavePairKeys={p.get('allHavePairKeys') if p else None}"
    elif check == 'syn_asp_range':
        p = _p(); n = p.get('nAspects') if p else None; ok = n is not None and 0 <= n <= 121; detail = f"nAspects={n}"
    elif check == 'syn_h_range':
        p = _p(); hs = [a['h'] for a in (p.get('aspects', []) if p else [])]; bad = [h for h in hs if not (-1 <= h <= 1)]; ok = len(bad) == 0; detail = f"bad h vals={bad}"
    elif check == 'syn_orb_pos':
        p = _p(); orbs = [a['orb'] for a in (p.get('aspects', []) if p else [])]; bad = [o for o in orbs if o < 0]; ok = len(bad) == 0; detail = f"negative orbs={bad}"
    elif check == 'syn_self':
        p = _p(); conjs = [a for a in (p.get('aspects', []) if p else []) if a['pair'].split('-')[0] == a['pair'].split('-')[1] and a['asp'] == 'Conjunction']; ok = len(conjs) == 11; detail = f"same-planet Conjunctions={len(conjs)}"
    elif check == 'syn_self_orb':
        p = _p(); sc = [a for a in (p.get('aspects', []) if p else []) if a['pair'].split('-')[0] == a['pair'].split('-')[1] and a['asp'] == 'Conjunction']; bad = [a['orb'] for a in sc if abs(a['orb']) > 0.01]; ok = len(bad) == 0; detail = f"non-zero self orbs={bad}"
    elif check == 'syn_slow_flag':
        p = _p(); sf = p.get('slowFlags', []) if p else []
        slow_pairs = [f for f in sf if f.get('slowA') or f.get('slowB')]
        su = [f for f in sf if f['pair'] == 'Sun-Uranus' and f.get('slowB')]
        us = [f for f in sf if f['pair'] == 'Uranus-Sun' and f.get('slowA')]
        ok = len(slow_pairs) > 0 and len(su) >= 1 and len(us) >= 1
        detail = f"slow-flagged pairs={len(slow_pairs)}, Sun-Uranus(slowB)={len(su)}, Uranus-Sun(slowA)={len(us)}"
    elif check == 'score_val':
        p = _p(); score = p.get('scores', {}).get(case['domain']) if p else None; ok = score == case['exp_score']; detail = f"{case['domain']}={score}, exp={case['exp_score']}"
    elif check == 'scores_range':
        p = _p(); sc = p.get('scores', {}) if p else {}; bad = [f"{k}={v}" for k, v in sc.items() if not (0 <= v <= 100)]; ok = len(bad) == 0; detail = "all in [0,100]" if ok else f"bad: {bad}"
    elif check == 'score_keys':
        p = _p(); sc = p.get('scores', {}) if p else {}; ok = set(sc.keys()) == {'overall','love','harmony','passion','mental','karmic'}; detail = f"keys={set(sc.keys())}"
    elif check == 'formula_harm':
        p = _p(); h = p.get('harmony') if p else None; ok = h == 100; detail = f"harmony={h}"
    elif check == 'formula_ov':
        p = _p(); ov = p.get('overall') if p else None; ok = ov is not None and ov > 50; detail = f"overall={ov} (expected >50)"
    elif check == 'score_details':
        p = _p(); n = p.get('nDetails', 0) if p else 0; ok = n > 0; detail = f"nDetails={n}"
    elif check == 'score_detail_fields':
        p = _p(); dk = p.get('detailKeys', []) if p else []; ok = all(f in dk for f in ('key','asp','h','w','c')); detail = f"detailKeys={dk}"
    elif check == 'conf_range':
        p = _p(); val = p.get(case['key']) if p else None; ok = val is not None and 0 <= val <= 100; detail = f"{case['key']}={val}"
    elif check == 'conf_one_tu':
        p = _p(); astro = p.get('astro') if p else None; ok = astro is not None and astro <= 85; detail = f"astro={astro}"
    elif check == 'conf_two_tu':
        p = _p(); astro = p.get('astro') if p else None; ok = astro is not None and astro <= 70; detail = f"astro={astro}"
    elif check == 'conf_found':
        p = _p(); found = p.get('found') if p else None; ok = found is not None and found >= 0; detail = f"found={found}"
    elif check == 'conf_formula':
        p = _p()
        if p:
            import math
            astro = p.get('astro', 0); coher = p.get('coher', 0)
            exp_g = math.floor(astro * 0.50 + coher * 0.50 + 0.5); act_g = p.get('global', -1)
            ok = act_g == exp_g; detail = f"global={act_g}, expected round({astro}*0.50+{coher}*0.50)={exp_g}"
        else:
            ok = False; detail = "null result"
    # ── natal aspects ─────────────────────────────────────────────────────
    elif check == 'nat_asp_range':
        p = _p(); n = p.get('nAspects') if p else None; ok = n is not None and n >= 0; detail = f"nAspects={n}"
    elif check == 'nat_asp_fields':
        p = _p(); ok = p is not None and p.get('allHaveFields', False); detail = f"allHaveFields={p.get('allHaveFields') if p else None}"
    elif check == 'nat_asp_h':
        p = _p(); hs = [a['h'] for a in (p.get('aspects', []) if p else [])]; bad = [h for h in hs if not (-1 <= h <= 1)]; ok = len(bad) == 0; detail = f"bad h vals={bad}"
    elif check == 'nat_asp_orb':
        p = _p(); orbs = [a['orb'] for a in (p.get('aspects', []) if p else [])]; bad = [o for o in orbs if o < 0]; ok = len(bad) == 0; detail = f"negative orbs={bad}"
    elif check == 'nat_asp_nodup':
        p = _p(); asps = p.get('aspects', []) if p else []
        pairs_seen = set()
        dups = []
        for a in asps:
            key = (a['pA'], a['pB']); rev = (a['pB'], a['pA'])
            if rev in pairs_seen: dups.append(f"{a['pA']}-{a['pB']}")
            pairs_seen.add(key)
        ok = len(dups) == 0; detail = f"duplicate pairs={dups}"
    elif check == 'nat_asp_max':
        p = _p(); n = p.get('nAspects') if p else None; ok = n is not None and n <= 55; detail = f"nAspects={n} (max 55)"
    elif check == 'nat_asp_slow':
        p = _p(); asps = p.get('aspects', []) if p else []
        uranus_asps = [a for a in asps if a['pA'] == 'Uranus' or a['pB'] == 'Uranus']
        slow_ok = all(a.get('slowA') or a.get('slowB') for a in uranus_asps) if uranus_asps else True
        ok = slow_ok; detail = f"Uranus aspects={len(uranus_asps)}, all slow-flagged={slow_ok}"
    # ── lunarPhase ────────────────────────────────────────────────────────
    elif check == 'lunar_idx':
        p = _p(); idx = p.get('idx') if p else None; ok = idx == case['exp_idx']; detail = f"idx={idx}, exp={case['exp_idx']}"
    elif check == 'lunar_angle_range':
        p = _p(); a = p.get('angle') if p else None; ok = a is not None and 0 <= a < 360; detail = f"angle={a}"
    elif check == 'lunar_langs':
        p = _p(); en = p.get('nameEn', '') if p else ''; fr = p.get('nameFr', '') if p else ''; it = p.get('nameIt', '') if p else ''
        ok = len(en) > 0 and len(fr) > 0 and len(it) > 0; detail = f"EN={en!r} FR={fr!r} IT={it!r}"
    elif check == 'lunar_idx_range':
        p = _p(); idx = p.get('idx') if p else None; ok = idx is not None and 0 <= idx <= 7; detail = f"idx={idx}"
    # ── elementTally ──────────────────────────────────────────────────────
    elif check == 'elem_total':
        p = _p(); total = sum(p.values()) if p else 0; ok = total == 11; detail = f"total={total}"
    elif check == 'elem_keys':
        p = _p(); ok = p is not None and set(p.keys()) == {'Fire','Earth','Air','Water'}; detail = f"keys={set(p.keys()) if p else None}"
    elif check == 'elem_nonneg':
        p = _p(); bad = [f"{k}={v}" for k, v in (p or {}).items() if v < 0]; ok = len(bad) == 0; detail = f"bad={bad}"
    # ── modalityTally ─────────────────────────────────────────────────────
    elif check == 'mod_total':
        p = _p(); total = sum(p.values()) if p else 0; ok = total == 11; detail = f"total={total}"
    elif check == 'mod_keys':
        p = _p(); ok = p is not None and set(p.keys()) == {'Cardinal','Fixed','Mutable'}; detail = f"keys={set(p.keys()) if p else None}"
    # ── dignityScores ─────────────────────────────────────────────────────
    elif check == 'dig_count':
        p = _p(); ok = p is not None and len(p) == 10; detail = f"count={len(p) if p else None}"
    elif check == 'dig_scores':
        p = _p(); bad = [f"{k}={v['score']}" for k, v in (p or {}).items() if v['score'] not in (-2,-1,0,1,2)]; ok = len(bad) == 0; detail = f"bad scores={bad}"
    elif check == 'dig_sun_aries':
        p = _p(); sun = p.get('Sun') if p else None; ok = sun is not None and sun.get('score') == 1 and sun.get('label') == 'exaltation'; detail = f"Sun={sun}"
    elif check == 'dig_sun_leo':
        p = _p(); sun = p.get('Sun') if p else None; ok = sun is not None and sun.get('score') == 2 and sun.get('label') == 'domicile'; detail = f"Sun={sun}"
    elif check == 'dig_sun_cap':
        p = _p(); sun = p.get('Sun') if p else None; ok = sun is not None and sun.get('score') in (0, -2); detail = f"Sun={sun}"
    elif check == 'dig_labels':
        p = _p(); bad = [k for k, v in (p or {}).items() if v['score'] != 0 and not v.get('label')]; ok = len(bad) == 0; detail = f"missing labels for={bad}"
    # ── retrogradeFlags ───────────────────────────────────────────────────
    elif check == 'retro_count':
        p = _p(); ok = p is not None and len(p) == 8; detail = f"count={len(p) if p else None}"
    elif check == 'retro_bool':
        p = _p(); bad = [k for k, v in (p or {}).items() if not isinstance(v, bool)]; ok = len(bad) == 0; detail = f"non-bool={bad}"
    elif check == 'retro_no_sun_moon':
        p = _p(); ok = p is not None and 'Sun' not in p and 'Moon' not in p; detail = f"keys={list(p.keys()) if p else None}"
    elif check == 'retro_pluto_1990':
        p = _p(); ok = p is not None and p.get('Pluto') == True; detail = f"Pluto={p.get('Pluto') if p else None}"
    elif check == 'retro_mercury_2000':
        p = _p(); ok = p is not None and p.get('Mercury') == True; detail = f"Mercury={p.get('Mercury') if p else None}"
    # ── buildNatalProfile ─────────────────────────────────────────────────
    elif check == 'profile_fields':
        p = _p(); required = {'nAspects','lunarIdx','lunarAngle','lunarEn','lunarFr','lunarIt','elements','modalities','elemTotal','modTotal','sunDignity','moonDignity','retrogrades','timeUnknown','JD','lat'}
        missing = required - set(p.keys() if p else []); ok = len(missing) == 0; detail = f"missing={missing}"
    elif check == 'profile_elem_total':
        p = _p(); total = p.get('elemTotal') if p else None; ok = total == 11; detail = f"elemTotal={total}"
    elif check == 'profile_mod_total':
        p = _p(); total = p.get('modTotal') if p else None; ok = total == 11; detail = f"modTotal={total}"
    elif check == 'profile_lunar_langs':
        p = _p(); ok = p is not None and all(len(p.get(k, '')) > 0 for k in ('lunarEn','lunarFr','lunarIt')); detail = f"EN={p.get('lunarEn') if p else None!r}"
    elif check == 'profile_asp_max':
        p = _p(); n = p.get('nAspects') if p else None; ok = n is not None and n <= 55; detail = f"nAspects={n}"
    elif check == 'profile_sun_dignity':
        p = _p(); d = p.get('sunDignity') if p else None; ok = d is not None and d.get('score') == 1 and d.get('label') == 'exaltation'; detail = f"sunDignity={d}"
    elif check == 'profile_jd':
        p = _p(); jd = p.get('JD') if p else None; ok = jd is not None and jd > 2400000; detail = f"JD={jd}"
    elif check == 'profile_lat':
        p = _p(); lat = p.get('lat') if p else None; ok = lat is not None and abs(lat - 48.9) < 0.01; detail = f"lat={lat}"
    elif check == 'profile_tu':
        p = _p(); tu = p.get('timeUnknown') if p else None; ok = tu == True; detail = f"timeUnknown={tu}"
    # ── builtinNatalReport ────────────────────────────────────────────────
    elif check == 'natal_report_basic':
        p = _p(); ok = p is not None and p.get('hasText') and p.get('hasH3'); detail = f"hasText={p.get('hasText') if p else None}, hasH3={p.get('hasH3') if p else None}"
    elif check == 'natal_report_lang':
        p = _p(); ok = p is not None and p.get('langTest', False); detail = f"langTest={p.get('langTest') if p else None}, length={p.get('length') if p else None}"
    elif check == 'natal_report_tu_warn':
        p = _p(); ok = p is not None and p.get('hasText'); detail = f"hasText={p.get('hasText') if p else None}"
    elif check == 'score_val_range':
        p = _p()
        sc = p.get('scores', {}) if p else {}
        domain = case['domain']
        val = sc.get(domain)
        ok = val is not None and 0 <= val <= 100
        detail = f"{domain}={val}"
    else:
        ok = True; detail = str(_p())

    return (ok, detail)


@pytest.mark.parametrize("idx", range(len(_CASES)), ids=[c['name'] for c in _CASES])
def test_unit_case(idx, unit_results, asc_store):
    case, nr = unit_results[idx]
    err = nr.get('error')
    assert not err, f"JS error: {err}"
    ok, detail = evaluate_unit_case(case, nr, asc_store)
    assert ok, detail
