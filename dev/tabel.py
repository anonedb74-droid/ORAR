import json,collections,sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L
d=json.load(open('/tmp/orar/app/data_initial.json'));loc={c['id']:c['locatie'] for c in d['clase']}
Z=d['zile']; A=d['orar']; B=json.load(open(sys.argv[1])); out=sys.argv[2]
LS={'Dorohoi':'D','Șendriceni':'Ș'}
def prof(o):
    P=collections.defaultdict(lambda: collections.defaultdict(dict))
    for c,zz in o.items():
        for z,hh in zz.items():
            for h,x in hh.items():
                for p in x['prof']: P[p['p']][z][int(h)]=(c,loc[c])
    return P
PA,PB=prof(A),prof(B)
def r2(m): return [z for z in Z if len({v[1] for v in m[z].values()})>1]
def fer(m): return sum(max(m[z])-min(m[z])+1-len(m[z]) for z in Z if m[z])
def zistr(m,z):
    if not m[z]: return "–"
    return " ".join(f"{h}{LS[v[1]]}" for h,v in sorted(m[z].items()))
def mutate(p):
    n=0
    for c in A:
        for z in Z:
            for h in set(A[c][z])|set(B[c][z]):
                a=A[c][z].get(h);b=B[c][z].get(h)
                if json.dumps(a,sort_keys=True)!=json.dumps(b,sort_keys=True):
                    if (a and any(q['p']==p for q in a['prof'])) or (b and any(q['p']==p for q in b['prof'])): n+=1
    return n
F="Calibri Light"; f=Font(name=F,size=10); fb=Font(name=F,size=10,bold=True); ft=Font(name=F,size=14,bold=True); fh=Font(name=F,size=10,bold=True,color="FFFFFF")
hf=PatternFill("solid",fgColor="1F4E78"); bun=PatternFill("solid",fgColor="A9D08E"); rau=PatternFill("solid",fgColor="F4B084"); gri=PatternFill("solid",fgColor="EDEDED")
th=Side(style="thin",color="999999"); bd=Border(left=th,right=th,top=th,bottom=th)
wrap=Alignment(wrap_text=True,vertical="top"); ctr=Alignment(horizontal="center",vertical="top",wrap_text=True)
def antet(ws,r,h,w):
    for i,x in enumerate(h,1):
        c=ws.cell(r,i,x); c.font=fh; c.fill=hf; c.alignment=ctr; c.border=bd
    for i,x in enumerate(w,1): ws.column_dimensions[L(i)].width=x
    ws.row_dimensions[r].height=44
def cel(ws,r,i,v,b=False,center=True,fill=None):
    c=ws.cell(r,i,v); c.font=fb if b else f; c.border=bd; c.alignment=ctr if center else wrap
    if fill: c.fill=fill
