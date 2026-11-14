from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

V="de verificat"
T={
"L9":dict(niv="Liceu tehnologic",sapt=30,ps=6,po=180,plan="Ordin 4.350/2025 (M.Of. 565 bis/2026)",spec=10,gen=[
 ("Limba și literatura română",3,""),("Limba modernă 1",2,""),("Limba modernă 2",1,""),("Matematică",2,""),("Fizică",1,""),("Chimie",1,""),("Biologie",1,""),
 ("Istorie",1,""),("Geografie",1,""),("Disciplină socio-umană",1,""),("Religie",1,""),("Discipline din domeniul arte",1,""),("Educație fizică și sport",1,""),
 ("Tehnologia informației și a comunicațiilor",1,""),("Dezvoltare personală și consiliere în carieră",1,"")]),
"L10":dict(niv="Liceu tehnologic",sapt=35,ps=3,po=90,plan="OMECTS 3081/2010, Anexa 2",spec=10,gen=[
 ("Limba și literatura română",3,""),("Limba modernă 1",2,""),("Limba modernă 2",1,""),("Matematică",3,"2 TC + 1 CD"),("Fizică",2,""),("Chimie",1,""),("Biologie",1,""),
 ("Istorie",1,""),("Geografie",1,""),("Socio-umane",1,""),("Religie",1,""),("Educație fizică",1,""),("Tehnologia informației și a comunicațiilor",1,""),("Educație antreprenorială",1,"")]),
"L11R":dict(niv="Liceu tehnologic",sapt=33,ps=5,po=150,plan="OMECI 3412/2009, Anexa 1 (resurse naturale)",spec=11,gen=[
 ("Limba și literatura română",3,""),("Limba modernă 1",2,""),("Limba modernă 2",2,"1 TC + 1 CD"),("Matematică",3,""),("Chimie",2,""),("Biologie",1,""),
 ("Istorie",1,""),("Geografie",1,""),("Economie",1,""),("Religie",1,""),("Educație fizică",1,""),("Tehnologia informației și a comunicațiilor",1,"")]),
"L12R":dict(niv="Liceu tehnologic",sapt=31,ps=5,po=150,plan="OMECI 3412/2009, Anexa 1 (resurse naturale)",spec=11,gen=[
 ("Limba și literatura română",3,""),("Limba modernă 1",2,""),("Limba modernă 2",2,"1 TC + 1 CD"),("Matematică",3,""),("Chimie",1,""),("Biologie",2,""),
 ("Istorie",1,""),("Geografie",1,""),("Economie aplicată",1,""),("Religie",1,""),("Educație fizică",1,""),("Tehnologia informației și a comunicațiilor",1,"")]),
"L11S":dict(niv="Liceu tehnologic",sapt=33,ps=4,po=120,plan="OMECI 3412/2009, Anexa 1 (servicii)",spec=12,gen=[
 ("Limba și literatura română",3,""),("Limba modernă 1",2,""),("Limba modernă 2",2,""),("Matematică",3,""),("Istorie",2,""),("Geografie",1,""),
 ("Economie",2,""),("Religie",1,""),("Educație fizică",1,""),("Tehnologia informației și a comunicațiilor",1,"")]),
"L12S":dict(niv="Liceu tehnologic",sapt=31,ps=5,po=150,plan="OMECI 3412/2009, Anexa 1 (servicii)",spec=11,gen=[
 ("Limba și literatura română",3,""),("Limba modernă 1",2,""),("Limba modernă 2",2,""),("Matematică",3,""),("Istorie",1,""),("Geografie",2,""),
 ("Economie aplicată",2,""),("Religie",1,""),("Educație fizică",1,""),("Tehnologia informației și a comunicațiilor",1,"")]),
"P10":dict(niv="Profesională 3 ani",sapt=32,ps=9,po=270,plan="Plan-cadru înv. profesional cl. a X-a; plan de învățământ OMEN 3915/2017",spec=21,gen=[
 ("Limba și literatura română",2,""),("Limba modernă 1",1,""),("Limba modernă 2",1,""),("Matematică",1,""),("Fizică",1,""),("Chimie",1,""),
 ("Socio-umane / Psihologie",1,""),("Religie",1,""),("Educație fizică",2,""),("Consiliere și orientare",1,"")]),
"P11":dict(niv="Profesională 3 ani",sapt=30,ps=10,po=300,plan="Plan-cadru înv. profesional cl. a XI-a; plan de învățământ OMEN 3500/2018",spec=21,gen=[
 ("Limba și literatura română",2,""),("Limba modernă 1",2,""),("Limba modernă 2",1,""),("Matematică",1,""),("Fizică",2,""),
 ("Istoria evreilor. Holocaustul",1,""),("Socio-umane / Educație antreprenorială",1,""),("Educație fizică",2,""),("Consiliere și orientare",1,"")]),
}
LIPSA="lipsește planul de învățământ din scanări"
C=[ # clasa, sablon, domeniu/calificare, module[(nume,ore/sapt,obs)], CDL/stagiu, obs
("IX F","L9","Mecanică",[("Bazele desenului tehnic",2,""),("Lăcătușărie generală",4,""),("Organe de mașini",2,""),("Asamblări mecanice",2,"")],"Dispozitive utilizate în domeniul mecanicii auto",""),
("IX G","L9","Mecanică",[("Bazele desenului tehnic",2,""),("Lăcătușărie generală",4,""),("Organe de mașini",2,""),("Asamblări mecanice",2,"")],"Repararea organelor de bază ale tractoarelor și mașinilor agricole",""),
("IX I","L9","Industrie alimentară",[("Securitatea și sănătatea în muncă și protecția mediului în industria alimentară",2,""),("Microbiologia și igiena în industria alimentară",4,""),("Operații de bază în laborator în industria alimentară",4,"")],"Materii prime și materiale în industria alimentară",""),
("IX J","L9","Turism și alimentație (Gastronomie)",[("Bazele contabilității",2,""),("Etică și comunicare",2,""),("Structuri de primire turistică",2,""),("Procese și calitate în HoReCa",4,"")],
 "Igiena și protecția muncii în unitățile de alimentație",""),
("X D","L10","Protecția mediului",[("Poluarea și protecția mediului",4,""),("Elemente de gospodărire a apelor",2,""),("Măsurarea mărimilor tehnice",4,"")],"Monitorizarea calității factorilor de mediu",""),
("X J","L10","Turism și alimentație",[("Etică și comunicare profesională",2,""),("Contabilitate generală",2,""),("Sortimentul de preparate și băuturi",4,""),("Sisteme de servire",2,"")],"Organizarea în domeniul alimentației",""),
("XI I","L11R","Tehnician în industria alimentară",[("Biochimia produselor alimentare",3,""),("Tehnologii specifice în industria alimentară fermentativă",3,""),("Tehnologii specifice de obținere a produselor de morărit și panificație",3,""),("CDL: Igiena în industria alimentară",2,"")],
 "Stagiu: Tehnici de laborator în industria alimentară","Scanarea nu are eticheta clasei; potrivită după calificare și CDL"),
("XI J","L11S","Tehnician în gastronomie",[("Administrarea firmei",2,""),("Marketing",2,""),("Contabilitate",2,""),("Producția gastronomică",4,""),("CDL: Calitatea și siguranța mediului de muncă",2,"")],"Stagiu de pregătire practică în gastronomie",""),
("XII C","L12R","Tehnician veterinar",[("Gestionarea unității agricole",2,""),("Bolile infecțioase",2,""),("Bolile chirurgicale",3,""),("Bolile obstetricale",2,""),("CDL: Noțiuni de toxicologie",2,"")],
 "Stagii: Expertiza sanitar-veterinară a cărnii și a produselor din carne; Conducerea tractorului și auto",""),
("XII I","L12R","Tehnician în industria alimentară",[("Tehnologii specifice de obținere a produselor de origine animală",5,V+": în orar sunt 6"),("Tehnologii specifice de prelucrare a legumelor și fructelor",4,V+": în orar sunt 3"),("CDL: Produse de panificație",2,"")],
 "Stagii: Asigurarea calității produselor alimentare; Tehnologii specifice în industria alimentară extractivă",""),
("XII J","L12S","Tehnician în gastronomie",[("Politici de marketing",2,""),("Analiza economico-financiară",2,""),("Negociere și contractare",2,""),("Calitatea în gastronomie",2,""),("Promovarea producției gastronomice",1,""),("CDL: Particularitățile cateringului",2,"")],
 "Stagiu de pregătire practică privind planificarea în gastronomie",""),
("X B","P10","Turism și alimentație (bucătar, cofetar-patiser, ospătar)",[("Etică și comunicare profesională",4,""),("Contabilitate generală",2,""),("Sortimentul de preparate și băuturi",9,""),("Sisteme de servire",6,"")],"Întocmirea meniurilor și servirea în restaurație",""),
("X F","P10","Mecanică – Mecanic auto",[("Măsurări tehnice",7,""),("Reprezentarea organelor de mașini",2,""),("Asamblări mecanice",6,""),("Automobile",6,"")],"Sisteme de siguranță a automobilelor",""),
("X G","P10","Mecanică – Mecanic agricol",[("Măsurări tehnice",7,""),("Reprezentarea organelor de mașini",4,""),("Asamblări mecanice",10,"")],"Motoare cu ardere internă și tractoare utilizate în agricultură",""),
("XI B","P11","Ospătar (chelner) vânzător în unități de alimentație",[("Servirea în restaurație",11,""),("Organizarea meselor speciale",10,"")],"Activități de protocol în unități de alimentație",""),
("XI F","P11","Mecanic auto",[("Pregătirea automobilului pentru exploatare",7,""),("Mentenanța automobilului",11,""),("Conducerea automobilului",3,"")],"Lucrări de reparare și recondiționare a componentelor automobilului",""),
("XI G","P11","Mecanic agricol",[("Conducere și elemente de legislație rutieră",4,""),("Repararea mașinilor și utilajelor agricole",9,""),("Întreținerea mașinilor și utilajelor agricole",3,""),("Executarea lucrărilor agricole",5,"")],
 "Tehnologii de exploatare a agregatelor agricole",""),
("XI K","P11","Brutar-patiser-preparator produse făinoase",None,"Igiena în industria alimentară","S-a scanat doar planul-cadru; "+LIPSA+". În orar: Fabricarea produselor de panificație 4, de patiserie 2, făinoase 3, Aplicații 12."),
("XI L","P11","Mecanic agricol",[("Conducere și elemente de legislație rutieră",4,""),("Repararea mașinilor și utilajelor agricole",9,""),("Întreținerea mașinilor și utilajelor agricole",3,""),("Executarea lucrărilor agricole",5,"")],
 "Tehnologii de exploatare a agregatelor agricole",""),
]

