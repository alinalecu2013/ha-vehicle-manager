# Opel Astra H Caravan (break) – model 3D procedural

Generator Python (numpy + Pillow) pentru un model `.glb` al Opel Astra H Caravan (A04, 2004–2010),
la cotele oficiale, cu materiale PBR și texturi desenate procedural. Nu folosește modele sau texturi
străine, deci rezultatul se poate distribui liber, sub aceeași licență MIT ca proiectul.

## Cote folosite

| Cotă | Valoare | În model |
|---|---|---|
| Lungime | 4515 mm | 4,515 m |
| Lățime (fără oglinzi) | 1794 mm | 1,794 m (2,038 m cu oglinzi) |
| Înălțime (cu bare de plafon) | 1500 mm | 1,500 m |
| Ampatament | 2703 mm | 2,703 m |
| Ecartament față / spate | 1488 / 1488 mm | 1,488 m |
| Consolă față / spate | 871 / 941 mm | 0,871 / 0,941 m |
| Gardă la sol | 160 mm | 0,160 m |
| Anvelope | 205/55 R16 | Ø 632 mm, lățime 205 mm |
| Prindere jantă | 5 × 110 | 5 prezoane pe Ø 110 mm |

Surse: [auto-data.net](https://www.auto-data.net/en/opel-astra-h-caravan-generation-548),
[ADAC Autokatalog](https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/opel/astra/h/207185),
[automoli.com](https://www.automoli.com/au/vehicles/opel/astra/astra-h-caravan-548/),
[fișa tehnică Opel Astra H (PDF)](https://dixi-car.pl/doc/opel-astra3-kom-dane-tech.pdf).
Culoarea implicită este Star Silver III metalizat (cod Opel Z157 / 2AU),
[referință vopsea](https://shop.paintscratch.com/colors/saturn/star-silver-iii-metallic-1572auwa782j).

Profilele (capotă, parbriz, linia geamurilor, plafon, hayon) sunt estimate după fotografii și
desene de profil, calibrate pe cotele de mai sus.

## Materiale

- vopsea metalizată cu lac (`KHR_materials_clearcoat`);
- flancuri, față și spate cu texturi de culoare și hărți metal/rugozitate/lac: rosturi de uși,
  geamuri cu rame negre, faruri cu proiector, grila cu bară cromată și emblemă, numere RO,
  stopuri verticale, lunetă cu degivrare, bușonul de rezervor pe dreapta;
- anvelope cu textură și hartă de normale pentru profil (4 șanțuri, lamele, inscripția 205/55 R16);
- jante de aliaj 16" cu 5 spițe duble, disc de frână Ø 280 mm, etrier, prezoane, capac cu emblemă;
- parbriz, oglinzi, bare de plafon din aluminiu, ștergătoare, pasaje de roată, evacuare.

## Utilizare

```bash
python genereaza.py Opel_Astra_H_Caravan.glb --numar "B 06 OPL" --culoare 168,172,176
python genereaza.py Opel_Astra_H_Caravan_mobil.glb --mobil      # varianta pentru telefon
npx @gltf-transform/cli optimize Opel_Astra_H_Caravan.glb Opel_Astra_H_Caravan_opt.glb \
    --compress quantize --texture-compress false --palette false --simplify false
```

Nu folosi `--simplify`: produce pete pe flancuri și găuri la pasajele roților.

## Ce face cardul cu modelul

Materialele au metadate `extras.vm`, citite de cardul Vehicle Manager:

| Material | Metadate | Folosire în card |
|---|---|---|
| Vopsea | `paint: true` | primește culoarea vehiculului |
| Flancuri, Față, Spate | `paint_srgb`, `paint_mr` | pixelii de vopsea (recunoscuți după harta metal/rugozitate) sunt recolorați, păstrând umbrele |
| Față, Spate | `plate` (dreptunghi UV) | numărul de înmatriculare e redesenat cu textul din configurare |
| Față, Spate | `lamp` + `emissiveTexture` | masca lămpilor (R = faruri / stopuri, G = semnalizări) se aprinde în mers sau pentru avarii |

Deci `--numar` și `--culoare` contează doar pentru alte aplicații; în card, culoarea și
numărul vin din configurarea vehiculului.

`--mobil` folosește texturi WebP (`EXT_texture_webp`) la jumătate de rezoluție.

Axe glTF: X spre față, Y în sus, Z spre dreapta mașinii; solul la Y = 0, originea la mijlocul ampatamentului.
Roțile sunt noduri separate (`roata_fata_dreapta` etc.), deci se pot roti în aplicație.
