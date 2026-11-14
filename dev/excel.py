import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L
o=json.load(open('rez.json'))
F="Calibri Light"
f=Font(name=F,size=10); fb=Font(name=F,size=10,bold=True); ft=Font(name=F,size=14,bold=True); fh=Font(name=F,size=10,bold=True,color="FFFFFF")
hf=PatternFill("solid",fgColor="1F4E78"); ok=PatternFill("solid",fgColor="E2EFDA"); rau=PatternFill("solid",fgColor="FCE4D6"); gri=PatternFill("solid",fgColor="F2F2F2")
th=Side(style="thin",color="999999"); bd=Border(left=th,right=th,top=th,bottom=th)
wrap=Alignment(wrap_text=True,vertical="top"); ctr=Alignment(horizontal="center",vertical="top",wrap_text=True)
def antet(ws,r,h,widths):
    for i,x in enumerate(h,1):
        c=ws.cell(r,i,x); c.font=fh; c.fill=hf; c.alignment=ctr; c.border=bd
    for i,w in enumerate(widths,1): ws.column_dimensions[L(i)].width=w
    ws.row_dimensions[r].height=58
def cel(ws,r,i,v,b=False,center=True,fill=None,fmt=None):
    c=ws.cell(r,i,v); c.font=fb if b else f; c.border=bd; c.alignment=ctr if center else wrap
    if fill: c.fill=fill
    if fmt: c.number_format=fmt
    return c
NOTE={
 "IX F":"Comasată: plan 6 săpt. = 180 ore = 150 ore stagiu (foaia ta) + 30 ore curriculum pentru aprofundare (ora a 3-a de matematică, în orar).",
 "IX G":"La fel ca IX F.","IX I":"La fel ca IX F.","IX J":"La fel ca IX F.",
 "X J":"Comasată: foaia ta are 3 săpt. × 30 = 90 ore (Matoschi), încadrarea are doar 84 ore la stagiu. Lipsesc 6 ore în încadrare.",
 "XII J":"Comasată: foaia ta are Gavriluță S30–S31 = 60 ore, încadrarea are 66 ore (Costache 90 + Gavriluță 66 = 156 față de 150 în plan). Sunt 6 ore în plus în încadrare.",
 "XI F":"Modulul Conducerea automobilului: plan 3 ore/săpt. × 27 = 81 ore; în orar sunt 51 (Bunduc 27 teorie + 24 IP, joi ora a 7-a). Lipsesc 30 de ore – de lămurit dacă se fac individual. Conducerea pe elevi (Botezatu 390, Ciobanu 330) e separată, în afara orarului.",
 "XI G":"Modulul Conducere și elemente de legislație rutieră: plan 4 ore/săpt. × 27 = 108 ore; în orar 54 ore legislație (9 săpt. × 6 ore, Ciobanu); restul de 54 = conducere individuală pe elev (30 B + 24 Tr), în afara orarului – corect.",
 "XI L":"La fel ca XI G.",
 "XI K":"Planul de învățământ (găsit pe net): panificație LT 3 + IP 5, patiserie LT 4 + IP 5, făinoase LT 2 + IP 2 ore/săpt.; stagiu CDL 300 ore. Încadrarea se potrivește exact. În orar totalul e corect (Scripcaru 9 ore, Zvonaru 12 ore Aplicații), dar celulele sunt denumite altfel: panificație 4 (plan 3), patiserie 2 (plan 4), făinoase 3 (plan 2) – de corectat doar denumirile.",
}
wb=Workbook(); s=wb.active; s.title="Sinteza pe clase"
s["A1"]="Practica pe clase – verificare plan-cadru / încadrare / orar / practică comasată (2026-2027)"; s["A1"].font=ft
s["A2"]="Surse: planurile-cadru din Drive „Aplicatie ORAR”, încadrarea CATEDRE … 28 09 2026, orarul 2026-2027 (zilele de Aplicații practice sunt aceleași și în orarul reorganizat), foaia PRACTICĂ COMASATĂ din ORAR CLASE 2026-2027.xlsx."; s["A2"].font=f
H=["Clasa","Nivel","Săpt. de curs","Specialitate + practică săpt. – plan (ore/an)","În orar, conform încadrării (ore/an)","din care instruire practică cu maistrul (ore/an)","Diferență orar – plan","Comasată – plan (săpt.)","Comasată – plan (ore)","Foaia ta: săpt.","Foaia ta: ore/săpt.","Foaia ta: total ore","Perioada","Încadrare: ore stagiu","Curriculum aprofundare (IX)","Diferență încadrare – foaie","Diferență foaie (+ aprofundare) – plan","Concluzie / observații"]
antet(s,4,H,[7,15,8,12,12,12,10,9,9,8,8,9,30,10,11,10,12,60])
r=5
for c in o['clase']:
    v=[c['clasa'],c['niv'],c['sapt'],c['spec_plan_an'],c['spec_inc'],c['pip_an'],f"=E{r}-D{r}",c['com_plan_s'],c['com_plan_o'],c['com_s'],c['com_os'],f"=J{r}*K{r}",c['com_per'],c['stag_inc'],c['caip'] or 0,f"=N{r}-L{r}",f"=L{r}+O{r}-I{r}",NOTE.get(c['clasa'],"Totul se potrivește.")]
    for i,x in enumerate(v,1): cel(s,r,i,x,b=(i==1),center=(i not in(2,13,18)))
    bun=c['clasa'] not in NOTE or c['clasa']=="XI K" or NOTE[c['clasa']].startswith("La fel ca IX") or c['clasa']=="IX F"
    s.cell(r,18).fill=ok if bun else rau
    r+=1
