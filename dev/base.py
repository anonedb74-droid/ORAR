import json,collections
d=json.load(open('/tmp/orar/app/data_initial.json'))
Z=d['zile'];loc={c['id']:c['locatie'] for c in d['clase']}
def stats(orar):
    occ=collections.defaultdict(lambda: collections.defaultdict(set)); locs=collections.defaultdict(lambda: collections.defaultdict(set))
    for c,zz in orar.items():
        for z,hh in zz.items():
            for h,x in hh.items():
                for p in x.get('prof',[]):
                    occ[p['p']][z].add(int(h)); locs[p['p']][z].add(loc[c])
    gaps=0;r2=0;det=[]
    for p in occ:
        for z,s in occ[p].items():
            g=max(s)-min(s)+1-len(s); gaps+=g
            if g: det.append((p,z,sorted(s),g))
            if len(locs[p][z])>1: r2+=1
    return gaps,r2,det
g,r,det=stats(d['orar']); print(g,r)
for x in sorted(det,key=lambda x:-x[3]): print(x)