F="Calibri Light"
f=Font(name=F,size=11); fb=Font(name=F,size=11,bold=True); ft=Font(name=F,size=14,bold=True); fh=Font(name=F,size=11,bold=True,color="FFFFFF")
hf=PatternFill("solid",fgColor="1F4E78"); yf=PatternFill("solid",fgColor="FFF2CC"); gf=PatternFill("solid",fgColor="E2EFDA")
th=Side(style="thin",color="999999"); bd=Border(left=th,right=th,top=th,bottom=th)
wrap=Alignment(wrap_text=True,vertical="top"); ctr=Alignment(horizontal="center",vertical="top",wrap_text=True)

wb=Workbook()
d=wb.active; d.title="Discipline"
s=wb.create_sheet("Sinteza pe clase",0)
n=wb.create_sheet("De lamurit")

# Discipline
d["A1"]="Discipline și module pe clase – ore pe săptămână și ore pe an (2026-2027)"; d["A1"].font=ft
d["A2"]="Sursa: planurile-cadru și planurile de învățământ scanate în Drive, folderul „Aplicatie ORAR”. Rândurile galbene sunt de verificat pe hârtie."; d["A2"].font=f
hd=["Clasa","Disciplină / Modul","Tip","Ore/săpt.","Săpt. cursuri (plan)","Ore/an","Observații"]
for i,h in enumerate(hd,1):
    c=d.cell(4,i,h); c.font=fh; c.fill=hf; c.alignment=ctr; c.border=bd
