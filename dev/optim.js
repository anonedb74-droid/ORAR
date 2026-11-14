/* ===== Reorganizarea orarului (R2 + ferestre) =====
   Scop: cât mai puține zile în care un profesor are ore în două locații (R2) și cât mai puține ferestre la profesori.
   Rămân neschimbate: blocurile de practică / zilele de specialitate (≥3 ore la rând cu aceiași profesori), orele
   fiecărui profesor la fiecare clasă, ora 1 și ziua fără goluri la fiecare clasă (R7), maximul de ore pe zi în locație,
   fără suprapuneri noi. Implicit, fiecare profesor vine doar în zilele în care vine acum (poate are ore la Ghilea sau în altă școală). */
function optimizeazaOrar(orar, clase, ZILE, maxOre, opt = {}){
  const W_R2 = opt.wR2 ?? 12, W_F = opt.wF ?? 1, W_SCH = opt.wSch ?? 0.03, W_ZI = opt.wZiNoua ?? 8;
  const ziNoua = !!opt.permiteZileNoi, fixeProf = new Set(opt.profFixati || []);
  const ITER = opt.iter ?? 200000, REST = opt.restarturi ?? 3;
  let seed = opt.seed ?? 12345;
  const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  const loc = {}; clase.forEach(c => loc[c.id] = c.locatie);
  const cheie = x => (x.prof || []).map(p => p.p + ":" + p.per).sort().join("|");
  const are = x => x && (x.disc || (x.prof || []).length);
  const G0 = {}, F = {}, sare = new Set(), lmin = {};
  for(const cl of clase){
    const c = cl.id; G0[c] = {}; F[c] = {};
    let mn = 99;
    for(const z of ZILE){
      const zi = (orar[c] || {})[z] || {};
      const ore = Object.keys(zi).filter(h => are(zi[h])).map(Number).sort((a, b) => a - b);
      if(ore.length && (ore[0] !== 1 || ore[ore.length - 1] !== ore.length)) sare.add(c); // clasă cu goluri: nu o ating
      const L = ore.map(h => zi[h]); G0[c][z] = L;
      const f = L.map(() => false);
      for(let i = 0; i < L.length;){
        let j = i; while(j + 1 < L.length && cheie(L[i]) && cheie(L[j + 1]) === cheie(L[i])) j++;
        if(j - i + 1 >= 3) for(let k = i; k <= j; k++) f[k] = true;
        i = j + 1;
      }
      F[c][z] = f; if(L.length) mn = Math.min(mn, L.length);
    }
    lmin[c] = mn === 99 ? 0 : mn;
  }
  const zileProf = {};
  for(const c in G0) for(const z of ZILE) G0[c][z].forEach(x => (x.prof || []).forEach(p => (zileProf[p.p] ??= new Set()).add(z)));
  const maxDisc = {};
  for(const c in G0){ maxDisc[c] = {}; for(const z of ZILE){ const n = {}; G0[c][z].forEach(x => { if(x.disc){ n[x.disc] = (n[x.disc] || 0) + 1; maxDisc[c][x.disc] = Math.max(maxDisc[c][x.disc] || 2, n[x.disc]); } }); } }
  const compat = (a, b) => (a.per === "P1" && b.per === "P2") || (a.per === "P2" && b.per === "P1");
  const fixd = (c, z, i) => F[c][z][i] === true; // pozițiile fixe sunt indexate pe grila inițială și nu se mută

  function costPZ(occ, p, z){
    const zi = occ[p]?.[z]; if(!zi) return 0;
    let mn = 99, mx = 0, n = 0; const locuri = new Set();
    for(const h in zi){ const L = zi[h]; if(!L.length) continue; const k = +h; n++; if(k < mn) mn = k; if(k > mx) mx = k; L.forEach(o => locuri.add(loc[o.c])); }
    if(!n) return 0;
    return W_F * (mx - mn + 1 - n) + (locuri.size > 1 ? W_R2 : 0) + (zileProf[p]?.has(z) ? 0 : W_ZI);
  }
  const scoateZi = (occ, L, c, z) => L.forEach((x, i) => (x.prof || []).forEach(p => { const A = occ[p.p][z][i + 1]; A.splice(A.findIndex(o => o.c === c && o.per === p.per), 1); }));
  const puneZi = (occ, L, c, z) => L.forEach((x, i) => (x.prof || []).forEach(p => { ((occ[p.p] ??= {})[z] ??= {})[i + 1] ??= []; occ[p.p][z][i + 1].push({c, per: p.per}); }));
  const discOk = (L, c) => { const n = {}; for(const x of L) if(x.disc){ n[x.disc] = (n[x.disc] || 0) + 1; if(n[x.disc] > maxDisc[c][x.disc]) return false; } return true; };
  const ziPermisa = p => ziNoua && !fixeProf.has(p);
  function valid(occ, L, c, z){
    if(L.length > (maxOre[loc[c]]?.[z] ?? 7)) return false;
    if(L.length < lmin[c]) return false;
    if(!discOk(L, c)) return false;
    for(let i = 0; i < L.length; i++) for(const p of (L[i].prof || [])){
      if(!zileProf[p.p]?.has(z) && !ziPermisa(p.p)) return false;
      const A = occ[p.p]?.[z]?.[i + 1] || [];
      if(!A.every(o => o.c === c || compat(o, p))) return false;
    }
    return true;
  }
  const schimb = (L, c, z) => L.reduce((s, x, i) => s + (G0[c][z][i] !== x ? 1 : 0), 0) + Math.max(0, G0[c][z].length - L.length);
  const stare = G => { const occ = {}; for(const c in G) for(const z of ZILE) puneZi(occ, G[c][z], c, z); return occ; };
  const total = (G, occ) => { let s = 0; for(const p in occ) for(const z of ZILE) s += costPZ(occ, p, z); for(const c in G) for(const z of ZILE) s += W_SCH * schimb(G[c][z], c, z); return s; };
  const claseMut = Object.keys(G0).filter(c => !sare.has(c));
  const mobile = (L, c, z) => L.map((x, i) => i).filter(i => !fixd(c, z, i) || F[c][z][i] === undefined);

  const cost0 = total(G0, stare(G0));
  let best = G0, bestCost = cost0;
  for(let r = 0; r < REST; r++){
    const G = {}; for(const c in G0){ G[c] = {}; for(const z of ZILE) G[c][z] = G0[c][z].slice(); }
    const fixPos = {}; // fixPos[c][z] = set de poziții fixe (rămân pe loc)
    for(const c in G0){ fixPos[c] = {}; for(const z of ZILE) fixPos[c][z] = new Set(F[c][z].map((f, i) => f ? i : -1).filter(i => i >= 0)); }
    const occ = stare(G);
    let cost = total(G, occ), bC = cost, bG = null;
    let T = 1;
    const profi = Object.keys(zileProf);
    const salveaza = () => { bG = {}; for(const cc in G){ bG[cc] = {}; for(const z of ZILE) bG[cc][z] = G[cc][z].slice(); } };
    // încearcă o mutare: noile liste nA (ziua z1) și nB (ziua z2) pentru clasa c
    function incearca(c, z1, z2, nA, nB){
      const A = G[c][z1], B = G[c][z2];
      const afect = new Set();
      for(const [L, z] of [[A, z1], [B, z2], [nA, z1], [nB, z2]]) L.forEach(x => (x.prof || []).forEach(p => afect.add(p.p + "\u0001" + z)));
      let inainte = 0; for(const k of afect){ const [p, z] = k.split("\u0001"); inainte += costPZ(occ, p, z); }
      const s0 = W_SCH * (schimb(A, c, z1) + (z1 !== z2 ? schimb(B, c, z2) : 0));
      scoateZi(occ, A, c, z1); if(z1 !== z2) scoateZi(occ, B, c, z2);
      if(!(valid(occ, nA, c, z1) && (z1 === z2 || valid(occ, nB, c, z2)))){ puneZi(occ, A, c, z1); if(z1 !== z2) puneZi(occ, B, c, z2); return; }
      puneZi(occ, nA, c, z1); if(z1 !== z2) puneZi(occ, nB, c, z2);
      let dupa = 0; for(const k of afect){ const [p, z] = k.split("\u0001"); dupa += costPZ(occ, p, z); }
      const s1 = W_SCH * (schimb(nA, c, z1) + (z1 !== z2 ? schimb(nB, c, z2) : 0));
      const delta = dupa - inainte + s1 - s0;
      if(delta <= 0 || rnd() < Math.exp(-delta / T)){
        G[c][z1] = nA; if(z1 !== z2) G[c][z2] = nB;
        cost += delta;
        if(cost < bC - 1e-9){ bC = cost; salveaza(); }
      } else {
        scoateZi(occ, nA, c, z1); if(z1 !== z2) scoateZi(occ, nB, c, z2);
        puneZi(occ, A, c, z1); if(z1 !== z2) puneZi(occ, B, c, z2);
      }
    }
    function schimba(c, z1, i, z2, j){
      const A = G[c][z1], B = G[c][z2];
      if(i < 0 || j < 0 || i >= A.length || j >= B.length || fixPos[c][z1].has(i) || fixPos[c][z2].has(j)) return;
      if(z1 === z2 && i === j) return;
      const x = A[i], y = B[j];
      if(cheie(x) === cheie(y) && x.disc === y.disc) return;
      let nA, nB;
      if(z1 === z2){ nA = A.slice(); nA[i] = y; nA[j] = x; nB = nA; }
      else { nA = A.slice(); nB = B.slice(); nA[i] = y; nB[j] = x; }
      incearca(c, z1, z2, nA, nB);
    }
    const mobilePoz = (c, z) => G[c][z].map((x, i) => i).filter(i => !fixPos[c][z].has(i));
    const alege = L => L[Math.floor(rnd() * L.length)];
    for(let it = 0; it < ITER; it++){
      const T0 = opt.T0 ?? 2, T1 = opt.T1 ?? 0.005; T = T0 * Math.pow(T1 / T0, it / ITER);
      const tip = rnd();
      if(tip < 0.25){ // mutare țintită: R2 sau fereastră la un profesor
        const p = alege(profi), z = alege(ZILE), zi = occ[p]?.[z];
        if(!zi) continue;
        const ore = Object.keys(zi).filter(h => zi[h].length).map(Number).sort((a, b) => a - b);
        if(!ore.length) continue;
        const locuri = {}; ore.forEach(h => zi[h].forEach(o => (locuri[loc[o.c]] ??= []).push([h, o.c])));
        const L = Object.keys(locuri);
        if(L.length > 1){
          L.sort((a, b) => locuri[a].length - locuri[b].length);
          const l = L[0], [h, c] = alege(locuri[l]);
          const z2s = ZILE.filter(z2 => z2 !== z && Object.values(occ[p]?.[z2] || {}).every(A => A.every(o => loc[o.c] === l)));
          if(!z2s.length) continue;
          const z2 = alege(z2s), M = mobilePoz(c, z2);
          if(rnd() < 0.3 && G[c][z].length - 1 === h - 1) incearca(c, z, z2, G[c][z].slice(0, -1), G[c][z2].concat([G[c][z][h - 1]]));
          else if(M.length) schimba(c, z, h - 1, z2, alege(M));
        } else {
          const mn = ore[0], mx = ore[ore.length - 1];
          if(mx - mn + 1 === ore.length) continue;
          const goluri = []; for(let h = mn; h <= mx; h++) if(!zi[h] || !zi[h].length) goluri.push(h);
          const g = alege(goluri), h = rnd() < 0.5 ? mn : mx, c = alege(zi[h]).c;
          if(rnd() < 0.5) schimba(c, z, h - 1, z, g - 1);
          else { const z2 = alege(ZILE), M = mobilePoz(c, z2); if(M.length) schimba(c, z, h - 1, z2, alege(M)); }
        }
        continue;
      }
      const c = alege(claseMut), z1 = alege(ZILE), z2 = alege(ZILE);
      if(tip < 0.85){
        const ma = mobilePoz(c, z1), mb = mobilePoz(c, z2);
        if(ma.length && mb.length) schimba(c, z1, alege(ma), z2, alege(mb));
      } else if(tip < 0.96){
        const A = G[c][z1];
        if(z1 === z2 || !A.length || fixPos[c][z1].has(A.length - 1)) continue;
        incearca(c, z1, z2, A.slice(0, -1), G[c][z2].concat([A[A.length - 1]]));
      } else {
        if(z1 === z2 || fixPos[c][z1].size || fixPos[c][z2].size) continue;
        incearca(c, z1, z2, G[c][z2].slice(), G[c][z1].slice());
      }
    }
    if(bG && bC < bestCost){ bestCost = bC; best = bG; }
    seed = (seed * 7 + r * 1013 + 1) & 0x7fffffff;
  }
  const nou = {};
  for(const c in orar){
    nou[c] = {};
    for(const z of ZILE){
      if(!G0[c] || sare.has(c)){ nou[c][z] = JSON.parse(JSON.stringify(orar[c][z] || {})); continue; }
      const zi = {}; best[c][z].forEach((x, i) => zi[i + 1] = JSON.parse(JSON.stringify(x))); nou[c][z] = zi;
    }
  }
  return {orar: nou, cost0, cost: bestCost};
}
if(typeof module !== "undefined") module.exports = {optimizeazaOrar};
