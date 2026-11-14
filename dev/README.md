# Unelte de dezvoltare – Aplicația ORAR

Nu sunt necesare pentru rularea aplicației (aceasta e doar `index.html` din rădăcină).

| Fișier | Rol |
|---|---|
| `index.src.html` | Sursa aplicației. `/*__DATA__*/null` se înlocuiește cu `data_initial.json`, iar `/*__PROPUNERE__*/null` cu `propunere_v2.0.json` → `index.html`. |
| `data_initial.json` | Datele inițiale: clase, profesori, încadrare (481 de rânduri), orarul din Excel, programul orelor, maximul de ore pe zi. |
| `propunere_v2.0.json` | Orarul reorganizat (5 zile în două locații, 9 ferestre). |
| `extract_app.py` | Construiește `data_initial.json` din Excelurile școlii (ORAR 2026-2027.xlsm, ORAR CLASE, CATEDRE). |
| `ilp.py` | Reorganizarea cu programare liniară în numere întregi (scipy/HiGHS): R2, R7, R13–R17, maximul pe zi, fără suprapuneri; `--inp`, `--zf 1` (zilele fixe), `--libere "X D,..."` (clase dezlegate), `--wr2`, `--timp`. |
| `optim.js` | Variantă euristică (căutare locală), mai slabă; păstrată pentru generatorul din aplicație. |
| `ev.py`, `chk.py`, `tr.py`, `comp.py`, `base.py` | Evaluare: ferestre și R2, R14/R15, mutările între locații (R16/R17), comparația pe profesori. |
| `build2.py`, `analiza.py`, `excel.py` | Planurile-cadru transcrise și verificarea practicii (`Verificare practica 2026-2027.xlsx`). |
| `tabel.py` | Tabelul de schimbări după reorganizare. |
| `inc_data.py` | Transcrierea încadrării scanate (varianta veche), pentru comparație. |
| `test14.py` | Test cu Playwright: verificări, aplicarea reorganizării, revenirea. |

Versiunea 2.1 (anul următor, fără Claude): taburile „Clase și planuri” (clasa cu disciplinele planului-cadru, ore/săpt. ↔ ore/an, copiere de la altă clasă sau din modelele anului trecut), „Profesori și încadrare” (fișa profesorului cu funcția și specialitățile; „Asociază o clasă” propune disciplinele din specialități cu orele rămase, se pot schimba de mână; % din normă), verificarea „Plan” (ore neîncadrate sau peste plan) și „Ani școlari” în „Date și setări” (anul următor: clasele trec IX→X→XI→XII, orarul și încadrarea pornesc goale; anii vechi rămân în `orar_an_<an>`; backup-ul JSON îi cuprinde pe toți în `_ani`).

Construire:
```
python3 -c "import json;s=open('dev/index.src.html').read();d=open('dev/data_initial.json').read();p=open('dev/propunere_v2.0.json').read();open('index.html','w').write(s.replace('/*__DATA__*/null',d.replace('</','<\\/')).replace('/*__PROPUNERE__*/null',p.replace('</','<\\/')))"
```
La fiecare publicare: crește versiunea din „Date și setări” și `CACHE_NAME` din `service-worker.js`.