r=5
for cl,tp,dom,mods,cdl,obs in C:
    t=T[tp]
    rows=[(nm,o,"Cultură generală",ob) for nm,o,ob in t["gen"]]
    if mods: rows+=[(nm,o,"Specialitate / practică săptămânală",ob) for nm,o,ob in mods]
    else: rows.append(("Specialitate și pregătire practică (module nedetaliate)",t["spec"],"Specialitate / practică săptămânală",LIPSA))
    assert sum(x[1] for x in rows)==sum(g[1] for g in t["gen"])+t["spec"],cl
    for nm,o,tip,ob in rows:
        vals=[cl,nm,tip,o,t["sapt"],f"=D{r}*E{r}",ob]
        for i,v in enumerate(vals,1):
            c=d.cell(r,i,v); c.font=f; c.border=bd; c.alignment=ctr if i in(1,4,5,6) else wrap
            if ob: c.fill=yf
        r+=1
last=r-1
for i,w in enumerate([8,58,32,10,12,10,48],1): d.column_dimensions[get_column_letter(i)].width=w
d.freeze_panes="A5"; d.auto_filter.ref=f"A4:G{last}"

# Sinteza
s["A1"]="Sinteză pe clase – ore pe săptămână și total pe an școlar (2026-2027)"; s["A1"].font=ft
s["A2"]="Orele pe săptămână și orele de cursuri se calculează din foaia „Discipline”. Săptămânile sunt cele tipărite în planul-cadru (vezi foaia „De lamurit”, punctul 1)."; s["A2"].font=f
hs=["Clasa","Nivel","Domeniu / Calificare","Ore/săpt. cultură generală","Ore/săpt. specialitate și practică","Total ore/săpt.","Săpt. cursuri (plan)","Ore cursuri/an",
    "Săpt. practică comasată / stagiu","Ore practică comasată / stagiu","Total ore/an","CDL / stagiu","Plan-cadru","Observații"]
