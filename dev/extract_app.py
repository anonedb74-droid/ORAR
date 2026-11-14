import sys,re,json
sys.path.insert(0,"/tmp/orar")
from collections import defaultdict
from openpyxl import load_workbook
from inc_data import D
ORAR="/mnt/user-data/uploads/ORAR 2026-2027/ORAR 2026-2027.xlsm"
LISTA="/mnt/user-data/uploads/ORAR 2026-2027/ORAR CLASE/ORAR CLASE 2026-2027.xlsx"
rows=json.load(open("cat_nou.json"))
sq=lambda s: re.sub(r"\s+"," ",str(s)).strip()
SQ=lambda s: sq(s).upper()
LIC=["IX F","IX G","IX I","IX J","X B","X D","X F","X G","X J","XI B","XI F","XI G","XI I","XI J","XI K","XI L","XII C","XII I","XII J"]
W={"IX F":30,"IX G":30,"IX I":30,"IX J":30,"X D":34,"X J":34,"X B":28,"X F":28,"X G":28,"XI I":32,"XI J":33,"XI B":27,"XI F":27,"XI G":27,"XI K":27,"XI L":27,"XII C":29,"XII I":29,"XII J":29}
def title(n):
    n=sq(n)
    return " ".join(w.capitalize() if w.isupper() or w.islower() else w for w in n.split())
CANON={}
for x in rows:
    p=sq(x["p"]); CANON[p]=title(p)
CANON["STEFAN ILIE"]="Ștefan Nicolae"
# ---- clase din Lista
wl=load_workbook(LISTA,data_only=True)["Lista"]
clase=[]
for r in wl.iter_rows(min_row=2,values_only=True):
    if not r[0] or str(r[0]).strip() not in LIC: continue
    c=str(r[0]).strip(); sub=str(r[2] or ""); parts=[s.strip() for s in sub.split("·")]
    loc="Dorohoi" if "Dorohoi" in sub else "Șendriceni"
    dirig=re.sub(r"^Diriginte:\s*","",str(r[3] or "")).strip()
    clase.append(dict(id=c,calificare=parts[0] if parts else "",locatie=loc,diriginte=dirig,saptamani=W[c],
        nivel=("profesional" if c in ("X B","X F","X G","XI B","XI F","XI G","XI K","XI L") else "liceu")))
clase.sort(key=lambda k:LIC.index(k["id"]))
# ---- incadrare
stg={(cl,tip,SQ(d)[:23]) for p,_,_,rr in D for tip,d,cl,ore,orar,obs in rr if orar=="STAGIU"}
cnd={(cl,tip,SQ(d)[:23]) for p,_,_,rr in D for tip,d,cl,ore,orar,obs in rr if orar=="COND"}
inc=[]
for x in rows:
    cl=sq(x["cl"]); d=sq(x["d"]).replace("_x000D_","").strip(); motiv=""
    if cl not in LIC: motiv="Ghilea / gimnaziu"
    elif "COND" in SQ(x["post"]) or (cl,x["tip"],SQ(d)[:23]) in cnd: motiv="conducere (individual)"
    elif SQ(d).startswith("STAGIU") or (cl,x["tip"],SQ(d)[:23]) in stg or (cl.startswith("IX") and x["cdl"]=="CDL"): motiv="stagiu / practică comasată"
    # XI F: ora de conducere de la Bunduc (PIP, 24 ore) se face in orele de curs (spus de Daniel, 13.11) -> intra in orar
    if cl=="XI F" and x["tip"]=="PIP" and SQ(d)=="CONDUCEREA AUTOMOBILULUI": motiv=""
    inc.append(dict(p=CANON[sq(x["p"])],clasa=cl,disciplina=d,tip=x["tip"],post=sq(x["post"] or ""),oreAn=x["ore"],
                    inOrar=(motiv==""),motiv=motiv,cdl=x["cdl"] or ""))
# ---- orar
wb=load_workbook(ORAR,data_only=True)
def ncl(c):
    c=re.sub(r"[\s*/]+","",str(c)).upper()
    m=re.match(r"^(XII|XI|IX|X)([A-Z])$",c); return (m.group(1)+" "+m.group(2)) if m else None
