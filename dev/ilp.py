"""Reorganizarea orarului cu programare liniară în numere întregi (HiGHS din scipy).
Minimizează: W_R2 * zile cu două locații + W_F * ferestre + W_SCH * ore mutate (+ W_ZI * zile noi, dacă se permit).
Fix: blocurile de >=3 ore la rând cu aceiași profesori; ora 1 și ziua fără goluri; maximul pe zi; orele pe tip de celulă;
fără suprapuneri (P1 cu P2 sunt compatibile); zilele profesorilor (implicit doar cele de acum)."""
import json, sys, collections, time
import numpy as np, unicodedata, re
def normd(t):
    t = unicodedata.normalize('NFD', (t or '').upper()); t = ''.join(ch for ch in t if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^A-Z0-9/]', '', t)
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix

def ruleaza(d, W_DS=3, W_R2=12, W_F=1, W_SCH=0.05, zile_noi=False, W_ZI=8, prof_fixati=(), timp=600, lungimi_fixe=False, gap=0.0, zi_fixa=False, libere=()):
    libere = set(libere)
    ZF = lambda c: zi_fixa and c not in libere
    LF = lambda c: (lungimi_fixe or zi_fixa) and c not in libere
    Z = d['zile']; clase = d['clase']; loc = {c['id']: c['locatie'] for c in clase}
    maxo = d['locatiiMaxOre']; orar = d['orar']; clop = d['clopot']
    cheie = lambda x: "|".join(sorted(p['p'] + ":" + p['per'] for p in x.get('prof', [])))
    tipk = lambda x: json.dumps({'d': x.get('disc', ''), 'p': sorted([(p['p'], p['per']) for p in x.get('prof', [])])}, ensure_ascii=False)
    G0 = {}; FIX = {}; lmin = {}
    for cl in clase:
        c = cl['id']; G0[c] = {}; FIX[c] = {}
        mn = 99
        for z in Z:
            zi = orar[c].get(z, {})
            ore = sorted(int(h) for h, x in zi.items() if x.get('disc') or x.get('prof'))
            assert ore == list(range(1, len(ore) + 1)), (c, z, ore)
            L = [zi[str(h)] for h in ore]; G0[c][z] = L
            f = [False] * len(L); i = 0
            while i < len(L):
                j = i
                while j + 1 < len(L) and cheie(L[i]) and cheie(L[j + 1]) == cheie(L[i]): j += 1
                if j - i + 1 >= 3:
                    for k in range(i, j + 1): f[k] = True
                i = j + 1
            FIX[c][z] = f
            if L: mn = min(mn, len(L))
        lmin[c] = mn
    zileProf = collections.defaultdict(set)
    for c in G0:
        for z in Z:
            for x in G0[c][z]:
                for p in x['prof']: zileProf[p['p']].add(z)
    # tipuri de lecții mutabile pe clasă
    tipuri = {}; exemplu = {}; cnt = {}
    for c in G0:
        cnt[c] = collections.Counter()
        for z in Z:
            for i, x in enumerate(G0[c][z]):
                if not FIX[c][z][i]:
                    k = tipk(x); cnt[c][k] += 1; exemplu[k] = x
        tipuri[c] = list(cnt[c])
    cntz = collections.defaultdict(collections.Counter)
    for c in G0:
        for z in Z:
            for i, x in enumerate(G0[c][z]):
                if not FIX[c][z][i]: cntz[c, z][tipk(x)] += 1
    maxDisc = {}
    for c in G0:
        maxDisc[c] = collections.defaultdict(lambda: 2)
        for z in Z:
            n = collections.Counter(normd(x.get('disc')) for x in G0[c][z] if x.get('disc'))
            for k, v in n.items(): maxDisc[c][k] = max(maxDisc[c][k], v)
    # R14: disciplinele de cultură generală – cel mult 2 ore pe zi la o clasă
    tipuriPC = collections.defaultdict(set)
    for r in d['incadrare']:
        if r.get('inOrar'): tipuriPC[r['p'], r['clasa']].add(r['tip'])
    for c in G0:
        for z in Z:
            for x in G0[c][z]:
                t = set().union(*[tipuriPC[p['p'], c] for p in x['prof']]) if x['prof'] else set()
                if x.get('disc') and t and t <= {'CG', 'O-CO', 'O-DIRIG'}: maxDisc[c][normd(x['disc'])] = 2
    H = lambda c, z: maxo[loc[c]][z]
    # ---- variabile
    nv = 0; lb = []; ub = []; obj = []; integ = []
    def var(lo=0, hi=1, cost=0.0, intg=1):
        nonlocal nv
        lb.append(lo); ub.append(hi); obj.append(cost); integ.append(intg); nv += 1; return nv - 1
    X = {}  # (c,k,z,h) -> var
    W = {}  # (c,z,h) -> var sau 1/0
    fixP = collections.defaultdict(list)  # (p,z,h) -> [(c,per)] din celule fixe
    for c in G0:
        for z in Z:
            n0 = len(G0[c][z])
            for h in range(1, H(c, z) + 1):
                i = h - 1
                if i < n0 and FIX[c][z][i]:
                    W[c, z, h] = ('k', 1)
                    for p in G0[c][z][i]['prof']: fixP[p['p'], z, h].append((c, p['per']))
                    continue
                if LF(c):
                    W[c, z, h] = ('k', 1 if h <= n0 else 0)
                else:
                    W[c, z, h] = var()
                if W[c, z, h] == ('k', 0): continue
                for k in tipuri[c]:
                    x = exemplu[k]
                    if ZF(c) and not cntz[c, z][k]: continue
                    if not zile_noi and any(z not in zileProf[p['p']] for p in x['prof']): continue
                    if zile_noi and any(p['p'] in prof_fixati and z not in zileProf[p['p']] for p in x['prof']): continue
                    orig = (i < n0 and not FIX[c][z][i] and tipk(G0[c][z][i]) == k)
                    X[c, k, z, h] = var(cost=0.0 if orig else W_SCH)
    rows = []; cols = []; vals = []; rlo = []; rhi = []; nr = 0
    def con(terms, lo, hi):
        nonlocal nr
        const = 0
        for v, a in terms:
            if isinstance(v, int) and not isinstance(v, bool) and v >= 0 and False: pass
        for v, a in terms:
            rows.append(nr); cols.append(v); vals.append(a)
        rlo.append(lo); rhi.append(hi); nr += 1
    # W: contiguitate și limite
    for c in G0:
        for z in Z:
            for h in range(2, H(c, z) + 1):
                con_ineq(con, [(W[c, z, h], 1), (W[c, z, h - 1], -1)], None, 0)
            # sum x = w pe fiecare oră mutabilă
            for h in range(1, H(c, z) + 1):
                i = h - 1
                if i < len(G0[c][z]) and FIX[c][z][i]: continue
                xs = [(X[c, k, z, h], 1) for k in tipuri[c] if (c, k, z, h) in X]
                w = W[c, z, h]
                con_ineq(con, xs + [(w, -1)], 0, 0)
            # lungime minimă
            ws = [(W[c, z, h], 1) for h in range(1, H(c, z) + 1)]
            con_ineq(con, ws, lmin[c], None)
            # disciplină pe zi
            discuri = collections.defaultdict(list); fixd = collections.Counter()
            for i, x in enumerate(G0[c][z]):
                if FIX[c][z][i] and x.get('disc'): fixd[normd(x['disc'])] += 1
            for (cc, k, zz, h), v in X.items():
                if cc == c and zz == z:
                    dd = normd(exemplu[k].get('disc'))
                    if dd: discuri[dd].append((v, 1))
            for dd, L in discuri.items():
                con_ineq(con, L, None, maxDisc[c][dd] - fixd[dd])
        # numărul de lecții pe tip
        for k in tipuri[c]:
            if ZF(c):
                for z in Z:
                    xs = [(v, 1) for (cc, kk, zz, h), v in X.items() if cc == c and kk == k and zz == z]
                    if xs: con_ineq(con, xs, cntz[c, z][k], cntz[c, z][k])
            else:
                xs = [(v, 1) for (cc, kk, z, h), v in X.items() if cc == c and kk == k]
                con_ineq(con, xs, cnt[c][k], cnt[c][k])
    # profesori
    prez = collections.defaultdict(list)  # (p,z,h) -> [(var, per, c)]
    for (c, k, z, h), v in X.items():
        for p in exemplu[k]['prof']: prez[p['p'], z, h].append((v, p['per'], c))
    profi = set(p for (p, z, h) in prez) | set(p for (p, z, h) in fixP)
    nR2 = 0; nF = 0
    Y = {}; R = []; GAPV = []
    for p in profi:
        for z in Z:
            hs = range(1, 8)
            any_ = False
            for h in hs:
                L = prez.get((p, z, h), []); Fx = fixP.get((p, z, h), [])
                if not L and not Fx: Y[p, z, h] = None; continue
                any_ = True
                # conflict: T/A + P1 <= 1, T/A + P2 <= 1 (pe clase diferite)
                fT = sum(1 for c, per in Fx if per not in ('P1', 'P2'))
                f1 = sum(1 for c, per in Fx if per == 'P1'); f2 = sum(1 for c, per in Fx if per == 'P2')
                t = [(v, 1) for v, per, c in L if per not in ('P1', 'P2')]
                a1 = [(v, 1) for v, per, c in L if per == 'P1']; a2 = [(v, 1) for v, per, c in L if per == 'P2']
                if t or a1: con_ineq(con, t + a1, None, 1 - fT - f1)
                if t or a2: con_ineq(con, t + a2, None, 1 - fT - f2)
                if Fx: Y[p, z, h] = ('k', 1)
                else:
                    y = var(); Y[p, z, h] = y
                    for v, per, c in L: con_ineq(con, [(y, 1), (v, -1)], 0, None)
                    con_ineq(con, [(y, 1)] + [(v, -1) for v, per, c in L], None, 0)
            if not any_: continue
            # ferestre: a (început) crescător, b (nefinalizat) descrescător
            if W_F > 0:
                A = [var() for h in hs]; B = [var() for h in hs]
                for idx, h in enumerate(hs):
                    y = Y[p, z, h]
                    if y is None: continue
                    if isinstance(y, tuple):
                        con_ineq(con, [(A[idx], 1)], 1, None); con_ineq(con, [(B[idx], 1)], 1, None)
                    else:
                        con_ineq(con, [(A[idx], 1), (y, -1)], 0, None); con_ineq(con, [(B[idx], 1), (y, -1)], 0, None)
                for idx in range(1, len(A)):
                    con_ineq(con, [(A[idx], 1), (A[idx - 1], -1)], 0, None)
                    con_ineq(con, [(B[idx], 1), (B[idx - 1], -1)], None, 0)
                for idx, h in enumerate(hs):
                    g = var(cost=W_F, intg=0, hi=1); GAPV.append(g)
                    y = Y[p, z, h]
                    terms = [(g, 1), (A[idx], -1), (B[idx], -1)]
                    rhs = -1
                    if y is not None: terms.append((y, 1))
                    con_ineq(con, terms, -1, None)
            # R2
            locs = collections.defaultdict(list); fixloc = set()
            for h in hs:
                for v, per, c in prez.get((p, z, h), []): locs[loc[c]].append(v)
                for c, per in fixP.get((p, z, h), []): fixloc.add(loc[c])
            Ls = {}
            for l in ('Dorohoi', 'Șendriceni'):
                if l in fixloc: Ls[l] = ('k', 1)
                elif locs[l]:
                    u = var(); Ls[l] = u
                    for v in locs[l]: con_ineq(con, [(u, 1), (v, -1)], 0, None)
                else: Ls[l] = ('k', 0)
            # R15: cel mult o schimbare de locație pe zi (fără dus-întors)
            if all(u != ('k', 0) for u in Ls.values()):
                dr = var(); tt = [var() for h in hs]
                for idx in range(1, len(tt)): con_ineq(con, [(tt[idx], 1), (tt[idx - 1], -1)], 0, None)
                for idx, h in enumerate(hs):
                    for v, per, c in prez.get((p, z, h), []):
                        if loc[c] == 'Dorohoi':
                            con_ineq(con, [(tt[idx], 1), (v, 1), (dr, 1)], None, 2)
                            con_ineq(con, [(tt[idx], -1), (v, 1), (dr, -1)], None, 0)
                        else:
                            con_ineq(con, [(tt[idx], -1), (v, 1), (dr, 1)], None, 1)
                            con_ineq(con, [(tt[idx], 1), (v, 1), (dr, -1)], None, 1)
                    for c, per in fixP.get((p, z, h), []):
                        if loc[c] == 'Dorohoi':
                            con_ineq(con, [(tt[idx], 1), (dr, 1)], None, 1)
                            con_ineq(con, [(tt[idx], -1), (dr, -1)], None, -1)
                        else:
                            con_ineq(con, [(tt[idx], -1), (dr, 1)], None, 0)
                            con_ineq(con, [(tt[idx], 1), (dr, -1)], None, 0)
                # R17: întâi Șendriceni, apoi Dorohoi (dr = 1 înseamnă Dorohoi întâi)
                obj[dr] = W_DS
            # R16: cel puțin 15 minute între locații, după programul orelor
            mins = lambda t: int(t[:2]) * 60 + int(t[3:5])
            for h1 in hs:
                for h2 in hs:
                    if h2 <= h1: continue
                    for v1, l1, f1 in [(v, loc[c], 0) for v, per, c in prez.get((p, z, h1), [])] + [(None, loc[c], 1) for c, per in fixP.get((p, z, h1), [])]:
                        for v2, l2, f2 in [(v, loc[c], 0) for v, per, c in prez.get((p, z, h2), [])] + [(None, loc[c], 1) for c, per in fixP.get((p, z, h2), [])]:
                            if l1 == l2: continue
                            a_ = clop[l1][z].get(str(h1)); b_ = clop[l2][z].get(str(h2))
                            if not a_ or not b_: continue
                            if mins(b_[:5]) - mins(a_[6:]) >= 15: continue
                            terms = [(v, 1) for v in (v1, v2) if v is not None]
                            con_ineq(con, terms, None, 1 - f1 - f2)
            r = var(cost=W_R2); R.append((p, z, r))
            con_ineq(con, [(r, 1)] + [(u, -1) for u in Ls.values()], -1, None)
            # zi nouă
            if zile_noi and z not in zileProf[p]:
                zn = var(cost=W_ZI)
                for h in hs:
                    for v, per, c in prez.get((p, z, h), []): con_ineq(con, [(zn, 1), (v, -1)], 0, None)
    A_ = coo_matrix((vals, (rows, cols)), shape=(nr, nv)).tocsr()
    lo_ = np.array([-np.inf if v is None else v for v in rlo]); hi_ = np.array([np.inf if v is None else v for v in rhi])
    print('variabile', nv, 'restricții', nr, file=sys.stderr)
    t = time.time()
    res = milp(c=np.array(obj), constraints=LinearConstraint(A_, lo_, hi_), integrality=np.array(integ), bounds=Bounds(np.array(lb), np.array(ub)),
               options={'time_limit': timp, 'disp': False, 'mip_rel_gap': gap})
    print('stare', res.status, res.message, 'timp', round(time.time() - t), 'obiectiv', res.fun, file=sys.stderr)
    if res.x is None: return None
    xv = res.x
    nou = {}
    for c in G0:
        nou[c] = {}
        for z in Z:
            zi = {}
            for h in range(1, H(c, z) + 1):
                i = h - 1
                if i < len(G0[c][z]) and FIX[c][z][i]: zi[str(h)] = G0[c][z][i]; continue
                for k in tipuri[c]:
                    v = X.get((c, k, z, h))
                    if v is not None and xv[v] > 0.5: zi[str(h)] = exemplu[k]
            nou[c][z] = zi
    for c in orar:
        if c not in nou: nou[c] = orar[c]
    return nou