wb=Workbook()
s=wb.active; s.title="Pe profesori"
s["A1"]="Ce s-a schimbat la fiecare profesor după reorganizarea orarului"; s["A1"].font=ft
s["A2"]="Zilele: Lu, Ma, Mi, Jo, Vi. „Zile în două locații” = zile cu ore și la Dorohoi, și la Șendriceni. Verde = mai bine, portocaliu = mai rău."; s["A2"].font=f
H=["Profesor","Zile cu ore – înainte","Zile cu ore – după","Zile în două locații – înainte","Zile în două locații – după","Nr. – înainte","Nr. – după","Ferestre – înainte","Ferestre – după","Ore mutate","Pe scurt"]
antet(s,4,H,[28,16,16,16,16,8,8,9,9,8,46])
r=5; T=[0]*4
ab=lambda zs:", ".join(z[:2] for z in zs) or "–"
for p in sorted(set(PA)|set(PB)):
    a,b=PA[p],PB[p]
    ra,rb,fa,fb_=r2(a),r2(b),fer(a),fer(b); n=mutate(p)
    za=[z for z in Z if a[z]]; zb=[z for z in Z if b[z]]
    T[0]+=len(ra);T[1]+=len(rb);T[2]+=fa;T[3]+=fb_
    msg=[]
    zi=lambda n: "o zi" if n==1 else f"{n} zile"
    fe=lambda n: "o fereastră" if n==1 else f"{n} ferestre"
    if len(rb)<len(ra): msg.append(f"cu {zi(len(ra)-len(rb))} mai puțin în două locații")
    elif len(rb)>len(ra): msg.append(f"cu {zi(len(rb)-len(ra))} mai mult în două locații")
    elif ra and ra!=rb: msg.append("același număr de zile în două locații, dar în alte zile")
    if fb_<fa: msg.append(f"{fe(fa-fb_)} mai puțin")
    elif fb_>fa: msg.append(f"{fe(fb_-fa)} mai mult")
    if not msg: msg.append("neschimbat" if n==0 else "orele s-au mutat, fără efect pe zile sau ferestre")
    v=[p,ab(za),ab(zb),ab(ra),ab(rb),len(ra),len(rb),fa,fb_,n,"; ".join(msg)]
    for i,x in enumerate(v,1):
        fill=None
        if i in(6,7) and len(ra)!=len(rb): fill=bun if len(rb)<len(ra) else rau
        if i in(8,9) and fa!=fb_: fill=bun if fb_<fa else rau
        cel(s,r,i,x,b=(i==1),center=(i not in(1,11)),fill=fill)
    r+=1
for i,x in enumerate(["TOTAL","","","","",T[0],T[1],T[2],T[3],"",""],1): cel(s,r,i,x,b=True,fill=gri)
s.freeze_panes="B5"
z=wb.create_sheet("Zilele pe profesori")
z["A1"]="Ziua fiecărui profesor înainte și după (ora + locația: D = Dorohoi, Ș = Șendriceni)"; z["A1"].font=ft
z["A2"]="Doar profesorii la care s-a schimbat ceva. Rândurile marcate au zi în două locații."; z["A2"].font=f
antet(z,4,["Profesor","Zi","Înainte","După"],[28,10,34,34])
r=5
for p in sorted(set(PA)|set(PB)):
    a,b=PA[p],PB[p]
    if all(zistr(a,x)==zistr(b,x) for x in Z): continue
    for x in Z:
        sa,sb=zistr(a,x),zistr(b,x)
        if sa=="–" and sb=="–": continue
        cel(z,r,1,p,b=True,center=False); cel(z,r,2,x)
        cel(z,r,3,sa,fill=rau if x in r2(a) else None); cel(z,r,4,sb,fill=rau if x in r2(b) else (bun if x in r2(a) else None))
        r+=1
z.freeze_panes="A5"
c=wb.create_sheet("Ore mutate pe clase")
c["A1"]="Orele mutate la fiecare clasă"; c["A1"].font=ft
antet(c,3,["Clasa","Zi","Ora","Înainte","După"],[8,10,6,46,46])
txt=lambda x: "–" if not x else f"{x['disc']} ({', '.join(q['p'].split()[0]+('' if q['per']=='T' else ' '+q['per']) for q in x['prof'])})"
r=4
for cl in A:
    for x in Z:
        for h in sorted(set(A[cl][x])|set(B[cl][x]),key=int):
            a=A[cl][x].get(h);b=B[cl][x].get(h)
            if json.dumps(a,sort_keys=True)!=json.dumps(b,sort_keys=True):
                for i,v in enumerate([cl,x,int(h),txt(a),txt(b)],1): cel(c,r,i,v,b=(i==1),center=(i<=3))
                r+=1
c.freeze_panes="A4"
for ws in wb:
    ws.page_setup.paperSize=9; ws.page_setup.orientation="landscape"; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0; ws.sheet_properties.pageSetUpPr.fitToPage=True
wb.save(out); print(T)