for i,h in enumerate(hs,1):
    c=s.cell(4,i,h); c.font=fh; c.fill=hf; c.alignment=ctr; c.border=bd
s.row_dimensions[4].height=62
r=5
for cl,tp,dom,mods,cdl,obs in C:
    t=T[tp]; rng=f"Discipline!$A$5:$A${last}"
    vals=[cl,t["niv"],dom,
      f'=SUMIFS(Discipline!$D$5:$D${last},{rng},A{r},Discipline!$C$5:$C${last},"Cultură generală")',
      f'=SUMIFS(Discipline!$D$5:$D${last},{rng},A{r},Discipline!$C$5:$C${last},"Specialitate / practică săptămânală")',
      f"=D{r}+E{r}",t["sapt"],f"=F{r}*G{r}",t["ps"],t["po"],f"=H{r}+J{r}",cdl,t["plan"],
      obs+(" Include 1 săpt. (30 ore) curriculum pentru aprofundare și inserție profesională." if tp=="L9" else "")]
    for i,v in enumerate(vals,1):
        c=s.cell(r,i,v); c.font=fb if i in(1,6,11) else f; c.border=bd; c.alignment=ctr if i in(1,4,5,6,7,8,9,10,11) else wrap
        if i in(6,11): c.fill=gf
        if obs and i==14: c.fill=yf
    r+=1
for i,w in enumerate([7,17,30,11,13,10,10,10,12,12,10,40,34,52],1): s.column_dimensions[get_column_letter(i)].width=w
s.freeze_panes="B5"

