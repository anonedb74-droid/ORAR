import json,collections,sys
d=json.load(open('/tmp/orar/app/data_initial.json'));loc={c['id']:c['locatie'] for c in d['clase']};B=d['clopot']
m=lambda t:int(t[:2])*60+int(t[3:5])
o=json.load(open(sys.argv[1]));P=collections.defaultdict(dict)
for c,zz in o.items():
  for z,hh in zz.items():
    for h,x in hh.items():
      for p in x['prof']: P[(p['p'],z)][int(h)]=loc[c]
for (p,z),mm in sorted(P.items()):
  hs=sorted(mm)
  for a,b in zip(hs,hs[1:]):
    if mm[a]!=mm[b]:
      g=m(B[mm[b]][z][str(b)][:5])-m(B[mm[a]][z][str(a)][6:]); print(p[:20],z,f"{mm[a][0]}{a}->{mm[b][0]}{b} {g}min",'' if g>=15 else 'NU!', 'D->Ș' if mm[a]=='Dorohoi' else '')
