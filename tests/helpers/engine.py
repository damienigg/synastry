"""Engine extraction from HTML and Node.js shim code."""

import math

# ── ENGINE EXTRACTION ─────────────────────────────────────────────────────────
START_MARKER = "// ASTRONOMY ENGINE"
END_MARKER   = "// BUILT-IN INTERPRETER"

COMPUTE_CONF_SHIM = """
// Minimal stubs so computeConf/builtinNatalReport run outside the browser app context
const STATE = { scoreData: { scores: null } };
function t(k){ return k; }  // i18n stub
// Minimal I18N stub — only the keys used by builtinNatalReport in tests
const I18N = {
  en:{ domicile:'domicile', exaltation:'exaltation', fall:'fall', detriment:'detriment',
       lunarPhaseTitle:'Lunar Phase', retrogradeTitle:'Retrograde Planets',
       natalSystemPrompt:'', compatTitles:['Stellar Union','Harmonious Bond','Complex Weave','Challenging Path','Deep Tension'],
       aspDescs:{Conjunction:'',Trine:'',Sextile:'',Square:'',Opposition:'',Quincunx:''}},
  fr:{ domicile:'Domicile', exaltation:'Exaltation', fall:'Chute', detriment:'Détriment',
       lunarPhaseTitle:'Phase Lunaire', retrogradeTitle:'Planètes Rétrogrades',
       natalSystemPrompt:'', compatTitles:['Union Stellaire','Lien Harmonieux','Tissu Complexe','Chemin Difficile','Tension Profonde'],
       aspDescs:{Conjunction:'',Trine:'',Sextile:'',Square:'',Opposition:'',Quincunx:''}},
  it:{ domicile:'Domicilio', exaltation:'Esaltazione', fall:'Caduta', detriment:'Detrimento',
       lunarPhaseTitle:'Fase Lunare', retrogradeTitle:'Pianeti Retrogradi',
       natalSystemPrompt:'', compatTitles:['Unione Stellare','Legame Armonioso','Intreccio Complesso','Percorso Difficile','Tensione Profonda'],
       aspDescs:{Conjunction:'',Trine:'',Sextile:'',Square:'',Opposition:'',Quincunx:''}},
};
let LANG = 'en';
"""


def extract_engine(html_path):
    text = html_path.read_text(encoding='utf-8')
    s = text.find(START_MARKER)
    e = text.find(END_MARKER)
    if s < 0: raise ValueError(f"'{START_MARKER}' not found in {html_path}")
    if e < 0: raise ValueError(f"'{END_MARKER}' not found in {html_path}")
    engine = text[s:e].strip()

    # Pull computeConf (synastry confidence, needed for compatibility tests)
    conf_start = text.find('\nfunction computeConf(')
    conf_end   = text.find('\nfunction confCard(', conf_start)
    if conf_start > 0 and conf_end > conf_start:
        engine += "\n" + COMPUTE_CONF_SHIM + text[conf_start:conf_end].strip()

    # Pull builtinNatalReport and buildNatalPrompt (natal profile tests)
    natal_start = text.find('\nfunction builtinNatalReport(')
    natal_end   = text.find('\nfunction renderNatalProfileBox(', natal_start)
    if natal_start > 0 and natal_end > natal_start:
        engine += "\n" + text[natal_start:natal_end].strip()

    return engine


# ── NODE SHIMS ────────────────────────────────────────────────────────────────
NODE_QUERY_SHIM = r"""
const [,,planet,dateStr] = process.argv;
const [y,m,d] = dateStr.split('-').map(Number);
const JD = toJD(y,m,d,12,0);
const T  = toT(JD);
let lon;
if      (planet === 'Sun')  lon = sunPos(T).lon;
else if (planet === 'Moon') lon = moonPos(T).lon;
else                        lon = planetPos(planet, T).lon;
process.stdout.write(JSON.stringify({planet,date:dateStr,JD,T,lon:parseFloat(lon.toFixed(6))})+'\n');
"""

