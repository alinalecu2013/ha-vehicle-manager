# Vehicle Manager pentru Home Assistant

Integrare + card Lovelace pentru evidenta actelor si caracteristicilor auto, cu suport
pentru mai multe vehicule, poza per masina si un model 3D rotativ in card.

## Ce urmareste

**Acte si scadente:** RCA, ITP, rovinieta, revizie, distributie.
Reviziile si distributia pot avea scadenta pe data, pe kilometraj, sau pe amandoua.

**Caracteristici:** marca, model, an fabricatie, kilometraj, culoare, capacitate motor,
combustibil folosit, numar de inmatriculare, plus VIN (opțional).

**Media:** o poza per masina si, opțional, un model 3D `.glb`/`.gltf`.

## Instalare

1. Copiaza folderul `custom_components/vehicle_manager` in `config/custom_components/`
   din Home Assistant.
2. Restarteaza Home Assistant.
3. **Setari &rsaquo; Dispozitive si servicii &rsaquo; Adauga integrare &rsaquo; Vehicle Manager**.
4. Repeta pasul 3 pentru fiecare masina. Un vehicul = un config entry = un device.

Cardul se inregistreaza automat ca resursa frontend (`/vehicle_manager_files/vehicle-manager-card.js`) —
nu trebuie adaugat manual in **Setari &rsaquo; Dashboards &rsaquo; Resurse**. Daca totusi nu apare,
goleste cache-ul browserului; in log vei vedea un avertisment daca inregistrarea automata a eșuat.

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
| `sensor` | RCA, ITP, Rovinieta, Revizie, Distributie | Zile ramase (negativ = expirat). |
| `sensor` | Marca, Model, An, Culoare, Capacitate, Combustibil, Nr. inmatriculare, VIN | Caracteristici (diagnostic). |
| `number` | Kilometraj, Revizie la km, Distributie la km | Editabile din interfata. |
| `date` | Expirare RCA / ITP / rovinieta, Scadenta revizie / distributie | Editabile din interfata. |
| `binary_sensor` | Acte de rezolvat, Acte expirate | Pentru automatizari si notificari. |
| `image` | Poza | Poza vehiculului. |

Pragurile de avertizare (implicit 30 de zile si 1000 km) se configureaza per vehicul din
**Configurare &rsaquo; Praguri de avertizare**.

## Servicii

- `vehicle_manager.set_mileage` — actualizeaza kilometrajul.
- `vehicle_manager.set_document` — seteaza data si/sau km-ul scadent pentru un act.
- `vehicle_manager.renew_document` — prelungeste un act cu N luni (de la scadenta
  actuala daca e in viitor, altfel de la azi).
- `vehicle_manager.mark_service_done` — inregistreaza o revizie sau o distributie si
  calculeaza automat urmatoarea scadenta.

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