s.freeze_panes="B5"
s.cell(r+1,1,"Coloanele G, P și Q se calculează singure: 0 = se potrivește. Verde = în regulă, portocaliu = de lămurit.").font=f

m=wb.create_sheet("Module")
m["A1"]="Modulele de specialitate – plan față de încadrarea din orar"; m["A1"].font=ft
H=["Clasa","Modul (plan de învățământ)","Ore/săpt. plan","Săpt.","Plan ore/an","Încadrare: teorie / laborator (ore/an)","Încadrare: instruire practică cu maistrul (ore/an)","Total în orar","Diferență","Profesori ((IP) = instruire practică)","Conducere individuală pe elevi (în afara orarului)"]
antet(m,3,H,[7,52,9,7,9,13,14,10,10,34,14])
r=4
for x in o['module']:
    v=[x['clasa'],x['modul'],x['osapt'],x['sapt'],f"=C{r}*D{r}" if x['osapt'] is not None else None,x['dsp'],x['pip'],f"=F{r}+G{r}",f"=H{r}-E{r}" if x['osapt'] is not None else None,x['prof'],x.get('indiv') or None]
    for i,y in enumerate(v,1): cel(m,r,i,y,center=(i not in(2,10)))
    bad=x['osapt'] is not None and x['plan']!=x['dsp']+x['pip']
    if bad: m.cell(r,9).fill=rau
    r+=1
m.freeze_panes="C4"

t=wb.create_sheet("Profesor x clasa")
t["A1"]="Fiecare profesor la fiecare clasă: orele din orar față de încadrare"; t["A1"].font=ft
t["A2"]="Ore pe an. Unde profesorul are ore pe perioade (P1/P2) sau în alternanță, orarul dă un interval (minim–maxim); încadrarea trebuie să cadă în interval."; t["A2"].font=f
H=["Clasa","Profesor","Încadrare (ore/an)","Orar – minim","Orar – maxim","Se potrivește"]
antet(t,4,H,[7,34,12,12,12,12])
r=5
for x in o['tp']:
    v=[x['clasa'],x['prof'],x['inc'],x['minim'],x['maxim'],"da" if x['ok'] else "NU"]
    for i,y in enumerate(v,1): cel(t,r,i,y,center=(i!=2),fill=(ok if i==6 and x['ok'] else rau if i==6 else None))
    r+=1
t.freeze_panes="C5"

for ws in wb:
    ws.page_setup.paperSize=9; ws.page_setup.orientation="landscape"; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0
    ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.print_options.gridLines=False
wb.save("/tmp/orar/pract/Verificare practica 2026-2027.xlsx")
