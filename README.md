# Vehicle Manager pentru Home Assistant

Integrare + card Lovelace pentru evidenta actelor si caracteristicilor auto, cu suport
pentru mai multe vehicule, poza per masina si un model 3D rotativ in card.

![Vehicle Manager Card](https://raw.githubusercontent.com/alinalecu2013/ha-vehicle-manager/main/images/card.png)

<p align="center">
  <img src="https://raw.githubusercontent.com/alinalecu2013/ha-vehicle-manager/main/images/phone.png" alt="Cardul pe telefon (tema Sunset)" width="300">
  &nbsp;
  <img src="https://raw.githubusercontent.com/alinalecu2013/ha-vehicle-manager/main/images/themes.png" alt="Meniul Themes" width="520">
</p>

<sub>Capturi cu date demonstrative.</sub>

## Ce urmareste

**Acte si scadente:** RCA, ITP, rovinieta, revizie, distributie, plus optional CASCO,
trusa medicala, extinctor, impozit auto si schimbul sezonier de anvelope.
Reviziile si distributia pot avea scadenta pe data, pe kilometraj, sau pe amandoua.

**Caracteristici:** marca, model, an fabricatie, kilometraj, culoare, capacitate motor,
combustibil folosit, numar de inmatriculare, plus VIN (opțional).

**Media:** o poza per masina si, opțional, un model 3D `.glb`/`.gltf`.

## Instalare

### Prin HACS (recomandat)

[![Deschide in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alinalecu2013&repository=ha-vehicle-manager&category=integration)

1. **HACS &rsaquo; &vellip; (dreapta sus) &rsaquo; Depozite personalizate** (Custom repositories).
2. Depozit: `https://github.com/alinalecu2013/ha-vehicle-manager`, tip: **Integration**, apoi **Adauga**.
3. Cauta **Vehicle Manager** in HACS si apasa **Descarca**.
4. Restarteaza Home Assistant.
5. **Setari &rsaquo; Dispozitive si servicii &rsaquo; Adauga integrare &rsaquo; Vehicle Manager**.
   Repeta pentru fiecare masina. Un vehicul = un config entry = un device.

Actualizarile apar in HACS (si in **Setari &rsaquo; Actualizari**); dupa fiecare actualizare
restarteaza Home Assistant.

### Manual

1. Copiaza folderul `custom_components/vehicle_manager` in `config/custom_components/`
   din Home Assistant.
2. Restarteaza Home Assistant si continua cu pasul 5 de mai sus.

### Cardul in HACS (optional)

Cardul are si un depozit HACS separat, in categoria **Dashboard**:
[alinalecu2013/vehicle-manager-card](https://github.com/alinalecu2013/vehicle-manager-card).
Daca il instalezi de acolo, il vezi si il actualizezi separat in HACS, iar integrarea
detecteaza instalarea (folderul `config/www/community/vehicle-manager-card/`) si nu mai
incarca propria copie. Fara el, integrarea incarca automat cardul inclus.

### Cardul se incarca singur

Integrarea inregistreaza automat cardul (`/vehicle_manager_files/vehicle-manager-card.js`),
cu versiunea in URL, deci **nu** trebuie adaugat in **Setari &rsaquo; Dashboards &rsaquo; Resurse**.
Daca ai adaugat anterior resursa manual, sterge-o. Daca dupa o actualizare cardul nu apare pe
telefon, in aplicatia Companion: **Setari &rsaquo; Companion app &rsaquo; Depanare &rsaquo;
Reset frontend cache**.

## Cardul

Adauga un card manual si foloseste:

```yaml
type: custom:vehicle-manager-card
```

Fara nicio alta setare, cardul descopera singur toate vehiculele configurate si le
listeaza in meniul drop-down din partea de sus.

### Opțiuni

| Opțiune | Implicit | Descriere |
| --- | --- | --- |
| `title` | numele vehiculului | Titlu fix in bara de sus. |
| `vehicles` | auto | Lista explicita de senzori `sensor.<vehicul>_stare_acte`. |
| `default_vehicle` | primul | Vehiculul selectat la incarcare. |
| `always_show_picker` | `false` | Arata drop-down-ul si cand exista un singur vehicul. |
| `auto_rotate` | `true` | Rotire automata a modelului 3D. |
| `rotate_speed` | `0.35` | Radiani pe secunda. |
| `show_photo_toggle` | `true` | Butonul `3D` / `Poza` din scena. |
| `show_theme_button` | `true` | Arata butonul **Themes** din bara de sus. |
| `show_costs_button` | `true` | Arata butonul **Costuri** din bara de sus. |
| `compact` | `false` | Mod compact pentru pagina principala (vezi mai jos). |
| `compact_items` | `3` | Cate acte se afiseaza in modul compact (1 - 5). |
| `navigation_path` | - | In modul compact, pagina deschisa la atingerea numelui (ex. `/lovelace/masini`). |
| `documents` | automat | Lista actelor afisate (vezi mai jos). |
| `specs` | toate | Lista caracteristicilor afisate: `make`, `model`, `year`, `mileage`, `color`, `engine_capacity`, `fuel_type`, `license_plate`. |
| `accent` | `#00e5ff` | Culoarea accent (ignorata dupa ce salvezi o tema din **Themes**). |
| `accent2` | `#ff2bd6` | Culoarea accent secundara (idem). |
| `three_src` | `https://esm.sh/three@0.160.0` | Sursa bibliotecii three.js. |
| `gltf_loader_src` | derivat din `three_src` | Sursa `GLTFLoader`. |

Exemplu complet:

```yaml
type: custom:vehicle-manager-card
default_vehicle: sensor.logan_stare_acte
accent: "#7cf5c0"
accent2: "#ffa63d"
rotate_speed: 0.25
```

### Ce acte si caracteristici apar

In editorul vizual al cardului bifezi ce acte si ce caracteristici vrei sa vezi. Fara
nicio bifa, cardul arata cele 5 acte de baza (RCA, ITP, rovinieta, revizie, distributie)
plus orice alt act care are o data completata, si toate caracteristicile. Bifele se aplica
si in modul compact.

```yaml
type: custom:vehicle-manager-card
documents: [rca, itp, rovinieta, casco, impozit]
specs: [make, model, mileage, license_plate]
```

Cheile actelor: `rca`, `itp`, `rovinieta`, `casco`, `revizie`, `distributie`,
`trusa_medicala`, `extinctor`, `impozit`, `anvelope`.

### Mod compact

Varianta mica a cardului, potrivita pentru pagina principala de pe telefon: numele si
starea masinii, scena 3D (sau poza) si actele cele mai urgente (intai cele expirate,
apoi cele care expira curand, apoi urmatoarele scadente). Panourile de caracteristici,
lista completa de acte si butoanele Themes / setari sunt ascunse; tema salvata se aplica
in continuare.

<p align="center"><img src="https://raw.githubusercontent.com/alinalecu2013/ha-vehicle-manager/main/images/compact.png" alt="Modul compact pe telefon" width="380"></p>

```yaml
type: custom:vehicle-manager-card
compact: true
compact_items: 3
navigation_path: /lovelace/masini   # optional: pagina cu cardul complet
```

Atingerea unui act deschide data lui, ca in cardul complet. Cu `navigation_path`,
atingerea numelui masinii (sau a sagetii) deschide pagina indicata.

### Costuri

Butonul **Costuri** din bara de sus deschide istoricul cheltuielilor vehiculului selectat:

![Panoul Costuri](https://raw.githubusercontent.com/alinalecu2013/ha-vehicle-manager/main/images/costs.png)

- totalul pe anul ales, totalul general si numarul de cheltuieli;
- un grafic pe categorii (RCA, ITP, rovinieta, revizie, distributie, reparatii, anvelope,
  combustibil, spalare, parcare, amenzi, taxe si impozit, accesorii, altele);
- formular de adaugare: data (implicit azi), categoria, suma, kilometrajul (implicit cel
  curent) si o nota;
- lista cheltuielilor, filtrabila pe ani, cu stergere (al doilea click confirma).

Cheltuielile se salveaza pe server (`.storage/vehicle_manager.expenses`), sunt aceleasi pe
toate dispozitivele si se actualizeaza live. Moneda este cea setata in
**Setari &rsaquo; Sistem &rsaquo; General**. La stergerea unui vehicul se sterge si
istoricul lui de cheltuieli.

### Jurnal de alimentari

Alimentarile se adauga tot din panoul **Costuri**, la categoria **Combustibil**: apar doua
campuri in plus, **Cantitate** (litri, sau kWh la masinile electrice) si **Plin complet**.

Consumul se calculeaza prin metoda *plin la plin*: cantitatea alimentata intre doua
plinuri complete (inclusiv alimentarile partiale dintre ele) impartita la kilometrii
parcursi. De aceea:

- completeaza **kilometrajul** la fiecare alimentare (fara el, alimentarea nu intra in calcul);
- primul plin complet doar fixeaza punctul de pornire; consumul apare de la al doilea.

In panou apar consumul mediu, costul combustibilului pe km si kilometrii masurati, iar la
fiecare plin consumul calculat pentru intervalul respectiv. Senzorul **Consum mediu**
poate fi folosit in grafice si automatizari.

Daca o cheltuiala (de orice categorie) are un kilometraj mai mare decat cel al
vehiculului, kilometrajul vehiculului se actualizeaza automat.

### Themes

Butonul **Themes** din bara de sus deschide meniul de personalizare direct din dashboard:

- **Presetari:** Neon, Ocean, Sunset, Forest, Carbon, Light si Home Assistant
  (preia culorile temei HA active).
- **Culori:** accent principal/secundar, fundal, panouri, text, text secundar, linii,
  plus culorile pentru starile valabil / expira curand / expirat.
- **Text:** familia de font si dimensiunea (75% - 160%).
- **Aspect:** spatiere, rotunjirea colturilor, opacitatea si estomparea panourilor,
  intensitatea stralucirii, grila de fundal.
- **Scena 3D:** inaltimea scenei (culorile scenei urmeaza tema).
- **Imagine de fundal:** incarca o poza direct din card (de pe telefon sau PC) sau
  foloseste un URL (`/local/fundal.jpg`, `https://...`). Se poate afisa pe tot cardul
  sau doar in scena 3D, cu incadrare (umple / potriveste / mozaic), pozitie, acoperire
  cu culoarea de fundal (pentru lizibilitate) si estompare. Pozele mai mari de 1920 px
  sunt micsorate in browser inainte de upload. Fisierele ajung in
  `config/www/vehicle_manager/theme-bg-*`; cele nefolosite se sterg la salvarea temei.

Modificarile se vad imediat. **Salveaza** pastreaza tema pe server (in
`.storage/vehicle_manager.theme`), deci e aceeasi pe toate dispozitivele si se aplica
live in toate dashboard-urile deschise. **Renunta** revine la tema salvata, iar
**Implicit** incarca tema originala (trebuie apoi salvata).

### Interactiune

- **Drop-down sus:** schimba vehiculul (selectia e retinuta in browser).
- **Trage cu mouse-ul/degetul** peste scena: rotire manuala, cu inertie.
- **Click pe un act:** deschide entitatea `date` corespunzatoare, deci poti schimba data pe loc.
- **Click pe kilometraj:** deschide entitatea `number`, deci poti actualiza km-ul pe loc.
- **Rotita din dreapta sus:** deschide pagina integrarii pentru editare completa.

### Modelul 3D

Fara model incarcat, cardul deseneaza procedural o masina stilizata, vopsita in culoarea
configurata a vehiculului (`Rosu`, `Albastru metalizat`, `#1f5fbf`... sunt toate acceptate).
Daca incarci un `.glb` sau `.gltf` in pasul **Poza si model 3D**, acela e randat in locul ei,
scalat automat.

**Modele mari.** Pe telefon, un model peste ~5 MB se incarca greu. Un model exportat din
SketchUp/SimLab se poate micsora fara diferente vizibile cu
[glTF-Transform](https://gltf-transform.dev) (necesita Node.js):

```bash
npx @gltf-transform/cli optimize masina.glb masina_optimizat.glb   --compress quantize --texture-compress false   --simplify-ratio 0.35 --simplify-error 0.001
```

`quantize` e citit direct de three.js (fara decodoare suplimentare); nu folosi `draco` sau
`meshopt`, cardul nu le incarca. Exemplu: un Citroen C3 a scazut de la 20 MB la 4 MB.

three.js se incarca de pe CDN la prima afisare. Pentru instalari fara internet, pune
`three.module.js` in `config/www/` si seteaza:

```yaml
three_src: /local/three.module.js
gltf_loader_src: /local/GLTFLoader.js
```

Daca three.js nu poate fi incarcat si vehiculul are poza, cardul comuta automat pe poza.

## Entitati create per vehicul

| Platforma | Entitate | Rol |
| --- | --- | --- |
| `sensor` | Stare acte | Starea cea mai grava; toate datele pentru card in atribute. |
| `sensor` | RCA, ITP, Rovinieta, CASCO, Revizie, Distributie, Trusa medicala, Extinctor, Impozit auto, Schimb anvelope | Zile ramase (negativ = expirat); atributul `document_key` e cheia actului pentru servicii. |
| `sensor` | Marca, Model, An, Culoare, Capacitate, Combustibil, Nr. inmatriculare, VIN | Caracteristici (diagnostic). |
| `number` | Kilometraj, Revizie la km, Distributie la km | Editabile din interfata. |
| `date` | Expirare RCA / ITP / rovinieta, Scadenta revizie / distributie | Editabile din interfata. |
| `binary_sensor` | Acte de rezolvat, Acte expirate | Pentru automatizari si notificari. |
| `image` | Poza | Poza vehiculului. |
| `calendar` | Scadente | Un eveniment pe toata ziua pentru fiecare act cu data de scadenta. |
| `sensor` | Cheltuieli anul curent | Suma cheltuielilor din anul curent (in moneda setata in HA), cu defalcare pe categorii in atribute. |
| `sensor` | Cheltuieli totale | Suma tuturor cheltuielilor inregistrate. |
| `sensor` | Consum mediu | L/100 km (kWh/100 km la electrice), din alimentari; in atribute: ultimul plin, costul pe km, km masurati. |

Actele optionale (CASCO, trusa medicala, extinctor, impozit auto, schimb anvelope) se
completeaza din **Configurare &rsaquo; Acte si scadente**. Cat timp nu au o data, nu
influenteaza starea vehiculului si nu apar in calendar sau in notificari. Schimbul de
anvelope e un memento sezonier: butonul din notificare il muta cu 6 luni. Costul unei
reinnoiri (campul `cost`) ajunge la categoria potrivita: CASCO, Accesorii (trusa,
extinctor), Taxe (impozit) sau Anvelope.

Pragurile de avertizare (implicit 30 de zile si 1000 km) se configureaza per vehicul din
**Configurare &rsaquo; Praguri de avertizare**.

## Kilometraj automat

Kilometrajul se poate prelua automat dintr-un senzor existent in Home Assistant: adaptor
OBD (ex. Torque, WiCAN), aplicatia producatorului masinii, Android Auto etc.

1. **Setari &rsaquo; Dispozitive si servicii &rsaquo; Vehicle Manager &rsaquo; Configurare**
   la vehiculul dorit.
2. Alege **Kilometraj automat** si selecteaza senzorul care raporteaza odometrul.

- Se aplica doar cresterile: o citire gresita (0, `unavailable`, senzor resetat) nu poate
  scadea kilometrajul.
- Valorile in mile (`mi`) sau metri (`m`) se convertesc in km; fara unitate se presupun km.
- In mers, kilometrajul se salveaza cel mult o data la 5 minute (ultima valoare nu se
  pierde), ca sa nu se scrie inutil pe disc.
- Kilometrajul se poate modifica in continuare si manual. In card apare eticheta **AUTO**
  langa kilometraj cand acesta vine dintr-un senzor.
- Pentru a reveni la kilometrajul manual, goleste campul.

## Calendar

Fiecare vehicul are o entitate `calendar.<vehicul>_scadente` cu toate actele care au o
data de scadenta (RCA, ITP, rovinieta si revizia/distributia, daca au data). Apare in
pagina **Calendar** din Home Assistant si poate fi adaugata intr-un card Calendar.
Actele urmarite doar pe kilometraj nu au o zi anume, deci nu apar in calendar.

## Notificari pe telefon

Blueprint-ul **Vehicle Manager: notificari pentru acte** trimite o notificare in
aplicatia Home Assistant Companion cand un act se apropie de scadenta:

[![Importa blueprint-ul](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/alinalecu2013/ha-vehicle-manager/blob/main/blueprints/automation/vehicle_manager/notificare_acte.yaml)

1. Apasa butonul de mai sus (sau **Setari &rsaquo; Automatizari &rsaquo; Blueprints &rsaquo;
   Importa blueprint** si lipeste adresa `https://github.com/alinalecu2013/ha-vehicle-manager/blob/main/blueprints/automation/vehicle_manager/notificare_acte.yaml`).
2. **Creeaza automatizare** din blueprint: alege vehiculele, telefonul, ora si cu cate
   zile inainte vrei notificarile (implicit 30, 7, 1 zi si in ziua scadentei).

Notificarea are un buton:

- **Am reinnoit (+12 luni)** pentru RCA, ITP si rovinieta: prelungeste actul
  (`renew_document`) cu numarul de luni ales in blueprint.
- **Am facut-o** pentru revizie si distributie: inregistreaza lucrarea la kilometrajul
  curent (`mark_service_done`) si calculeaza urmatoarea scadenta din intervalele setate
  in blueprint (implicit 15.000 km / 12 luni pentru revizie si 90.000 km / 60 de luni
  pentru distributie; verifica valorile in cartea service-ului masinii).

Dupa apasare, notificarea dispare de pe telefon. Optional, actele expirate sunt
reamintite zilnic. Pentru mai multe telefoane, creeaza cate o automatizare; fiecare
trateaza doar butoanele propriilor notificari.

## Servicii

- `vehicle_manager.set_mileage` — actualizeaza kilometrajul.
- `vehicle_manager.set_document` — seteaza data si/sau km-ul scadent pentru un act.
- `vehicle_manager.renew_document` — prelungeste un act cu N luni (de la scadenta
  actuala daca e in viitor, altfel de la azi).
- `vehicle_manager.mark_service_done` — inregistreaza o revizie sau o distributie si
  calculeaza automat urmatoarea scadenta.
- `vehicle_manager.add_expense` — adauga o cheltuiala (categorie, suma, data, km, nota;
  pentru combustibil si `quantity` / `full_tank`).
- `vehicle_manager.delete_expense` — sterge o cheltuiala dupa id.

`renew_document` si `mark_service_done` accepta si campul optional `cost`: suma platita
se inregistreaza automat in istoric, la categoria actului. Exemplu:

```yaml
action: vehicle_manager.renew_document
target:
  entity_id: sensor.astra_stare_acte
data:
  document: rca
  months: 12
  cost: 1240
```

Exemplu de automatizare:

```yaml
automation:
  - alias: Avertizare acte auto
    triggers:
      - trigger: state
        entity_id: binary_sensor.logan_acte_de_rezolvat
        to: "on"
    actions:
      - action: notify.persistent_notification
        data:
          title: Acte auto
          message: >
            {{ state_attr('binary_sensor.logan_acte_de_rezolvat', 'acte') | join(', ') }}
```

## Detalii de implementare

- Sursa cardului este `custom_components/vehicle_manager/www/vehicle-manager-card.js`.
  La o versiune noua: actualizeaza versiunea in `const.py`, `manifest.json` si
  `CARD_VERSION` din card, publica release-ul integrarii, apoi ruleaza
  `scripts/publica-card.sh`, care copiaza cardul in depozitul HACS al cardului si face
  release-ul cu aceeasi versiune.

- Sursa de adevar pentru fiecare vehicul este `entry.options`. Modificarile din entitati,
  din servicii sau din fluxul de opțiuni se salveaza acolo si recalculeaza starea fara reload
  (singura excepție: redenumirea vehiculului, care reincarca entry-ul ca sa se actualizeze
  numele device-ului).
- Starea derivata (zile ramase) se recalculeaza si periodic, la 15 minute.
- Fisierele incarcate ajung in `config/www/vehicle_manager/` si se sterg la eliminarea
  vehiculului.
- Inelul de progres din card e proportional cu un orizont presupus: 365 de zile pentru RCA,
  rovinieta si revizie, 730 pentru ITP, 1825 pentru distributie — integrarea nu cunoaste data
  de emitere, doar scadenta. Pentru scadentele pe km, orizontul este 15 000 km la revizie
  si 120 000 km la distributie.