def _isv(w, c, z, h, W): return False
class _Const:
    pass
CONST = {}
def _t(w, c, z, h, W):
    # întoarce ('k', valoare) pentru constante, altfel indexul variabilei
    if (c, z, h) in _VARS: return w
    return ('k', w)
_VARS = set()
def con_ineq(con, terms, lo, hi):
    k = 0; T = []
    for v, a in terms:
        if isinstance(v, tuple): k += a * v[1]
        elif v is None: continue
        else: T.append((v, a))
    lo2 = None if lo is None else lo - k
    hi2 = None if hi is None else hi - k
    if not T:
        assert (lo2 is None or lo2 <= 1e-9) and (hi2 is None or hi2 >= -1e-9), ('restricție imposibilă', terms, lo, hi)
        return
    con(T, lo2, hi2)

if __name__ == '__main__':
    d = json.load(open('/tmp/orar/app/data_initial.json'))
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--zn', type=int, default=0); ap.add_argument('--fixe', type=int, default=0)
    ap.add_argument('--timp', type=int, default=300); ap.add_argument('--out', default='ilp.json'); ap.add_argument('--wr2', type=float, default=12); ap.add_argument('--wf', type=float, default=1); ap.add_argument('--inp', default=''); ap.add_argument('--zf', type=int, default=0); ap.add_argument('--libere', default='')
    a = ap.parse_args()
    if a.inp: d['orar'] = json.load(open(a.inp))
    n = ruleaza(d, zile_noi=bool(a.zn), lungimi_fixe=bool(a.fixe), timp=a.timp, W_R2=a.wr2, W_F=a.wf, zi_fixa=bool(a.zf), libere=[x for x in a.libere.split(',') if x])
    if n: json.dump(n, open(a.out, 'w'), ensure_ascii=False)
