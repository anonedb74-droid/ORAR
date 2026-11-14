import json,re,unicodedata,collections,openpyxl,glob
def N(t):
    t=unicodedata.normalize('NFD',(t or '').upper()); t=''.join(ch for ch in t if unicodedata.category(ch)!='Mn')
    return re.sub(r'[^A-Z0-9 ]',' ',t)
def tok(t): return {w for w in N(t).split() if len(w)>2 and w not in ('CDL','DIN','PENTRU','SPECIFICE','SPECIFIC','TEHNOLOGII','PRODUSELOR','INDUSTRIA','ALIMENTARA')}
src=open('/tmp/orar/build2.py').read()
ns={}; exec(src[:src.index("F=\"Calibri Light\"")].replace("from openpyxl","#"),ns)
T,C=ns['T'],ns['C']
C=[(cl,tp,dom,([("Fabricarea produselor de panificație",8,"LT 3 + IP 5"),("Fabricarea produselor de patiserie",9,"LT 4 + IP 5"),("Fabricarea produselor făinoase",4,"LT 2 + IP 2")] if cl=="XI K" else mods),cdl,("" if cl=="XI K" else obs)) for cl,tp,dom,mods,cdl,obs in C]
d=json.load(open('/tmp/orar/app/data_initial.json'))
W={c['id']:c['saptamani'] for c in d['clase']}
inc=[r for r in d['incadrare']]
# foaia comasată
f=glob.glob('/mnt/user-data/uploads/**/ORAR CLASE 2026-2027.xlsx',recursive=True)[0]
ws=[w for w in openpyxl.load_workbook(f,data_only=True).worksheets if 'COMAS' in w.title.upper()][0]
COM={r[0]:dict(sapt=r[1],osapt=r[2],tot=r[3],per=r[4],prof=r[5]) for r in ws.iter_rows(min_row=2,values_only=True) if r[0]}
# orar: ore/săpt pe (prof,clasa,per)
OR=collections.Counter()
for c,zz in d['orar'].items():
    for z,hh in zz.items():
        for h,x in hh.items():
            for p in x['prof']: OR[(p['p'],c,p['per'])]+=1
out={'clase':[],'module':[]}
for cl,tp,dom,mods,cdl,obs in C:
    t=T[tp]; w=W[cl]
    rows=[r for r in inc if r['clasa']==cl]
    spec=[r for r in rows if r['tip'] in ('DSP','PIP')]
    stag=[r for r in rows if not r['inOrar'] and 'stagiu' in (r['motiv'] or '')]
    used=set()
    if mods:
        asign=collections.defaultdict(list)
        for r in spec:
            if not r['inOrar']: continue
            sc=[(len(tok(nm.replace('CDL:',''))&tok(r['disciplina']))/max(1,len(tok(nm.replace('CDL:','')))),i) for i,(nm,o,ob) in enumerate(mods)]
            best=max(sc)
            if best[0]>=0.5: asign[best[1]].append(r); used.add(id(r))
        for i,(nm,o,ob) in enumerate(mods):
            m=asign[i]
            dsp=sum(r['oreAn'] for r in m if r['tip']=='DSP'); pip=sum(r['oreAn'] for r in m if r['tip']=='PIP')
            out['module'].append(dict(clasa=cl,modul=nm,osapt=o,sapt=w,plan=o*w,dsp=dsp,pip=pip,
                prof='; '.join(sorted({r['p'].split()[0]+(' (IP)' if r['tip']=='PIP' else '') for r in m})),obs=ob,
                indiv=sum(r['oreAn'] for r in spec if not r['inOrar'] and 'conducere' in (r['motiv'] or '') and len(tok(nm)&tok(r['disciplina']))>=1)))
    rest=[r for r in spec if r['inOrar'] and id(r) not in used]
    for r in rest:
        out['module'].append(dict(clasa=cl,modul='(în încadrare, nepotrivit cu planul) '+r['disciplina'],osapt=None,sapt=w,plan=None,
            dsp=r['oreAn'] if r['tip']=='DSP' else 0,pip=r['oreAn'] if r['tip']=='PIP' else 0,prof=r['p'].split()[0],obs=''))
    # practica săptămânală în orar: ore/săpt cu profesorii PIP
    pipprof={r['p'] for r in rows if r['tip']=='PIP' and r['inOrar']}
    orT=sum(v for (p,c,per),v in OR.items() if c==cl and p in pipprof and per in('T','A'))
    orP=sum(v for (p,c,per),v in OR.items() if c==cl and p in pipprof and per in('P1','P2'))
    pipAn=sum(r['oreAn'] for r in rows if r['tip']=='PIP' and r['inOrar'])
    com=COM.get(cl,{})
    # verificare profesor×clasă: orar vs încadrare (P1/P2 = interval)
    tp_ok=[]
    for p in sorted({r['p'] for r in rows if r['inOrar']}):
        incP=sum(r['oreAn'] for r in rows if r['p']==p and r['inOrar'])
        t_=sum(v for (pp,c,per),v in OR.items() if c==cl and pp==p and per=='T')*w
        pp_=sum(v for (pp,c,per),v in OR.items() if c==cl and pp==p and per in('P1','P2','A'))*w
        tp_ok.append((p, incP, t_, t_+pp_, t_-0.5*w<=incP<=t_+pp_+0.5*w))
    out.setdefault('tp',[]).extend([dict(clasa=cl,prof=p,inc=i,minim=a_,maxim=b_,ok=k) for p,i,a_,b_,k in tp_ok])
    out['clase'].append(dict(clasa=cl,niv=t['niv'],sapt=w,spec_plan=t['spec'],spec_plan_an=t['spec']*w,
        spec_inc=sum(r['oreAn'] for r in spec if r['inOrar']),pip_an=pipAn,pip_orar_T=orT,pip_orar_P=orP,
        com_plan_s=t['ps'],com_plan_o=t['po'],com_s=com.get('sapt'),com_os=com.get('osapt'),com_o=com.get('tot'),com_per=com.get('per'),com_prof=com.get('prof'),
        stag_inc=sum(r['oreAn'] for r in stag),stag_prof='; '.join(f"{r['p'].split()[0]} {r['oreAn']}" for r in stag),
        caip=sum(r['oreAn'] for r in rows if 'APROFUNDARE' in N(r['disciplina']))))
json.dump(out,open('rez.json','w'),ensure_ascii=False,indent=0)
for c in out['clase']: print(c['clasa'],c['sapt'],'spec',c['spec_plan_an'],c['spec_inc'],'pip',c['pip_an'],c['pip_orar_T'],c['pip_orar_P'],'com',c['com_plan_o'],c['com_o'],c['stag_inc'],c['caip'])
print()
for m in out['module']:
    tot=(m['dsp']+m['pip']); 
    if m['plan']!=tot: print(m['clasa'],m['modul'][:60],m['plan'],m['dsp'],m['pip'],m['prof'])
