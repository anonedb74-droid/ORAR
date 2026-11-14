import json,sys,collections
exec(open('base.py').read().split("g,r,det=stats")[0])
o=json.load(open(sys.argv[1]));g,r,det=stats(o)
# zile noi și verificări
def days(orar):
  D=collections.defaultdict(set)
  for c,zz in orar.items():
    for z,hh in zz.items():
      for h,x in hh.items():
        for p in x['prof']: D[p['p']].add(z)
  return D
D0=days(d['orar']);D1=days(o);noi=[(p,sorted(D1[p]-D0[p])) for p in D1 if D1[p]-D0[p]]
lib=[(p,sorted(D0[p]-D1[p])) for p in D0 if D0[p]-D1[p]]
ch=sum(1 for c in o for z in o[c] for h in set(o[c][z])|set(d['orar'][c][z]) if json.dumps(o[c][z].get(h),sort_keys=True)!=json.dumps(d['orar'][c][z].get(h),sort_keys=True))
print('ferestre',g,'R2',r,'zile noi',noi,'zile eliberate',lib,'celule schimbate',ch)