# De lamurit
n["A1"]="De lămurit / de verificat"; n["A1"].font=ft
items=[
"1. Săptămânile de cursuri. În tabel am pus săptămânile tipărite în planul-cadru (30, 31, 32, 33, 35). Pe scanări apar corecturi de mână care par recalculări pe mai puține săptămâni: 34 la X liceu, 32 la XI liceu, 28 la X profesională, 27 la XI profesională. Confirmă câte săptămâni de cursuri are fiecare an de studiu în 2026-2027 (regula R11). Orele pe săptămână nu se schimbă.",
"2. XI K (Brutar-patiser): s-a scanat doar planul-cadru, fără planul de învățământ cu modulele. Modulele le-am luat din orar doar ca observație.",
"3. Clasele din adresa cu CDL-urile (IX B, IX D, X H, X K) nu există în orar; în orar sunt 19 clase, inclusiv IX J și XI L. Am mers pe clasele din orar.",
"4. Planurile pentru XI și XII liceu sunt din 2009 și nu conțin Istoria evreilor. Holocaustul (XI) și Istoria comunismului (XII), care apar în orar. De aceea orarul are cu 1 oră pe săptămână mai mult decât planul scanat (vezi foaia „Comparatie cu orarul”).",
"5. Clasa a IX-a liceu: orarul are Matematică 3 ore, planul are 2. Presupun că ora în plus vine din cele 30 de ore/an de aprofundare; confirmă.",
"6. XI F, XI G, XI L: în orar sunt cu 1–2 ore de specialitate mai puțin decât cele 21 din plan. Conform notei din plan, orele de conducere se fac prin programare individuală; confirmă dacă asta e explicația.",
"7. XII C: vezi diferențele pe module din foaia „Comparatie cu orarul”.",
"8. Fișierul „MO 565 bis-2026 - Nota de fundamentare - partea I” nu are text recunoscut și nu l-am putut citi; nu conține ore pe clase.",
]
for i,tx in enumerate(items,3):
    c=n.cell(i,1,tx); c.font=f; c.alignment=wrap; n.row_dimensions[i].height=75
n.column_dimensions["A"].width=120

