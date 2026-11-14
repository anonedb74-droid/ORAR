import json,sys,collections,unicodedata,re
def normd(t):
    t=unicodedata.normalize('NFD',(t or '').upper()); t=''.join(ch for ch in t if unicodedata.category(ch)!='Mn'); return re.sub(r'[^A-Z0-9/]','',t)
d=json.load(open('/tmp/orar/app/data_initial.json'));loc={c['id']:c['locatie'][0] for c in d['clase']}
tips=collections.defaultdict(set)
for r in d['incadrare']:
  if r['inOrar']: tips[(r['p'],r['clasa'])].add(r['tip'])
o=json.load(open(sys.argv[1]))
for c,zz in o.items():
  for z,hh in zz.items():
    n=collections.Counter(normd(x['disc']) for x in hh.values() if x['prof'] and set().union(*[tips[(p['p'],c)] for p in x['prof']])<= {'CG','O-CO','O-DIRIG'} and set().union(*[tips[(p['p'],c)] for p in x['prof']]))
    for k,v in n.items():
      if v>2: print('R14',c,z,k,v)
P=collections.defaultdict(dict)
for c,zz in o.items():
  for z,hh in zz.items():
    for h,x in hh.items():
      for p in x['prof']: P[(p['p'],z)][int(h)]=loc[c]
for (p,z),m in P.items():
  seq=[m[h] for h in sorted(m)]
  if sum(1 for a,b in zip(seq,seq[1:]) if a!=b)>1: print('R15',p,z,''.join(seq))
  if len(set(seq))>1: print('  R2',p,z,''.join(str(h)+m[h] for h in sorted(m)))