NODE_UNIT_SHIM = r"""
const [,,casesJson] = process.argv;
const cases = JSON.parse(casesJson);
const out = cases.map(c => {
    try {
        let got;
        if      (c.fn==='toJD')   { const[y,m,d,h,tz]=c.args; got=toJD(y,m,d,h,tz||0); }
        else if (c.fn==='toT')    got = toT(c.args[0]);
        else if (c.fn==='m360')   got = m360(c.args[0]);
        else if (c.fn==='sunPos')    got = sunPos(c.args[0]).lon;
        else if (c.fn==='moonPos')   got = moonPos(c.args[0]).lon;
        else if (c.fn==='planetPos') got = planetPos(c.args[0],c.args[1]).lon;
        else if (c.fn==='degSign'){
            const r=degSign(c.args[0]);
            got=JSON.stringify({sign:r.sign,sym:r.sym,deg:r.deg,lon:r.lon});
        }
        else if (c.fn==='ascPos'){
            const[T,lat,lon]=c.args;
            const r=ascPos(T,lat,lon);
            got=JSON.stringify({lon:parseFloat(r.lon.toFixed(6)),gmst:parseFloat(r.tGMST),
                lst:parseFloat(r.tLST),eps:parseFloat(r.tEps),lat:parseFloat(r.tLat),lonGeo:parseFloat(r.tLon)});
        }
        else if (c.fn==='getAspectsConst'){
            got=JSON.stringify(ASPECTS.map(a=>({name:a.name,angle:a.angle,orb:a.orb,h:a.h,sym:a.sym})));
        }
        else if (c.fn==='getZSIGNS') got=JSON.stringify(ZSIGNS);
        else if (c.fn==='getZSYMS')  got=JSON.stringify(ZSYMS);
        else if (c.fn==='getSW')     got=JSON.stringify(Object.keys(SW));
        else if (c.fn==='getSWVal')  got=SW[c.args[0]]??null;
        else if (c.fn==='getSDDomains') got=JSON.stringify(Object.keys(SD));
        else if (c.fn==='getSDKeys')    got=JSON.stringify(SD[c.args[0]]||[]);
        else if (c.fn==='getAspect'){
            const r=getAspect(c.args[0],c.args[1]);
            got=r?JSON.stringify({name:r.name,h:r.h,sym:r.sym,
                orb_actual:parseFloat(r.orb_actual),diff:parseFloat(r.diff)}):'null';
        }
        else if (c.fn==='buildChart'){
            const[ds,ts,tz,tu,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,tu||false,lat,lon);
            const posOut={};
            for(const[k,v] of Object.entries(ch.pos))
                posOut[k]={lon:parseFloat(v.lon.toFixed(6)),sign:v.sign,deg:v.deg,sym:v.sym};
            got=JSON.stringify({JD:parseFloat(ch.JD.toFixed(6)),T:parseFloat(ch.T.toFixed(8)),
                timeUnknown:ch.timeUnknown,lat:ch.lat,nPositions:Object.keys(ch.pos).length,
                planets:Object.keys(ch.pos),pos:posOut,nTrace:ch.trace.length});
        }
        else if (c.fn==='buildSynastry'){
            const[dsA,tsA,tzA,latA,lonA,dsB,tsB,tzB,latB,lonB]=c.args;
            const cA=buildChart(dsA,tsA,tzA||0,false,latA||42,lonA||0);
            const cB=buildChart(dsB,tsB,tzB||0,false,latB||42,lonB||0);
            const pairs=buildSynastry(cA,cB);
            const aspPairs=pairs.filter(p=>p.asp);
            got=JSON.stringify({nPairs:pairs.length,nAspects:aspPairs.length,
                allHavePairKeys:pairs.every(p=>'pA' in p&&'pB' in p&&'lA' in p&&'lB' in p&&'sA' in p&&'sB' in p&&'slowA' in p&&'slowB' in p),
                slowFlags:pairs.map(p=>({pair:`${p.pA}-${p.pB}`,slowA:p.slowA,slowB:p.slowB,hasAsp:!!p.asp})),
                aspects:aspPairs.map(p=>({pair:`${p.pA}-${p.pB}`,asp:p.asp.name,orb:parseFloat(p.asp.orb_actual),h:p.asp.h}))});
        }
        else if (c.fn==='scoreSyn'){
            const[dsA,tsA,tzA,latA,lonA,dsB,tsB,tzB,latB,lonB]=c.args;
            const cA=buildChart(dsA,tsA,tzA||0,false,latA||42,lonA||0);
            const cB=buildChart(dsB,tsB,tzB||0,false,latB||42,lonB||0);
            const pairs=buildSynastry(cA,cB);
            const sd=scoreSyn(pairs);
            got=JSON.stringify({scores:sd.scores,nDetails:sd.details.length,
                detailKeys:sd.details.length?Object.keys(sd.details[0]):[]});
        }
        else if (c.fn==='scoreSynFormula'){
            const cA=buildChart('2000-01-01','12:00',0,false,42,0);
            const cB=buildChart('2000-01-01','12:00',0,false,42,0);
            const pairs=buildSynastry(cA,cB);
            const sd=scoreSyn(pairs);
            got=JSON.stringify({harmony:sd.scores.harmony,overall:sd.scores.overall});
        }
        // ── Natal profile ─────────────────────────────────────────────────────
        else if (c.fn==='buildNatalAspects'){
            const[ds,ts,tz,tu,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,tu||false,lat||42,lon||0);
            const asps=buildNatalAspects(ch);
            got=JSON.stringify({
                nAspects:asps.length,
                allHaveFields:asps.every(a=>'pA' in a&&'pB' in a&&'asp' in a&&'lA' in a&&'lB' in a),
                aspects:asps.map(a=>({pA:a.pA,pB:a.pB,name:a.asp.name,h:a.asp.h,orb:parseFloat(a.asp.orb_actual),slowA:a.slowA,slowB:a.slowB})),
            });
        }
        else if (c.fn==='lunarPhase'){
            const[ds,ts,tz,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,false,lat||42,lon||0);
            const lp=lunarPhase(ch);
            got=JSON.stringify({angle:lp.angle,idx:lp.idx,nameEn:lp.names.en,nameFr:lp.names.fr,nameIt:lp.names.it});
        }
        else if (c.fn==='elementTally'){
            const[ds,ts,tz,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,false,lat||42,lon||0);
            got=JSON.stringify(elementTally(ch));
        }
        else if (c.fn==='modalityTally'){
            const[ds,ts,tz,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,false,lat||42,lon||0);
            got=JSON.stringify(modalityTally(ch));
        }
        else if (c.fn==='dignityScores'){
            const[ds,ts,tz,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,false,lat||42,lon||0);
            got=JSON.stringify(dignityScores(ch));
        }
        else if (c.fn==='retrogradeFlags'){
            const[ds,ts,tz,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,false,lat||42,lon||0);
            got=JSON.stringify(retrogradeFlags(ch));
        }
        else if (c.fn==='buildNatalProfile'){
            const[ds,ts,tz,tu,lat,lon]=c.args;
            const ch=buildChart(ds,ts,tz||0,tu||false,lat||42,lon||0);
            const p=buildNatalProfile(ch);
            got=JSON.stringify({
                nAspects:    p.aspects.length,
                lunarIdx:    p.lunarPhase.idx,
                lunarAngle:  p.lunarPhase.angle,
                lunarEn:     p.lunarPhase.names.en,
                lunarFr:     p.lunarPhase.names.fr,
                lunarIt:     p.lunarPhase.names.it,
                elements:    p.elements,
                modalities:  p.modalities,
                elemTotal:   Object.values(p.elements).reduce((a,b)=>a+b,0),
                modTotal:    Object.values(p.modalities).reduce((a,b)=>a+b,0),
                sunDignity:  p.dignities.Sun,
                moonDignity: p.dignities.Moon,
                retrogrades: p.retrogrades,
                timeUnknown: p.timeUnknown,
                JD:          parseFloat(p.JD.toFixed(4)),
                lat:         p.lat,
            });
        }
        else if (c.fn==='builtinNatalReport'){
            const[ds,ts,tz,tu,lat,lon,lang]=c.args;
            const ch=buildChart(ds,ts,tz||0,tu||false,lat||42,lon||0);
            const p=buildNatalProfile(ch);
            const name=c.name_arg||'TestPerson';
            const text=builtinNatalReport(p,name,lang||'en');
            got=JSON.stringify({
                hasText:     text.length>100,
                hasH3:       text.includes('###'),
                langTest:    lang==='fr'?text.includes('Feu')||text.includes('Lune'):
                             lang==='it'?text.includes('Luna')||text.includes('Fuoco'):
                             text.includes('Moon')||text.includes('Fire')||text.includes('Earth'),
                length:      text.length,
            });
        }
        else if (c.fn==='computeConf'){
            const[dsA,tsA,tzA,tuA,latA,lonA,dsB,tsB,tzB,tuB,latB,lonB]=c.args;
            const cA=buildChart(dsA,tsA,tzA||0,tuA||false,latA||42,lonA||0);
            const cB=buildChart(dsB,tsB,tzB||0,tuB||false,latB||42,lonB||0);
            const pairs=buildSynastry(cA,cB);
            const sd=scoreSyn(pairs);
            STATE.scoreData={scores:sd.scores};
            const conf=computeConf(cA,cB,pairs,null);
            got=JSON.stringify({global:conf.global,astro:conf.astro,cov:conf.cov,
                coher:conf.coher,found:conf.found,nFlags:conf.flags.length,llmScore:conf.llmScore});
        }
        else got=null;
        return {name:c.name,got};
    } catch(e){ return {name:c.name,got:null,error:e.message}; }
});
process.stdout.write(JSON.stringify(out)+'\n');
"""

NODE_ASC_SHIM = r"""
const [,,dateStr,hour,lat,lon] = process.argv;
const [y,m,d] = dateStr.split('-').map(Number);
const JD = toJD(y,m,d,parseFloat(hour),0);
const T  = toT(JD);
const r  = ascPos(T, parseFloat(lat), parseFloat(lon));
process.stdout.write(JSON.stringify({asc:parseFloat(r.lon.toFixed(6)),gmst:parseFloat(r.tGMST),lst:parseFloat(r.tLST)})+'\n');
"""


# ── PYTHON JD HELPER ──────────────────────────────────────────────────────────
def jd_py(y, m, d, h=12, tz=0):
    ut = h - tz
    yr = y - 1 if m <= 2 else y
    mo = m + 12 if m <= 2 else m
    A  = math.floor(yr / 100)
    Bc = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (yr + 4716)) + math.floor(30.6001 * (mo + 1)) + d + Bc - 1524.5 + ut / 24


def T_from(date_str, h=12):
    y, m, d = map(int, date_str.split('-'))
    return (jd_py(y, m, d, h) - 2451545) / 36525