ZILE=["Luni","Marți","Miercuri","Joi","Vineri"]
def slots(ws):
    out=[];day=0
    for r in range(4,ws.max_row+1):
        h=ws.cell(r,2).value
        if h is None: continue
        if str(h).strip()=="1": day+=1
        if day>5: break
        out.append((r,day,int(str(h).strip()),sq(ws.cell(r,3).value or "")))
    return out
clopot={"Dorohoi":{},"Șendriceni":{}}
cells={}
for sh,loc in (("ORAR SENDRICENI","Șendriceni"),("ORAR DOROHOI","Dorohoi")):
    ws=wb[sh]; sl=slots(ws)
    for r,d,h,t in sl:
        if t: clopot[loc].setdefault(ZILE[d-1],{})[h]=t.replace(".",":")
    for col in range(4,ws.max_column+1):
        cl=ws.cell(1,col).value
        if cl and SQ(cl)=="ZIUA": break
        c=ncl(cl) if cl else None
        if not c: continue
        for r,d,h,t in sl:
            v=ws.cell(r,col).value
            if v and str(v).strip(): cells[(c,d,h)]=dict(disc=sq(v),prof=[])
ws=wb["ORAR SENDRICENI"]; sl=slots(ws)
start=[c for c in range(1,ws.max_column+1) if SQ(ws.cell(1,c).value or "")=="CLASA"][1]
onames=[]
for col in range(start+1,ws.max_column+1):
    t=ws.cell(1,col).value
    if t: onames.append((col,SQ(t)))
def canon_of(o):
    k=o.split()[0]
    if o=="STEFAN NICOLAE": return "Ștefan Nicolae"
    if o=="TEOANA ANA MARIA": return CANON["TEOANU ANAMARIA"]
    if o=="DOHOTARIU VIOREL": return CANON["DOHOTARIU DUMITRU VIOREL"]
    c=[p for p in CANON if p.split()[0]==k]
    if len(c)>1: c=[p for p in c if any(w in p.split()[1:] for w in o.split()[1:])]
    assert len(c)==1,(o,c)
    return CANON[c[0]]
miss=[]
for col,o in onames:
    P=canon_of(o)
    for r,d,h,t in sl:
        v=ws.cell(r,col).value
        if not v or not str(v).strip(): continue
        raw=str(v).strip()
        per="P1" if raw.endswith("/") else ("P2" if raw.startswith("/") else ("A" if "*" in raw else "T"))
        for part in [p for p in re.split(r"[/,+]",raw) if p.strip()]:
            c=ncl(part)
            if not c: miss.append((o,raw)); continue
            cells.setdefault((c,d,h),dict(disc="",prof=[]))["prof"].append(dict(p=P,per=per))
# XII I Educatie fizica: Stefan primele 6 saptamani (P1), Botezatu apoi (P2) - spus de Daniel
for (c,d,h),v in cells.items():
    if c=="XII I" and "FIZIC" in v["disc"].upper():
        for x in v["prof"]:
            x["per"]="P1" if x["p"]=="Ștefan Nicolae" else "P2"
        print("XII I ed fiz:",d,h,v)
orar={c["id"]:{z:{} for z in ZILE} for c in clase}
for (c,d,h),v in cells.items():
    orar[c][ZILE[d-1]][str(h)]=v
prof=sorted({x["p"] for x in inc}, key=lambda s:s.lower())
data=dict(versiune=1,an="2026-2027",zile=ZILE,clase=clase,profesori=prof,incadrare=inc,orar=orar,clopot=clopot,
  locatiiMaxOre={"Dorohoi":{"Luni":7,"Marți":6,"Miercuri":6,"Joi":6,"Vineri":6},"Șendriceni":{"Luni":7,"Marți":7,"Miercuri":7,"Joi":7,"Vineri":6}})
json.dump(data,open("app/data_initial.json","w"),ensure_ascii=False)
print("clase",len(clase),"prof",len(prof),"inc",len(inc),"celule",len(cells),"miss",miss[:5])
print(json.dumps(clopot,ensure_ascii=False)[:600])
print(clase[:2])
