import json,collections,sys
d=json.load(open('/tmp/orar/app/data_initial.json'));loc={c['id']:c['locatie'][0] for c in d['clase']}
Z=d['zile']
def prof(o):
    P=collections.defaultdict(lambda: collections.defaultdict(dict))
    for c,zz in o.items():
        for z,hh in zz.items():
            for h,x in hh.items():
                for p in x['prof']: P[p['p']][z][int(h)]=loc[c]
    return P
def st(m):
    r2=[z for z in Z if len(set(m[z].values()))>1]
    f=sum(max(m[z])-min(m[z])+1-len(m[z]) for z in Z if m[z])
    return r2,f
A=prof(d['orar']);B=prof(json.load(open(sys.argv[1])))
tot=[0,0,0,0]
for p in sorted(A):
    a=st(A[p]);b=st(B[p]); tot[0]+=len(a[0]);tot[1]+=len(b[0]);tot[2]+=a[1];tot[3]+=b[1]
    if a!=b or a[0]: print(f"{p[:22]:22} R2 {','.join(x[:2] for x in a[0]) or '-':12} -> {','.join(x[:2] for x in b[0]) or '-':12} F {a[1]}->{b[1]}")
print(tot)