ORAR={ # ore/sapt numarate din ORAR 2026-2027.xlsm (foile ORAR SENDRICENI si ORAR DOROHOI)
"IX F":(30,"6-6-6-6-6","Matematică 3 în orar, 2 în plan (probabil ora de aprofundare, 30 ore/an)."),
"IX G":(30,"6-6-6-6-6","Matematică 3 în orar, 2 în plan (probabil ora de aprofundare, 30 ore/an)."),
"IX I":(30,"6-6-6-6-6","Matematică 3 în orar, 2 în plan (probabil ora de aprofundare, 30 ore/an)."),
"IX J":(30,"6-6-6-6-6","Matematică 3 în orar, 2 în plan (probabil ora de aprofundare, 30 ore/an)."),
"X D":(30,"6-6-6-6-6","Se potrivește pe fiecare disciplină."),
"X J":(30,"6-6-6-6-6","Se potrivește pe fiecare disciplină."),
"XI I":(31,"7-6-6-6-6","Istorie 2 în orar, 1 în plan (probabil a doua oră este Istoria evreilor. Holocaustul). Restul se potrivește."),
"XI J":(31,"7-6-6-6-6","În orar apare Istoria evreilor (1 oră), care nu e în planul din 2009. Restul se potrivește."),
"XII C":(31,"7-6-6-6-6","Geografie 2 în orar, 1 în plan; nu apare Istoria comunismului (apare la XII I și XII J). Module: Gestionarea unității agricole 1 (plan 2), Boli chirurgicale 2 (plan 3); în orar apare Expertiza sanitar-veterinară a cărnii 2 ore, care în plan este modul de stagiu."),
"XII I":(31,"7-6-6-6-6","În orar apare Istoria comunismului (1 oră), care nu e în planul din 2009. Module: 6 + 3 în orar, 5 + 4 citit din plan (de verificat pe hârtie)."),
"XII J":(30,"6-6-6-6-6","În orar apare Istoria comunismului (1 oră), care nu e în planul din 2009. Restul se potrivește."),
"X B":(33,"7-7-7-6-6","Totalul se potrivește. Specialitate: 9 ore pe module + 12 ore APLICAȚII = 21."),
"X F":(33,"7-7-7-6-6","Totalul se potrivește. Specialitate: 9 ore pe module + 12 ore APLICAȚII = 21."),
"X G":(33,"7-7-7-6-6","Totalul se potrivește. Specialitate: 9 ore pe module + 12 ore APLICAȚII = 21."),
"XI B":(34,"7-7-7-7-6","Totalul se potrivește. Specialitate 21 de ore."),
"XI F":(33,"7-7-6-7-6","Specialitate 20 de ore în orar, 21 în plan."),
"XI G":(32,"7-6-7-6-6","Specialitate 19 ore în orar, 21 în plan."),
"XI K":(34,"7-7-7-7-6","Totalul se potrivește. Specialitate 21 de ore (9 pe module + 12 APLICAȚII)."),
"XI L":(32,"6-6-7-7-6","Specialitate 19 ore în orar, 21 în plan."),
}
PR={"IX F":(6,150),"IX G":(6,150),"IX I":(6,150),"IX J":(6,150),"X B":(9,270),"X D":(3,90),"X F":(9,270),"X G":(9,270),"X J":(3,90),"XI B":(10,300),"XI F":(10,300),"XI G":(10,300),
"XI I":(5,150),"XI J":(4,120),"XI K":(10,300),"XI L":(10,300),"XII C":(5,150),"XII I":(5,150),"XII J":(5,150)}
k=wb.create_sheet("Comparatie cu orarul",1)
k["A1"]="Comparație: planuri-cadru față de orarul 2026-2027"; k["A1"].font=ft
k["A2"]="Orele din orar sunt numărate din Desktop\\ORAR\\ORAR 2026-2027\\ORAR 2026-2027.xlsm; practica comasată este din ORAR CLASE 2026-2027.xlsx, foaia PRACTICĂ COMASATĂ."; k["A2"].font=f
hk=["Clasa","Ore/săpt. plan","Ore/săpt. orar","Diferență","Ore pe zi în orar (L-V)","Practică comasată plan (ore)","Practică comasată orar (săpt.)","Practică comasată orar (ore)","Diferență ore practică","Ce diferă"]
for i,h in enumerate(hk,1):
    c=k.cell(4,i,h); c.font=fh; c.fill=hf; c.alignment=ctr; c.border=bd
k.row_dimensions[4].height=62
nC=len(C)
for j,(cl,tp,dom,mods,cdl,obs) in enumerate(C):
    r=5+j; o=ORAR[cl]; p=PR[cl]
    rs=f"'Sinteza pe clase'!$A$5:$A${4+nC}"
    vals=[cl,f"=INDEX('Sinteza pe clase'!$F$5:$F${4+nC},MATCH(A{r},{rs},0))",o[0],f"=C{r}-B{r}",o[1],
          f"=INDEX('Sinteza pe clase'!$J$5:$J${4+nC},MATCH(A{r},{rs},0))",p[0],p[1],f"=H{r}-F{r}",o[2]]
    for i,v in enumerate(vals,1):
        c=k.cell(r,i,v); c.font=fb if i in(1,4) else f; c.border=bd; c.alignment=wrap if i==10 else ctr
        if o[0]!=T[tp]["spec"]+sum(g[1] for g in T[tp]["gen"]) and i in(4,10): c.fill=yf
for i,w in enumerate([7,10,10,10,14,13,13,13,12,95],1): k.column_dimensions[get_column_letter(i)].width=w
k.freeze_panes="B5"

for ws in wb:
    ws.page_setup.paperSize=9; ws.page_setup.orientation="landscape"; ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0
    ws.sheet_properties.pageSetUpPr.fitToPage=True
wb.save("/home/claude/Ore pe clase - planuri-cadru si orar 2026-2027.xlsx")
