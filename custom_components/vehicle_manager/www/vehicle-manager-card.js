/*
 * Vehicle Manager Card
 * Card Lovelace pentru integrarea `vehicle_manager`.
 *
 * Layout: selector de vehicul sus, caracteristici in stanga,
 * model 3D rotativ in centru, acte in dreapta.
 */

const CARD_VERSION = "2.0.0";
const DEFAULT_THREE = "https://esm.sh/three@0.160.0";

/* ------------------------------------------------------------------ */
/* Limba: romana cand Home Assistant e in romana, altfel engleza        */
/* ------------------------------------------------------------------ */

const detectLang = (code) => (String(code || "").toLowerCase().startsWith("ro") ? "ro" : "en");
let LANG = detectLang(document.documentElement.lang || navigator.language);

function setLanguage(hass) {
  LANG = detectLang(hass?.locale?.language || hass?.language || LANG);
}

/* Textele raman in romana in cod; EN are traducerile. {nume} se inlocuieste din vars. */
function t(text, vars) {
  let out = LANG === "ro" ? text : EN[text] ?? text;
  if (vars) for (const [key, value] of Object.entries(vars)) out = out.split(`{${key}}`).join(String(value));
  return out;
}

const EN = {
  "Valabil": "Valid",
  "Expira curand": "Expiring soon",
  "Expirat": "Expired",
  "Necompletat": "Not set",
  "RCA": "Insurance (RCA)",
  "ITP": "Inspection (ITP)",
  "Rovinieta": "Road tax",
  "CASCO": "CASCO",
  "Revizie": "Service",
  "Distributie": "Timing belt",
  "Trusa medicala": "First aid kit",
  "Extinctor": "Fire extinguisher",
  "Impozit auto": "Vehicle tax",
  "Schimb anvelope": "Tyre change",
  "Marca": "Make",
  "Model": "Model",
  "An fabricatie": "Year",
  "Kilometraj": "Mileage",
  "Culoare": "Color",
  "Capacitate motor": "Engine",
  "Combustibil": "Fuel",
  "Nr. inmatriculare": "License plate",
  "Parcare": "Parking",
  "Benzina": "Petrol",
  "Diesel": "Diesel",
  "GPL": "LPG",
  "Benzina + GPL": "Petrol + LPG",
  "Hibrid": "Hybrid",
  "Hibrid plug-in": "Plug-in hybrid",
  "Electric": "Electric",
  "Altul": "Other",
  "azi": "today",
  "maine": "tomorrow",
  "{n} zile": "{n} days",
  "expirat de {n} z": "expired {n} d ago",
  "depasit {km} km": "{km} km overdue",
  "chiar acum": "just now",
  "acum {n} min": "{n} min ago",
  "acum {n} h": "{n} h ago",
  "ieri": "yesterday",
  "acum {n} zile": "{n} days ago",
  "expirat acum {n} zile": "expired {n} days ago",
  "{n} zile ramase": "{n} days left",
  "depasit cu {km} km": "{km} km overdue",
  "{km} km ramasi": "{km} km left",
  "fara scadenta setata": "no due date set",
  "in mers": "driving",
  "parcata": "parked",
  "Reparatii": "Repairs",
  "Anvelope": "Tyres",
  "Spalare": "Car wash",
  "Amenzi": "Fines",
  "Taxe si impozit": "Taxes",
  "Accesorii": "Accessories",
  "Altele": "Other",
  "Alte documente (talon, cartea masinii...)": "Other documents (registration, vehicle book...)",
  "Culori": "Colors",
  "Foloseste culorile temei Home Assistant": "Use the Home Assistant theme colors",
  "Accent principal": "Primary accent",
  "Accent secundar": "Secondary accent",
  "Fundal": "Background",
  "Panouri": "Panels",
  "Text secundar": "Secondary text",
  "Linii si contururi": "Lines and borders",
  "Stare: valabil": "Status: valid",
  "Stare: expira curand": "Status: expiring soon",
  "Stare: expirat": "Status: expired",
  "Futurist (implicit)": "Futuristic (default)",
  "Fontul Home Assistant": "Home Assistant font",
  "Fontul sistemului": "System font",
  "Rotunjit": "Rounded",
  "Dimensiune font": "Font size",
  "Aspect": "Layout",
  "Spatiere": "Spacing",
  "Rotunjire colturi": "Corner radius",
  "Opacitate panouri": "Panel opacity",
  "Estompare panouri": "Panel blur",
  "Intensitate stralucire": "Glow intensity",
  "Grila de fundal": "Background grid",
  "Scena 3D": "3D scene",
  "Inaltime scena": "Scene height",
  "Imagine de fundal": "Background image",
  "Imagine": "Image",
  "Unde se afiseaza": "Shown on",
  "Tot cardul": "Whole card",
  "Doar scena 3D": "3D scene only",
  "Incadrare": "Fit",
  "Umple": "Cover",
  "Potriveste": "Contain",
  "Mozaic": "Tile",
  "Pozitie": "Position",
  "Centru": "Center",
  "Sus": "Top",
  "Jos": "Bottom",
  "Acoperire cu culoarea de fundal": "Background color overlay",
  "Estompare imagine": "Image blur",
  "Modificarile se vad imediat; apasa Salveaza ca sa le pastrezi pe toate dispozitivele.": "Changes apply instantly; press Save to keep them on all devices.",
  "Implicit": "Default",
  "Renunta": "Cancel",
  "Salveaza": "Save",
  "Se salveaza...": "Saving...",
  "Tema nu a putut fi salvata: {err}": "The theme could not be saved: {err}",
  "Serverul ruleaza o versiune veche a integrarii (fara Themes). Copiaza tot folderul custom_components/vehicle_manager, inclusiv theme.py, si restarteaza Home Assistant.": "The server runs an old version of the integration (without Themes). Update the integration and restart Home Assistant.",
  "fara imagine": "no image",
  "Incarca imagine": "Upload image",
  "Elimina": "Remove",
  "sau un URL: /local/fundal.jpg, https://...": "or a URL: /local/background.jpg, https://...",
  "URL invalid: trebuie sa inceapa cu / sau https:// si sa nu contina spatii, ghilimele sau paranteze.": "Invalid URL: it must start with / or https:// and contain no spaces, quotes or parentheses.",
  "Se pregateste imaginea...": "Preparing the image...",
  "Se incarca imaginea...": "Uploading the image...",
  "serverul ruleaza o versiune veche a integrarii; copiaza theme.py nou si restarteaza Home Assistant": "the server runs an old version of the integration; update it and restart Home Assistant",
  "Imagine incarcata. Apasa Salveaza ca sa o pastrezi.": "Image uploaded. Press Save to keep it.",
  "Imaginea nu a putut fi incarcata: {err}": "The image could not be uploaded: {err}",
  "Selecteaza vehiculul": "Select vehicle",
  "Costuri": "Costs",
  "Dosar": "Folder",
  "Dosarul masinii: polite, talon...": "Vehicle folder: policies, registration...",
  "Editeaza vehiculele": "Edit vehicles",
  "Deschide pagina vehiculului": "Open the vehicle page",
  "Caracteristici": "Specifications",
  "Poza": "Photo",
  "Acte si scadente": "Documents and due dates",
  "Modelul 3D nu a putut fi incarcat (biblioteca three.js nu este accesibila). Adauga o poza vehiculului sau seteaza three_src catre o copie locala.": "The 3D model could not be loaded (three.js is not reachable). Add a photo of the vehicle or point three_src to a local copy.",
  "Vehicul": "Vehicle",
  "model 3d · trage pentru rotire": "3d model · drag to rotate",
  "randare procedurala · trage pentru rotire": "procedural render · drag to rotate",
  "Necesita atentie: {list}": "Needs attention: {list}",
  "Toate actele sunt in regula": "All documents are in order",
  "prag {days}z / {km}km": "threshold {days}d / {km}km",
  "Nicio scadenta completata": "No due dates set",
  "Ultimul loc de parcare": "Last parking spot",
  "Navigheaza pana la masina": "Navigate to the car",
  "Preluat automat din senzor": "Read automatically from a sensor",
  "{n} fisier(e) in dosar": "{n} file(s) in the folder",
  "Dosarul nu poate fi incarcat (actualizeaza integrarea si restarteaza Home Assistant).": "The folder cannot be loaded (update the integration and restart Home Assistant).",
  "Se incarca...": "Loading...",
  "Poze sau PDF-uri cu actele masinii. Se deschid doar din Home Assistant.": "Photos or PDFs of the vehicle documents. They open only from Home Assistant.",
  "niciun fisier": "no files",
  "Adauga": "Add",
  "Sterge": "Delete",
  "sterge?": "delete?",
  "Fisierul nu a putut fi sters: {err}": "The file could not be deleted: {err}",
  "Fisierul nu a putut fi deschis: {err}": "The file could not be opened: {err}",
  "serverul ruleaza o versiune veche a integrarii": "the server runs an old version of the integration",
  "Incarcat: {name}.": "Uploaded: {name}.",
  "Fisierul nu a putut fi incarcat: {err}": "The file could not be uploaded: {err}",
  "Serverul ruleaza o versiune veche a integrarii (fara Costuri). Actualizeaza integrarea si restarteaza Home Assistant.": "The server runs an old version of the integration (without Costs). Update the integration and restart Home Assistant.",
  "Costurile nu pot fi incarcate: {err}": "Costs cannot be loaded: {err}",
  "Perioada": "Period",
  "Descarca perioada aleasa ca fisier CSV (Excel)": "Download the selected period as a CSV file (Excel)",
  "Export CSV": "Export CSV",
  "Data": "Date",
  "Categorie": "Category",
  "Suma": "Amount",
  "Nota": "Note",
  "optional": "optional",
  "Cantitate (kWh)": "Quantity (kWh)",
  "Cantitate (l)": "Quantity (l)",
  "Cantitate": "Quantity",
  "Plin complet": "Full tank",
  "Introdu o suma mai mare decat zero.": "Enter an amount greater than zero.",
  "Adaugat: {what}, {amount}.": "Added: {what}, {amount}.",
  "Fara kilometraj, alimentarea nu intra in calculul consumului.": "Without mileage, the fill-up is not used for consumption.",
  "Cheltuiala nu a putut fi salvata: {err}": "The expense could not be saved: {err}",
  "Exportul nu a reusit: {err}": "Export failed: {err}",
  "Sigur?": "Sure?",
  "Cheltuiala nu a putut fi stearsa: {err}": "The expense could not be deleted: {err}",
  "Anul {year}": "Year {year}",
  "Toti anii": "All years",
  "Total": "Total",
  "Medie pe an": "Yearly average",
  "Cheltuieli": "Expenses",
  "Total general": "Grand total",
  "Cheltuieli in an": "Expenses this year",
  "Consum mediu": "Average consumption",
  "Combustibil pe km": "Fuel per km",
  "Km masurati": "Measured km",
  "Nicio cheltuiala in perioada aleasa. Adaug-o din formularul de mai sus.": "No expenses in the selected period. Add one with the form above.",
  "(partial)": "(partial)",
  "Sterge (id {id})": "Delete (id {id})",
  "Inca nu ai inregistrat cheltuieli pentru acest vehicul.": "No expenses recorded for this vehicle yet.",
  "Titlu (gol = numele vehiculului)": "Title (empty = vehicle name)",
  "Vehicul implicit": "Default vehicle",
  "Rotire automata": "Auto-rotate",
  "Buton comutare poza": "Photo toggle button",
  "Viteza de rotire": "Rotation speed",
  "Buton Themes (culorile se aleg din card)": "Themes button (colors are chosen in the card)",
  "Buton Costuri (istoricul cheltuielilor)": "Costs button (expense history)",
  "Buton Dosar (poze si PDF-uri cu actele)": "Folder button (photos and PDFs of documents)",
  "Mod compact (pentru pagina principala)": "Compact mode (for the home page)",
  "Acte afisate in modul compact": "Documents shown in compact mode",
  "Pagina deschisa din modul compact (ex. /lovelace/masini)": "Page opened from compact mode (e.g. /lovelace/cars)",
  "Acte afisate (nimic bifat: cele 5 de baza + actele completate)": "Documents shown (none checked: the 5 basic ones + any filled in)",
  "Caracteristici afisate (nimic bifat: toate)": "Specifications shown (none checked: all)",
  "Sursa three.js": "three.js source",
  "Garaj": "Garage",
  "Titlu": "Title",
  "Acte": "Documents",
  "necompletate": "not set",
  "Consum": "Consumption",
  "Costuri {year}": "Costs {year}",
  "{label} (+{n} acte)": "{label} (+{n} more)",
  "Niciun vehicul. Adauga unul din Setari › Dispozitive si servicii › Vehicle Manager.": "No vehicles. Add one in Settings › Devices & services › Vehicle Manager.",
  "Pagina deschisa la atingerea unui vehicul (gol = detaliile vehiculului)": "Page opened when tapping a vehicle (empty = vehicle details)",
  "Niciun vehicul gasit. Adauga unul din <code>Setari &rsaquo; Dispozitive si servicii &rsaquo; Adauga integrare &rsaquo; Vehicle Manager</code>.": "No vehicle found. Add one in <code>Settings &rsaquo; Devices &amp; services &rsaquo; Add integration &rsaquo; Vehicle Manager</code>."
};

console.info(
  `%c VEHICLE-MANAGER-CARD %c ${CARD_VERSION} `,
  "background:#00e5ff;color:#001018;font-weight:700;border-radius:3px 0 0 3px",
  "background:#131821;color:#9fb0c0;border-radius:0 3px 3px 0"
);

/* Orizont pentru inelul de progres cand documentul este exprimat in km. */
const KM_HORIZON = { revizie: 15000, distributie: 120000 };

/* Ordinea in modul compact: intai ce e expirat, apoi ce expira curand. */
const STATUS_RANK = { expired: 0, warning: 1, ok: 2, unknown: 3 };

const STATUS_LABEL = {
  ok: "Valabil",
  warning: "Expira curand",
  expired: "Expirat",
  unknown: "Necompletat",
};

/* Actele afisate implicit; celelalte apar doar dupa ce sunt completate. */
const CLASSIC_DOCUMENTS = ["rca", "itp", "rovinieta", "revizie", "distributie"];

/* Pentru editor: aceleasi chei ca DOCUMENTS din const.py. */
const DOCUMENT_OPTIONS = [
  ["rca", "RCA"],
  ["itp", "ITP"],
  ["rovinieta", "Rovinieta"],
  ["casco", "CASCO"],
  ["revizie", "Revizie"],
  ["distributie", "Distributie"],
  ["trusa_medicala", "Trusa medicala"],
  ["extinctor", "Extinctor"],
  ["impozit", "Impozit auto"],
  ["anvelope", "Schimb anvelope"],
];

const SPEC_ROWS = [
  { key: "make", label: "Marca", icon: "mdi:car-side" },
  { key: "model", label: "Model", icon: "mdi:car-info" },
  { key: "year", label: "An fabricatie", icon: "mdi:calendar-blank" },
  { key: "mileage", label: "Kilometraj", icon: "mdi:counter", unit: "km", entity: "mileage", auto: "mileage_auto" },
  { key: "color", label: "Culoare", icon: "mdi:palette", swatch: true },
  { key: "engine_capacity", label: "Capacitate motor", icon: "mdi:engine", unit: "cm³" },
  { key: "fuel_type", label: "Combustibil", icon: "mdi:gas-station", useLabel: "fuel_label" },
  { key: "license_plate", label: "Nr. inmatriculare", icon: "mdi:card-text-outline" },
  { key: "parking", label: "Parcare", icon: "mdi:car-brake-parking" },
];

/* "12 zile", "expirat de 3 z", "depasit 1.400 km" */
function shortRemaining(document_) {
  const { days, km_remaining: km } = document_;
  if (days !== null && days !== undefined) {
    if (days < 0) return t("expirat de {n} z", { n: Math.abs(days) });
    if (days === 0) return t("azi");
    if (days === 1) return t("maine");
    return t("{n} zile", { n: days });
  }
  if (km !== null && km !== undefined) {
    return km < 0 ? t("depasit {km} km", { km: formatNumber(Math.abs(km)) }) : `${formatNumber(km)} km`;
  }
  return "—";
}

/* "acum 5 min", "acum 3 h", "acum 2 zile" */
function timeAgo(iso) {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const minutes = Math.max(0, Math.round((Date.now() - then) / 60000));
  if (minutes < 1) return t("chiar acum");
  if (minutes < 60) return t("acum {n} min", { n: minutes });
  const hours = Math.round(minutes / 60);
  if (hours < 24) return t("acum {n} h", { n: hours });
  const days = Math.round(hours / 24);
  return days === 1 ? t("ieri") : t("acum {n} zile", { n: days });
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  if (Number.isNaN(number)) return String(value);
  return number.toLocaleString(LANG === "ro" ? "ro-RO" : "en-GB");
}

function formatDate(iso, language) {
  if (!iso) return null;
  const parsed = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return iso;
  return parsed.toLocaleDateString(language || "ro-RO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function fireEvent(node, type, detail) {
  const event = new Event(type, { bubbles: true, cancelable: false, composed: true });
  event.detail = detail || {};
  node.dispatchEvent(event);
  return event;
}

function moreInfo(node, entityId) {
  if (!entityId) return;
  fireEvent(node, "hass-more-info", { entityId });
}

function navigate(path) {
  history.pushState(null, "", path);
  window.dispatchEvent(new CustomEvent("location-changed"));
}

/* ------------------------------------------------------------------ */
/* Viewer 3D                                                           */
/* ------------------------------------------------------------------ */

class CarViewer {
  constructor(canvas, options) {
    this.canvas = canvas;
    this.options = options;
    this.disposed = false;
    this.failed = false;

    this.yaw = -0.6;
    this.pitch = 0.2;
    this.spin = 0;
    this.dragging = false;
    this.lastPointer = null;
    this.lastFrame = 0;

    this._pendingVehicle = null;
    this._currentKey = null;
  }

  /* --------------------------------------------------------------- */
  async init() {
    try {
      this.THREE = await import(/* webpackIgnore: true */ this.options.threeSrc);
    } catch (err) {
      console.error("vehicle-manager-card: nu am putut incarca three.js", err);
      this.failed = true;
      throw err;
    }
    if (this.disposed) return;

    const THREE = this.THREE;

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    if ("outputColorSpace" in this.renderer) {
      this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    }
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.Fog(this.options.bg || "#05070c", 7, 17);

    this.camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
    this.radius = 8.2;

    this._buildEnvironment();
    this._buildLights();
    this._buildStage();

    this.carGroup = new THREE.Group();
    this.scene.add(this.carGroup);

    this._attachPointerHandlers();
    this._observeResize();

    this.ready = true;
    if (this._pendingVehicle) {
      const pending = this._pendingVehicle;
      this._pendingVehicle = null;
      await this.setVehicle(pending);
    }
    this._loop(performance.now());
  }

  /* --------------------------------------------------------------- */
  _buildEnvironment() {
    const THREE = this.THREE;
    const size = 64;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    const gradient = ctx.createLinearGradient(0, 0, 0, size);
    gradient.addColorStop(0, "#1a2535");
    gradient.addColorStop(0.45, "#0b1018");
    gradient.addColorStop(0.5, this.options.accent);
    gradient.addColorStop(0.56, "#0b1018");
    gradient.addColorStop(1, "#05070b");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);

    const texture = new THREE.CanvasTexture(canvas);
    texture.mapping = THREE.EquirectangularReflectionMapping;
    if ("colorSpace" in texture) texture.colorSpace = THREE.SRGBColorSpace;

    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.envMap?.dispose?.();
    this.envMap = pmrem.fromEquirectangular(texture).texture;
    this.scene.environment = this.envMap;
    pmrem.dispose();
    texture.dispose();
  }

  _buildLights() {
    const THREE = this.THREE;
    this.scene.add(new THREE.HemisphereLight(0x9fc4ff, 0x0a0d12, 0.55));

    const key = new THREE.DirectionalLight(0xffffff, 2.1);
    key.position.set(4, 7, 5);
    this.scene.add(key);

    const left = new THREE.PointLight(this.options.accent, 55, 18);
    left.position.set(-5, 2.1, 3.4);
    this.scene.add(left);

    const right = new THREE.PointLight(this.options.accent2, 45, 18);
    right.position.set(5.2, 1.7, -3.2);
    this.scene.add(right);

    const under = new THREE.PointLight(this.options.accent, 18, 7);
    under.position.set(0, -0.35, 0);
    this.scene.add(under);

    this.accentLights = { left, right, under };
  }

  _buildStage() {
    const THREE = this.THREE;
    const stage = new THREE.Group();

    const grid = new THREE.GridHelper(16, 32, this.options.accent, this.options.accent);
    grid.material.transparent = true;
    grid.material.opacity = 0.14;
    grid.position.y = -0.002;
    stage.add(grid);

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(3.15, 0.012, 8, 160),
      new THREE.MeshBasicMaterial({
        color: this.options.accent,
        transparent: true,
        opacity: 0.75,
      })
    );
    ring.rotation.x = Math.PI / 2;
    stage.add(ring);

    const outer = new THREE.Mesh(
      new THREE.TorusGeometry(3.95, 0.006, 8, 160),
      new THREE.MeshBasicMaterial({
        color: this.options.accent2,
        transparent: true,
        opacity: 0.4,
      })
    );
    outer.rotation.x = Math.PI / 2;
    stage.add(outer);

    stage.add(this._buildShadowBlob());
    this.scene.add(stage);
    this.stageGroup = stage;
  }

  /* Recoloreaza scena dupa schimbarea temei. */
  setTheme(colors) {
    Object.assign(this.options, colors);
    if (!this.ready) return;

    this.accentLights.left.color.set(this.options.accent);
    this.accentLights.right.color.set(this.options.accent2);
    this.accentLights.under.color.set(this.options.accent);
    this.scene.fog.color.set(this.options.bg);
    if (this.edgeMaterial) this.edgeMaterial.color.set(this.options.accent);

    this.scene.remove(this.stageGroup);
    this.stageGroup.traverse((node) => {
      node.geometry?.dispose?.();
      node.material?.map?.dispose?.();
      node.material?.dispose?.();
    });
    this._buildStage();
    this._buildEnvironment();
  }

  _buildShadowBlob() {
    const THREE = this.THREE;
    const size = 128;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    gradient.addColorStop(0, "rgba(0,0,0,0.75)");
    gradient.addColorStop(0.55, "rgba(0,0,0,0.3)");
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);

    const texture = new THREE.CanvasTexture(canvas);
    const blob = new THREE.Mesh(
      new THREE.PlaneGeometry(6.4, 3.4),
      new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
      })
    );
    blob.rotation.x = -Math.PI / 2;
    blob.position.y = 0.004;
    return blob;
  }

  /* --------------------------------------------------------------- */
  /* Masina procedurala                                               */
  /* --------------------------------------------------------------- */
  _buildProceduralCar(colorHex) {
    const THREE = this.THREE;
    const group = new THREE.Group();
    const width = 1.86;

    const bodyShape = new THREE.Shape();
    bodyShape.moveTo(-1.95, 0.22);
    bodyShape.lineTo(-2.06, 0.5);
    bodyShape.quadraticCurveTo(-2.1, 0.74, -1.86, 0.8);
    bodyShape.quadraticCurveTo(-1.5, 0.86, -1.22, 0.88);
    bodyShape.quadraticCurveTo(-0.95, 1.26, -0.52, 1.3);
    bodyShape.lineTo(0.2, 1.31);
    bodyShape.quadraticCurveTo(0.68, 1.28, 0.86, 0.94);
    bodyShape.quadraticCurveTo(1.3, 0.84, 1.72, 0.78);
    bodyShape.quadraticCurveTo(2.04, 0.72, 2.08, 0.46);
    bodyShape.lineTo(2.04, 0.24);
    bodyShape.quadraticCurveTo(1.9, 0.16, 1.6, 0.16);
    bodyShape.lineTo(-1.6, 0.16);
    bodyShape.quadraticCurveTo(-1.88, 0.16, -1.95, 0.22);

    const bodyGeometry = new THREE.ExtrudeGeometry(bodyShape, {
      depth: width,
      bevelEnabled: true,
      bevelThickness: 0.1,
      bevelSize: 0.1,
      bevelSegments: 4,
      curveSegments: 18,
    });
    bodyGeometry.translate(0, 0, -width / 2);

    const bodyMaterial = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(colorHex),
      metalness: 0.5,
      roughness: 0.22,
      clearcoat: 1,
      clearcoatRoughness: 0.06,
      envMapIntensity: 1.25,
    });
    group.add(new THREE.Mesh(bodyGeometry, bodyMaterial));

    /* Contur holografic subtil peste caroserie. */
    this.edgeMaterial = new THREE.LineBasicMaterial({
      color: this.options.accent,
      transparent: true,
      opacity: 0.22,
    });
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(bodyGeometry, 26),
      this.edgeMaterial
    );
    edges.scale.set(1.004, 1.004, 1.004);
    group.add(edges);

    /* Banda de geamuri. */
    const glassShape = new THREE.Shape();
    glassShape.moveTo(-1.16, 0.9);
    glassShape.quadraticCurveTo(-0.92, 1.2, -0.52, 1.24);
    glassShape.lineTo(0.18, 1.25);
    glassShape.quadraticCurveTo(0.6, 1.22, 0.78, 0.95);
    glassShape.lineTo(-1.16, 0.9);

    const glassGeometry = new THREE.ExtrudeGeometry(glassShape, {
      depth: width + 0.04,
      bevelEnabled: false,
      curveSegments: 14,
    });
    glassGeometry.translate(0, 0, -(width + 0.04) / 2);
    group.add(
      new THREE.Mesh(
        glassGeometry,
        new THREE.MeshPhysicalMaterial({
          color: 0x080d14,
          metalness: 0.2,
          roughness: 0.08,
          envMapIntensity: 1.6,
        })
      )
    );

    /* Roti. */
    const tireMaterial = new THREE.MeshStandardMaterial({
      color: 0x12161b,
      roughness: 0.88,
      metalness: 0.05,
    });
    const rimMaterial = new THREE.MeshPhysicalMaterial({
      color: 0xd3dae1,
      metalness: 1,
      roughness: 0.24,
      envMapIntensity: 1.5,
    });
    const tireGeometry = new THREE.CylinderGeometry(0.42, 0.42, 0.3, 36);
    const rimGeometry = new THREE.CylinderGeometry(0.25, 0.25, 0.32, 20);

    this.wheels = [];
    for (const x of [1.3, -1.32]) {
      for (const z of [width / 2 - 0.02, -(width / 2 - 0.02)]) {
        const wheel = new THREE.Group();
        const tire = new THREE.Mesh(tireGeometry, tireMaterial);
        const rim = new THREE.Mesh(rimGeometry, rimMaterial);
        tire.rotation.x = Math.PI / 2;
        rim.rotation.x = Math.PI / 2;
        wheel.add(tire, rim);
        wheel.position.set(x, 0.42, z);
        group.add(wheel);
        this.wheels.push(wheel);
      }
    }

    /* Faruri si stopuri. */
    const headlight = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: new THREE.Color(0xdff3ff),
      emissiveIntensity: 2.4,
    });
    const taillight = new THREE.MeshStandardMaterial({
      color: 0x320207,
      emissive: new THREE.Color(0xff2d3f),
      emissiveIntensity: 2.2,
    });
    const lampGeometry = new THREE.BoxGeometry(0.08, 0.1, 0.46);
    for (const z of [0.56, -0.56]) {
      const front = new THREE.Mesh(lampGeometry, headlight);
      front.position.set(2.06, 0.48, z);
      group.add(front);
      const rear = new THREE.Mesh(lampGeometry, taillight);
      rear.position.set(-2.07, 0.58, z);
      group.add(rear);
    }

    return group;
  }

  /* --------------------------------------------------------------- */
  async _loadModel(url) {
    const loaderUrl = this.options.gltfLoaderSrc;
    const module = await import(/* webpackIgnore: true */ loaderUrl);
    const Loader = module.GLTFLoader;
    if (!Loader) throw new Error("GLTFLoader indisponibil");

    const gltf = await new Promise((resolve, reject) => {
      new Loader().load(url, resolve, undefined, reject);
    });

    const THREE = this.THREE;
    const model = gltf.scene;
    const box = new THREE.Box3().setFromObject(model);
    const size = new THREE.Vector3();
    const center = new THREE.Vector3();
    box.getSize(size);
    box.getCenter(center);

    const scale = 4.3 / Math.max(size.x, size.z, 0.001);
    model.scale.setScalar(scale);
    model.position.set(
      -center.x * scale,
      -box.min.y * scale,
      -center.z * scale
    );

    const wrapper = new THREE.Group();
    wrapper.add(model);
    return wrapper;
  }

  /* --------------------------------------------------------------- */
  async setVehicle(vehicle) {
    if (this.failed) return;
    if (!this.ready) {
      this._pendingVehicle = vehicle;
      return;
    }

    const key = `${vehicle.model3d || ""}|${vehicle.colorHex}`;
    if (key === this._currentKey) return;
    this._currentKey = key;

    this._clearCar();
    this.wheels = [];

    if (vehicle.model3d) {
      try {
        const model = await this._loadModel(vehicle.model3d);
        if (this.disposed || this._currentKey !== key) return;
        this.carGroup.add(model);
        return;
      } catch (err) {
        console.warn(
          "vehicle-manager-card: modelul 3D nu a putut fi incarcat, folosesc masina procedurala",
          err
        );
        if (this.disposed || this._currentKey !== key) return;
      }
    }

    this.carGroup.add(this._buildProceduralCar(vehicle.colorHex));
  }

  _clearCar() {
    if (!this.carGroup) return;
    while (this.carGroup.children.length) {
      const child = this.carGroup.children.pop();
      child.traverse?.((node) => {
        node.geometry?.dispose?.();
        const material = node.material;
        if (Array.isArray(material)) material.forEach((m) => m.dispose?.());
        else material?.dispose?.();
      });
    }
  }

  /* --------------------------------------------------------------- */
  _attachPointerHandlers() {
    const onDown = (event) => {
      this.dragging = true;
      this.lastPointer = event.clientX;
      this.lastPointerY = event.clientY;
      this.canvas.setPointerCapture?.(event.pointerId);
    };
    const onMove = (event) => {
      if (!this.dragging) return;
      const dx = event.clientX - this.lastPointer;
      const dy = event.clientY - this.lastPointerY;
      this.lastPointer = event.clientX;
      this.lastPointerY = event.clientY;
      this.yaw -= dx * 0.008;
      this.pitch = clamp(this.pitch + dy * 0.004, -0.05, 0.75);
      this.spin = -dx * 0.004;
      event.preventDefault();
    };
    const onUp = (event) => {
      this.dragging = false;
      this.canvas.releasePointerCapture?.(event.pointerId);
    };

    this.canvas.addEventListener("pointerdown", onDown);
    this.canvas.addEventListener("pointermove", onMove);
    this.canvas.addEventListener("pointerup", onUp);
    this.canvas.addEventListener("pointercancel", onUp);
    this.canvas.addEventListener("pointerleave", onUp);
    this._handlers = { onDown, onMove, onUp };
  }

  _observeResize() {
    this._resize();
    this.observer = new ResizeObserver(() => this._resize());
    this.observer.observe(this.canvas.parentElement || this.canvas);
  }

  _resize() {
    if (!this.renderer) return;
    const host = this.canvas.parentElement || this.canvas;
    const width = Math.max(host.clientWidth || 0, 1);
    const height = Math.max(host.clientHeight || 0, 1);
    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();

    /*
     * Intr-o scena ingusta (ex. modul compact pe telefon) masina ar iesi din cadru:
     * camera se departeaza proportional, iar ceata se muta odata cu ea.
     */
    const fit = Math.max(1, 1.2 / this.camera.aspect);
    this.radius = 8.2 * fit;
    this.scene.fog.near = 7 + this.radius - 8.2;
    this.scene.fog.far = 17 + this.radius - 8.2;
  }

  _loop(now) {
    if (this.disposed) return;
    const delta = Math.min((now - this.lastFrame) / 1000 || 0, 0.1);
    this.lastFrame = now;

    if (this.options.autoRotate && !this.dragging) {
      this.yaw += this.options.rotateSpeed * delta;
    }
    if (!this.dragging) {
      this.yaw += this.spin;
      this.spin *= 0.94;
      if (Math.abs(this.spin) < 0.00002) this.spin = 0;
    }

    const radius = this.radius;
    const pitch = this.pitch;
    this.camera.position.set(
      Math.sin(this.yaw) * radius * Math.cos(pitch),
      0.9 + Math.sin(pitch) * radius,
      Math.cos(this.yaw) * radius * Math.cos(pitch)
    );
    this.camera.lookAt(0, 0.62, 0);

    if (this.wheels) {
      for (const wheel of this.wheels) wheel.rotation.z -= delta * 0.6;
    }

    this.renderer.render(this.scene, this.camera);
    this._raf = requestAnimationFrame((timestamp) => this._loop(timestamp));
  }

  setOptions(options) {
    Object.assign(this.options, options);
  }

  dispose() {
    this.disposed = true;
    if (this._raf) cancelAnimationFrame(this._raf);
    this.observer?.disconnect();
    this._clearCar();
    this.envMap?.dispose?.();
    this.renderer?.dispose?.();
  }
}

/* ------------------------------------------------------------------ */
/* Teme                                                                */
/* ------------------------------------------------------------------ */

/*
 * Tema e salvata pe server (vehicle_manager/theme/*), deci e aceeasi pe toate
 * dispozitivele. Cheile si limitele trebuie sa ramana sincronizate cu theme.py.
 */
const FILES_WS_SUBSCRIBE = "vehicle_manager/files/subscribe";
const FILES_WS_DELETE = "vehicle_manager/files/delete";
const FILES_URL = "/api/vehicle_manager/files";
/* Pe langa acte: talon, cartea masinii etc. (GENERAL_SLOT din files.py) */
const FILES_GENERAL = ["general", "Alte documente (talon, cartea masinii...)", "mdi:folder-outline"];

const EXPENSES_WS_SUBSCRIBE = "vehicle_manager/expenses/subscribe";
const EXPENSES_WS_ADD = "vehicle_manager/expenses/add";
const EXPENSES_WS_DELETE = "vehicle_manager/expenses/delete";

/* Aceleasi chei ca EXPENSE_CATEGORIES din const.py. */
const EXPENSE_CATEGORIES = {
  rca: ["RCA", "mdi:shield-car"],
  itp: ["ITP", "mdi:car-wrench"],
  rovinieta: ["Rovinieta", "mdi:road-variant"],
  casco: ["CASCO", "mdi:shield-star"],
  revizie: ["Revizie", "mdi:oil"],
  distributie: ["Distributie", "mdi:cog-sync"],
  reparatii: ["Reparatii", "mdi:wrench"],
  anvelope: ["Anvelope", "mdi:tire"],
  combustibil: ["Combustibil", "mdi:gas-station"],
  spalare: ["Spalare", "mdi:car-wash"],
  parcare: ["Parcare", "mdi:parking"],
  amenzi: ["Amenzi", "mdi:file-document-alert"],
  taxe: ["Taxe si impozit", "mdi:bank"],
  accesorii: ["Accesorii", "mdi:car-seat"],
  altele: ["Altele", "mdi:dots-horizontal"],
};

function todayIso() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

const THEME_WS_SUBSCRIBE = "vehicle_manager/theme/subscribe";
const THEME_WS_SAVE = "vehicle_manager/theme/save";
const THEME_BG_UPLOAD = "/api/vehicle_manager/theme/background";

/* Aceeasi regula ca BG_URL_RE din theme.py: valoarea ajunge in CSS url("..."). */
const BG_URL_RE = /^(https?:\/\/|\/)[^\s"'()<>\\]+$/;
const BG_MAX_SIDE = 1920;

const THEME_COLOR_KEYS = [
  "accent", "accent2", "bg", "panel", "text", "dim", "line", "ok", "warn", "bad",
];

const THEME_DEFAULTS = {
  preset: "neon",
  follow_ha: false,
  accent: "#00e5ff",
  accent2: "#ff2bd6",
  bg: "#070a10",
  panel: "#121822",
  text: "#e8eef5",
  dim: "#8b9cb0",
  line: "#82aac8",
  ok: "#22d38a",
  warn: "#ffb020",
  bad: "#ff4d5e",
  font_family: "default",
  font_scale: 1,
  spacing: 1,
  radius: 1,
  panel_opacity: 0.68,
  blur: 9,
  glow: 1,
  grid: true,
  stage_height: 300,
  bg_image: "",
  bg_target: "card",
  bg_fit: "cover",
  bg_position: "center",
  bg_overlay: 0.55,
  bg_blur: 0,
};

/* Preferintele de dimensiuni si imaginea de fundal raman cand alegi o alta presetare. */
const THEME_LAYOUT_KEYS = [
  "font_family", "font_scale", "spacing", "stage_height",
  "bg_image", "bg_target", "bg_fit", "bg_position", "bg_overlay", "bg_blur",
];

const THEME_PRESETS = [
  { id: "neon", name: "Neon", values: {} },
  {
    id: "ocean",
    name: "Ocean",
    values: {
      accent: "#38bdf8", accent2: "#6366f1", bg: "#06111d", panel: "#0e1d2e",
      text: "#e6f1fb", dim: "#8aa3bb", line: "#5b8db8",
      ok: "#2dd4bf", warn: "#fbbf24", bad: "#f87171",
    },
  },
  {
    id: "sunset",
    name: "Sunset",
    values: {
      accent: "#ff8a3d", accent2: "#ff3d7f", bg: "#130a0d", panel: "#24131a",
      text: "#fbeee8", dim: "#b9a19b", line: "#c7837a",
      ok: "#4ade80", warn: "#ffc53d", bad: "#ff4d5e",
    },
  },
  {
    id: "forest",
    name: "Forest",
    values: {
      accent: "#7cf5c0", accent2: "#c6f432", bg: "#06110c", panel: "#0f1f17",
      text: "#e7f5ec", dim: "#8fae9c", line: "#6fa58a",
      ok: "#4ade80", warn: "#facc15", bad: "#fb7185",
    },
  },
  {
    id: "carbon",
    name: "Carbon",
    values: {
      accent: "#e5e7eb", accent2: "#9ca3af", bg: "#0a0a0a", panel: "#161616",
      text: "#f3f4f6", dim: "#9ca3af", line: "#6b7280", glow: 0.4,
    },
  },
  {
    id: "light",
    name: "Light",
    values: {
      accent: "#0077cc", accent2: "#d6336c", bg: "#f2f5f9", panel: "#ffffff",
      text: "#17202b", dim: "#5b6878", line: "#7a8899",
      ok: "#148a55", warn: "#b86e00", bad: "#c8243a",
      grid: false, glow: 0.5, panel_opacity: 0.9,
    },
  },
  { id: "ha", name: "Home Assistant", values: { follow_ha: true, glow: 0.6 } },
];

/* Culorile temei Home Assistant, folosite cand follow_ha este activ. */
const HA_COLOR_VARS = {
  accent: "var(--primary-color, #03a9f4)",
  accent2: "var(--accent-color, #ff9800)",
  bg: "var(--card-background-color, var(--ha-card-background, #1c1c1c))",
  panel: "var(--secondary-background-color, #282828)",
  text: "var(--primary-text-color, #e1e1e1)",
  dim: "var(--secondary-text-color, #9b9b9b)",
  line: "var(--divider-color, #6f6f6f)",
  ok: "var(--success-color, #43a047)",
  warn: "var(--warning-color, #ffa600)",
  bad: "var(--error-color, #db4437)",
};

const MONO_STACK = 'ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace';

/* [font text, font etichete] */
const FONT_STACKS = {
  default: ["inherit", MONO_STACK],
  ha: ["inherit", "inherit"],
  system: ['system-ui, -apple-system, "Segoe UI", Roboto, sans-serif', 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'],
  mono: [MONO_STACK, MONO_STACK],
  serif: ['Georgia, "Times New Roman", serif', 'Georgia, "Times New Roman", serif'],
  rounded: ['ui-rounded, "Nunito", "Varela Round", "Segoe UI", sans-serif', 'ui-rounded, "Nunito", "Varela Round", "Segoe UI", sans-serif'],
};

const THEME_GROUPS = [
  {
    title: "Culori",
    items: [
      { key: "follow_ha", type: "bool", label: "Foloseste culorile temei Home Assistant" },
      { key: "accent", type: "color", label: "Accent principal" },
      { key: "accent2", type: "color", label: "Accent secundar" },
      { key: "bg", type: "color", label: "Fundal" },
      { key: "panel", type: "color", label: "Panouri" },
      { key: "text", type: "color", label: "Text" },
      { key: "dim", type: "color", label: "Text secundar" },
      { key: "line", type: "color", label: "Linii si contururi" },
      { key: "ok", type: "color", label: "Stare: valabil" },
      { key: "warn", type: "color", label: "Stare: expira curand" },
      { key: "bad", type: "color", label: "Stare: expirat" },
    ],
  },
  {
    title: "Text",
    items: [
      {
        key: "font_family",
        type: "select",
        label: "Font",
        options: [
          ["default", "Futurist (implicit)"],
          ["ha", "Fontul Home Assistant"],
          ["system", "Fontul sistemului"],
          ["mono", "Monospace"],
          ["serif", "Serif"],
          ["rounded", "Rotunjit"],
        ],
      },
      { key: "font_scale", type: "range", label: "Dimensiune font", min: 0.75, max: 1.6, step: 0.05, format: "percent" },
    ],
  },
  {
    title: "Aspect",
    items: [
      { key: "spacing", type: "range", label: "Spatiere", min: 0.6, max: 1.6, step: 0.05, format: "percent" },
      { key: "radius", type: "range", label: "Rotunjire colturi", min: 0, max: 2, step: 0.1, format: "percent" },
      { key: "panel_opacity", type: "range", label: "Opacitate panouri", min: 0.1, max: 1, step: 0.02, format: "percent" },
      { key: "blur", type: "range", label: "Estompare panouri", min: 0, max: 24, step: 1, format: "px" },
      { key: "glow", type: "range", label: "Intensitate stralucire", min: 0, max: 2, step: 0.1, format: "percent" },
      { key: "grid", type: "bool", label: "Grila de fundal" },
    ],
  },
  {
    title: "Scena 3D",
    items: [
      { key: "stage_height", type: "range", label: "Inaltime scena", min: 180, max: 640, step: 10, format: "px" },
    ],
  },
  {
    title: "Imagine de fundal",
    items: [
      { key: "bg_image", type: "image", label: "Imagine" },
      {
        key: "bg_target",
        type: "select",
        label: "Unde se afiseaza",
        options: [["card", "Tot cardul"], ["stage", "Doar scena 3D"]],
      },
      {
        key: "bg_fit",
        type: "select",
        label: "Incadrare",
        options: [["cover", "Umple"], ["contain", "Potriveste"], ["tile", "Mozaic"]],
      },
      {
        key: "bg_position",
        type: "select",
        label: "Pozitie",
        options: [["center", "Centru"], ["top", "Sus"], ["bottom", "Jos"]],
      },
      { key: "bg_overlay", type: "range", label: "Acoperire cu culoarea de fundal", min: 0, max: 0.95, step: 0.05, format: "percent" },
      { key: "bg_blur", type: "range", label: "Estompare imagine", min: 0, max: 20, step: 1, format: "px" },
    ],
  },
];

const THEME_RANGES = Object.fromEntries(
  THEME_GROUPS.flatMap((group) => group.items)
    .filter((item) => item.type === "range")
    .map((item) => [item.key, item])
);

const HEX_RE = /^#[0-9a-f]{6}$/i;

const THEME_SELECTS = Object.fromEntries(
  THEME_GROUPS.flatMap((group) => group.items)
    .filter((item) => item.type === "select")
    .map((item) => [item.key, item.options.map(([value]) => value)])
);

/* Completeaza si valideaza o tema, ca valorile gresite sa nu strice cardul. */
function normalizeTheme(raw) {
  const theme = { ...THEME_DEFAULTS };
  if (!raw || typeof raw !== "object") return theme;

  for (const [key, fallback] of Object.entries(THEME_DEFAULTS)) {
    const value = raw[key];
    if (value === undefined || value === null) continue;
    if (THEME_COLOR_KEYS.includes(key)) {
      if (typeof value === "string" && HEX_RE.test(value)) theme[key] = value.toLowerCase();
    } else if (typeof fallback === "boolean") {
      theme[key] = Boolean(value);
    } else if (typeof fallback === "number") {
      const number = Number(value);
      const range = THEME_RANGES[key];
      if (Number.isFinite(number)) {
        theme[key] = range ? clamp(number, range.min, range.max) : number;
      }
    } else if (THEME_SELECTS[key]) {
      if (THEME_SELECTS[key].includes(value)) theme[key] = value;
    } else if (key === "bg_image") {
      if (value === "" || BG_URL_RE.test(value)) theme[key] = value;
    } else {
      theme[key] = String(value);
    }
  }
  return theme;
}

function formatThemeValue(item, value) {
  if (item.format === "percent") return `${Math.round(value * 100)}%`;
  if (item.format === "px") return `${Math.round(value)}px`;
  return String(value);
}

/* Variabilele CSS aplicate pe ha-card. */
function themeToCss(theme) {
  const color = (key) => (theme.follow_ha ? HA_COLOR_VARS[key] : theme[key]);
  const [font, mono] = FONT_STACKS[theme.font_family] || FONT_STACKS.default;
  return {
    "--vm-accent": color("accent"),
    "--vm-accent-2": color("accent2"),
    "--vm-bg": color("bg"),
    "--vm-panel-c": color("panel"),
    "--vm-panel-p": `${Math.round(theme.panel_opacity * 100)}%`,
    "--vm-text": color("text"),
    "--vm-dim": color("dim"),
    "--vm-line-c": color("line"),
    "--vm-ok": color("ok"),
    "--vm-warn": color("warn"),
    "--vm-bad": color("bad"),
    "--vm-font": font,
    "--vm-mono": mono,
    "--vm-fs": String(theme.font_scale),
    "--vm-sp": String(theme.spacing),
    "--vm-r": String(theme.radius),
    "--vm-blur": `${theme.blur}px`,
    "--vm-glow": String(theme.glow),
    "--vm-glow-1": `${Math.round(16 * theme.glow)}%`,
    "--vm-glow-2": `${Math.round(13 * theme.glow)}%`,
    "--vm-glow-3": `${Math.round(10 * theme.glow)}%`,
    "--vm-grid": theme.grid ? String(0.25 * Math.max(theme.glow, 0.4)) : "0",
    "--vm-stage-h": `${Math.round(theme.stage_height)}px`,
    "--vm-bg-img": theme.bg_image ? `url("${theme.bg_image}")` : "none",
    "--vm-bg-size": theme.bg_fit === "tile" ? "auto" : theme.bg_fit,
    "--vm-bg-repeat": theme.bg_fit === "tile" ? "repeat" : "no-repeat",
    "--vm-bg-pos": `center ${theme.bg_position}`,
    "--vm-bg-ov": String(theme.bg_overlay),
    "--vm-bg-blur": `${theme.bg_blur}px`,
  };
}

/*
 * Micsoreaza pozele mari inainte de upload (pozele de telefon au usor 5-10 MB).
 * GIF-urile si formatele pe care browserul nu le poate decoda raman neschimbate.
 */
async function shrinkImage(file) {
  if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return file;
  try {
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, BG_MAX_SIDE / Math.max(bitmap.width, bitmap.height));
    if (scale === 1 && file.size < 1.5 * 1024 * 1024) {
      bitmap.close?.();
      return file;
    }
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close?.();
    /* PNG ramane PNG ca sa pastreze transparenta */
    const type = file.type === "image/png" ? "image/png" : "image/jpeg";
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, type, 0.85));
    return blob && blob.size < file.size ? blob : file;
  } catch (err) {
    return file;
  }
}

/* ------------------------------------------------------------------ */
/* Stiluri                                                             */
/* ------------------------------------------------------------------ */

const STYLES = `
:host { display: block; }

/*
 * Toate valorile vizuale vin din variabile setate de tema (vezi THEME_DEFAULTS).
 * Variantele transparente se obtin cu color-mix, ca orice culoare aleasa sa functioneze.
 */
ha-card {
  --vm-accent: #00e5ff;
  --vm-accent-2: #ff2bd6;
  --vm-bg: #070a10;
  --vm-panel-c: #121822;
  --vm-panel-p: 68%;
  --vm-text: #e8eef5;
  --vm-dim: #8b9cb0;
  --vm-line-c: #82aac8;
  --vm-ok: #22d38a;
  --vm-warn: #ffb020;
  --vm-bad: #ff4d5e;
  --vm-font: inherit;
  --vm-mono: ui-monospace, "SFMono-Regular", Menlo, monospace;
  --vm-fs: 1;
  --vm-sp: 1;
  --vm-r: 1;
  --vm-blur: 9px;
  --vm-glow: 1;
  --vm-glow-1: 16%;
  --vm-glow-2: 13%;
  --vm-glow-3: 10%;
  --vm-grid: 0.25;
  --vm-stage-h: 300px;

  --vm-panel: color-mix(in srgb, var(--vm-panel-c) var(--vm-panel-p), transparent);
  --vm-line: color-mix(in srgb, var(--vm-line-c) 22%, transparent);
  --vm-soft: color-mix(in srgb, var(--vm-bg) 82%, transparent);

  display: block;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--vm-line);
  border-radius: calc(12px * var(--vm-r));
  background:
    radial-gradient(1100px 420px at 50% -12%, color-mix(in srgb, var(--vm-accent) var(--vm-glow-1), transparent), transparent 70%),
    radial-gradient(760px 420px at 108% 118%, color-mix(in srgb, var(--vm-accent-2) var(--vm-glow-2), transparent), transparent 70%),
    linear-gradient(160deg, color-mix(in srgb, var(--vm-bg) 88%, var(--vm-text)) 0%, var(--vm-bg) 55%, color-mix(in srgb, var(--vm-bg) 90%, #000) 100%);
  color: var(--vm-text);
  font-family: var(--vm-font);
}

ha-card::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background-image:
    linear-gradient(var(--vm-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--vm-line) 1px, transparent 1px);
  background-size: 46px 46px;
  opacity: var(--vm-grid);
  mask-image: radial-gradient(130% 90% at 50% 0%, #000 25%, transparent 78%);
  -webkit-mask-image: radial-gradient(130% 90% at 50% 0%, #000 25%, transparent 78%);
}

/* ---- imagine de fundal ---- */
.bg-layer {
  position: absolute;
  inset: calc(var(--vm-bg-blur, 0px) * -2);
  z-index: 0;
  pointer-events: none;
  background-image: var(--vm-bg-img, none);
  background-size: var(--vm-bg-size, cover);
  background-repeat: var(--vm-bg-repeat, no-repeat);
  background-position: var(--vm-bg-pos, center);
  filter: blur(var(--vm-bg-blur, 0px));
}
.bg-layer::after {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--vm-bg);
  opacity: var(--vm-bg-ov, 0.55);
}
.bg-layer[hidden] { display: none; }
.vm, .empty { position: relative; z-index: 2; }

.vm { position: relative; padding: calc(14px * var(--vm-sp)) calc(16px * var(--vm-sp)) calc(12px * var(--vm-sp)); }

/* ---- bara superioara ---- */
.top {
  display: flex;
  align-items: center;
  gap: calc(12px * var(--vm-sp));
  flex-wrap: wrap;
  padding-bottom: calc(12px * var(--vm-sp));
  border-bottom: 1px solid var(--vm-line);
}

.brand { display: flex; align-items: center; gap: 10px; min-width: 0; }

.led {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--vm-ok);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--vm-ok) 16%, transparent), 0 0 calc(14px * var(--vm-glow)) var(--vm-ok);
  flex: none;
}
.led[data-status="warning"] { background: var(--vm-warn); box-shadow: 0 0 0 3px color-mix(in srgb, var(--vm-warn) 16%, transparent), 0 0 calc(14px * var(--vm-glow)) var(--vm-warn); }
.led[data-status="expired"] { background: var(--vm-bad); box-shadow: 0 0 0 3px color-mix(in srgb, var(--vm-bad) 18%, transparent), 0 0 calc(14px * var(--vm-glow)) var(--vm-bad); animation: pulse 1.4s ease-in-out infinite; }
.led[data-status="unknown"] { background: var(--vm-dim); box-shadow: none; }

@keyframes pulse { 50% { opacity: .35; } }

.titles { display: flex; flex-direction: column; min-width: 0; }
.titles .t {
  font-size: calc(15px * var(--vm-fs)); font-weight: 650; letter-spacing: .02em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.titles .s {
  font: calc(10px * var(--vm-fs))/1.4 var(--vm-mono);
  letter-spacing: .16em; text-transform: uppercase; color: var(--vm-dim);
}

.top-spacer { flex: 1 1 auto; }

.picker { position: relative; flex: 0 1 230px; min-width: 150px; }
.picker select {
  width: 100%;
  appearance: none;
  padding: 8px 32px 8px 12px;
  font: inherit; font-size: calc(13px * var(--vm-fs));
  color: var(--vm-text);
  background: var(--vm-soft);
  border: 1px solid var(--vm-line);
  border-radius: calc(10px * var(--vm-r));
  cursor: pointer;
}
.picker select option { background: var(--vm-bg); color: var(--vm-text); }
.picker select:focus-visible { outline: 2px solid var(--vm-accent); outline-offset: 1px; }
.picker::after {
  content: "";
  position: absolute; right: 12px; top: 50%;
  width: 6px; height: 6px; margin-top: -4px;
  border-right: 2px solid var(--vm-accent);
  border-bottom: 2px solid var(--vm-accent);
  transform: rotate(45deg);
  pointer-events: none;
}

.plate {
  font: 600 calc(13px * var(--vm-fs))/1 var(--vm-mono);
  letter-spacing: .12em;
  padding: 7px 11px;
  border-radius: calc(7px * var(--vm-r));
  color: #0a0f16;
  background: linear-gradient(180deg, #f4f7fa, #c9d3dd);
  border: 1px solid rgba(255,255,255,.55);
  white-space: nowrap;
}

.icon-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  min-width: 34px; height: 34px; flex: none; padding: 0 8px;
  border-radius: calc(9px * var(--vm-r)); cursor: pointer;
  font: calc(10px * var(--vm-fs))/1 var(--vm-mono); letter-spacing: .14em; text-transform: uppercase;
  color: var(--vm-dim);
  background: var(--vm-soft);
  border: 1px solid var(--vm-line);
}
.icon-btn ha-icon { --mdc-icon-size: 18px; }
.icon-btn:hover,
.icon-btn[aria-expanded="true"] { color: var(--vm-accent); border-color: var(--vm-accent); }

/* ---- corp ---- */
.body {
  display: grid;
  grid-template-columns: minmax(170px, 0.95fr) minmax(260px, 1.5fr) minmax(200px, 1.1fr);
  gap: calc(14px * var(--vm-sp));
  padding-top: calc(14px * var(--vm-sp));
  align-items: stretch;
}

.panel {
  position: relative;
  padding: calc(12px * var(--vm-sp));
  border-radius: calc(14px * var(--vm-r));
  background: var(--vm-panel);
  border: 1px solid var(--vm-line);
  backdrop-filter: blur(var(--vm-blur));
  -webkit-backdrop-filter: blur(var(--vm-blur));
}

.panel h3 {
  margin: 0 0 10px;
  font: calc(10px * var(--vm-fs))/1 var(--vm-mono);
  letter-spacing: .2em; text-transform: uppercase;
  color: var(--vm-accent);
  display: flex; align-items: center; gap: 8px;
}
.panel h3::after {
  content: ""; flex: 1 1 auto; height: 1px;
  background: linear-gradient(90deg, var(--vm-accent), transparent);
  opacity: .55;
}

/* ---- caracteristici ---- */
.specs { display: flex; flex-direction: column; gap: 2px; }

.spec {
  display: grid;
  grid-template-columns: 22px 1fr auto;
  align-items: center;
  gap: 8px;
  padding: calc(7px * var(--vm-sp)) 4px;
  border-bottom: 1px dashed var(--vm-line);
  background: none; border-left: 0; border-right: 0; border-top: 0;
  color: inherit; font: inherit; text-align: left; width: 100%;
}
.spec:last-child { border-bottom: 0; }
.spec[data-clickable="true"] { cursor: pointer; border-radius: calc(8px * var(--vm-r)); }
.spec[data-clickable="true"]:hover { background: color-mix(in srgb, var(--vm-accent) 8%, transparent); }

.spec ha-icon { --mdc-icon-size: calc(17px * var(--vm-fs)); color: var(--vm-dim); }
.spec .k {
  font: calc(10px * var(--vm-fs))/1.3 var(--vm-mono);
  letter-spacing: .1em; text-transform: uppercase; color: var(--vm-dim);
}
.spec .v {
  font-size: calc(13.5px * var(--vm-fs)); font-weight: 600; text-align: right;
  display: inline-flex; align-items: center; gap: 6px;
}
.spec .nav {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: 7px;
  color: var(--vm-accent); border: 1px solid color-mix(in srgb, var(--vm-accent) 55%, transparent);
}
.spec .nav ha-icon { --mdc-icon-size: 16px; color: var(--vm-accent); }
.spec .when { font-size: calc(12.5px * var(--vm-fs)); }
.spec .auto {
  font: 600 calc(8.5px * var(--vm-fs))/1 var(--vm-mono); letter-spacing: .12em; text-transform: uppercase;
  padding: 3px 5px; border-radius: 5px;
  color: var(--vm-accent); border: 1px solid color-mix(in srgb, var(--vm-accent) 55%, transparent);
}
.swatch {
  width: 12px; height: 12px; border-radius: 3px;
  border: 1px solid rgba(255,255,255,.35);
  box-shadow: 0 0 8px rgba(255,255,255,.18);
}

/* ---- scena 3D ---- */
.stage {
  position: relative;
  min-height: var(--vm-stage-h);
  border-radius: calc(16px * var(--vm-r));
  overflow: hidden;
  border: 1px solid var(--vm-line);
  background:
    radial-gradient(70% 55% at 50% 42%, color-mix(in srgb, var(--vm-accent) var(--vm-glow-3), transparent), transparent 70%),
    linear-gradient(180deg, color-mix(in srgb, var(--vm-bg) 30%, transparent), color-mix(in srgb, var(--vm-bg) 85%, transparent));
}

.stage canvas {
  position: absolute; inset: 0;
  display: block; width: 100%; height: 100%;
  touch-action: none; cursor: grab;
}
.stage canvas:active { cursor: grabbing; }

.stage .photo {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: contain;
  padding: 18px;
  box-sizing: border-box;
  filter: drop-shadow(0 18px 28px rgba(0,0,0,.6));
}

.stage [hidden] { display: none !important; }

.bracket {
  position: absolute; width: 20px; height: 20px;
  border: 2px solid var(--vm-accent); opacity: calc(.5 * var(--vm-glow)); pointer-events: none;
}
.bracket.tl { top: 10px; left: 10px; border-right: 0; border-bottom: 0; }
.bracket.tr { top: 10px; right: 10px; border-left: 0; border-bottom: 0; }
.bracket.bl { bottom: 10px; left: 10px; border-right: 0; border-top: 0; }
.bracket.br { bottom: 10px; right: 10px; border-left: 0; border-top: 0; }

.hud {
  position: absolute; left: 14px; bottom: 12px;
  font: calc(9px * var(--vm-fs))/1.5 var(--vm-mono);
  letter-spacing: .18em; text-transform: uppercase;
  color: var(--vm-dim); pointer-events: none;
}

.stage-actions {
  position: absolute; top: 10px; right: 10px;
  display: flex; gap: 6px;
}
.chip {
  font: calc(9px * var(--vm-fs))/1 var(--vm-mono);
  letter-spacing: .16em; text-transform: uppercase;
  padding: 7px 9px; border-radius: calc(8px * var(--vm-r)); cursor: pointer;
  color: var(--vm-dim);
  background: var(--vm-soft);
  border: 1px solid var(--vm-line);
}
.chip[aria-pressed="true"] { color: var(--vm-bg); background: var(--vm-accent); border-color: var(--vm-accent); }

.stage-msg {
  position: absolute; inset: 0;
  display: grid; place-items: center; padding: 20px;
  text-align: center; font-size: calc(12.5px * var(--vm-fs)); color: var(--vm-dim);
}

/* ---- acte ---- */
.docs { display: flex; flex-direction: column; gap: calc(8px * var(--vm-sp)); }

.doc {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: calc(8px * var(--vm-sp));
  border-radius: calc(11px * var(--vm-r));
  cursor: pointer;
  text-align: left;
  color: inherit;
  font: inherit;
  background: color-mix(in srgb, var(--vm-bg) 60%, transparent);
  border: 1px solid var(--vm-line);
  border-left: 3px solid var(--vm-dim);
}
.doc:hover { background: color-mix(in srgb, var(--vm-accent) 8%, transparent); }
.doc[data-status="ok"] { border-left-color: var(--vm-ok); }
.doc[data-status="warning"] { border-left-color: var(--vm-warn); }
.doc[data-status="expired"] { border-left-color: var(--vm-bad); }

.ring { position: relative; width: 44px; height: 44px; }
.ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.ring circle { fill: none; stroke-width: 3.5; stroke-linecap: round; }
.ring .trk { stroke: var(--vm-line); }
.ring .val { stroke: var(--vm-dim); transition: stroke-dashoffset .5s ease; }
.doc[data-status="ok"] .ring .val { stroke: var(--vm-ok); }
.doc[data-status="warning"] .ring .val { stroke: var(--vm-warn); }
.doc[data-status="expired"] .ring .val { stroke: var(--vm-bad); }
.ring .num {
  position: absolute; inset: 0;
  display: grid; place-items: center;
  font: 600 calc(12px * var(--vm-fs))/1 var(--vm-mono);
}

.doc .meta { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.doc .name {
  font: calc(10px * var(--vm-fs))/1.2 var(--vm-mono);
  letter-spacing: .14em; text-transform: uppercase; color: var(--vm-dim);
}
.doc .main { font-size: calc(13.5px * var(--vm-fs)); font-weight: 650; }
.doc .sub { font-size: calc(11px * var(--vm-fs)); color: var(--vm-dim); }
.doc ha-icon { --mdc-icon-size: calc(18px * var(--vm-fs)); color: var(--vm-dim); }

/* ---- subsol ---- */
.foot {
  display: flex; justify-content: space-between; gap: 10px;
  padding-top: calc(10px * var(--vm-sp)); margin-top: calc(12px * var(--vm-sp));
  border-top: 1px solid var(--vm-line);
  font: calc(9px * var(--vm-fs))/1.4 var(--vm-mono);
  letter-spacing: .14em; text-transform: uppercase; color: var(--vm-dim);
}

.empty { padding: 26px 16px; text-align: center; color: var(--vm-dim); font-size: calc(13px * var(--vm-fs)); }
.empty code { color: var(--vm-accent); }

/* ---- meniul Themes si panoul Costuri ---- */
.themes, .costs, .files {
  margin-top: calc(12px * var(--vm-sp));
  padding: 14px;
  border-radius: calc(14px * var(--vm-r));
  background: var(--vm-panel);
  border: 1px solid var(--vm-accent);
  box-shadow: 0 0 calc(24px * var(--vm-glow)) color-mix(in srgb, var(--vm-accent) 18%, transparent);
  font-size: 13px;
}
.themes[hidden], .costs[hidden], .files[hidden] { display: none; }

/* ---- dosarul cu documente ---- */
.f-list { display: flex; flex-direction: column; gap: 8px; }
.f-slot {
  display: grid; grid-template-columns: 22px minmax(110px, 180px) 1fr auto;
  gap: 10px; align-items: center; padding: 8px 10px;
  border-radius: 10px; border: 1px solid var(--vm-line); background: var(--vm-soft);
}
.f-slot > ha-icon { --mdc-icon-size: 18px; color: var(--vm-dim); }
.f-slot .lbl { font-weight: 600; font-size: 13px; }
.f-chips { display: flex; flex-wrap: wrap; gap: 6px; min-width: 0; }
.f-chip {
  display: inline-flex; align-items: center; gap: 4px; max-width: 220px;
  padding: 4px 4px 4px 8px; border-radius: 8px; font-size: 12px;
  color: var(--vm-text); background: color-mix(in srgb, var(--vm-accent) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--vm-accent) 35%, transparent);
}
.f-chip .open {
  display: inline-flex; align-items: center; gap: 4px; min-width: 0; cursor: pointer;
  background: none; border: 0; color: inherit; font: inherit; padding: 0;
}
.f-chip .open span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.f-chip ha-icon { --mdc-icon-size: 15px; flex: none; }
.f-chip .del {
  border: 0; background: none; color: var(--vm-dim); cursor: pointer;
  font: 600 13px/1 var(--vm-mono); padding: 2px 5px; border-radius: 6px;
}
.f-chip .del[data-confirm="true"] { color: var(--vm-bad); }
.f-empty { font-size: 12px; color: var(--vm-dim); }
.f-slot .btn { padding: 7px 10px; font-size: 10px; }
.f-slot input[type="file"] { display: none; }
@media (max-width: 560px) {
  .f-slot { grid-template-columns: 22px 1fr auto; }
  .f-chips { grid-column: 1 / -1; }
}

.doc .clip {
  display: inline-flex; align-items: center; gap: 1px;
  font: 600 10px/1 var(--vm-mono); color: var(--vm-accent);
}
.doc .clip ha-icon { --mdc-icon-size: 13px; color: var(--vm-accent); }

.th-head {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  margin-bottom: 12px;
}
.th-head h2 {
  margin: 0; flex: 1 1 auto;
  font: 600 12px/1 var(--vm-mono); letter-spacing: .2em; text-transform: uppercase;
  color: var(--vm-accent);
}
.th-status { font-size: 11px; color: var(--vm-dim); }

.th-presets {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(104px, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}
.th-preset {
  display: flex; flex-direction: column; gap: 6px;
  padding: 8px; border-radius: 10px; cursor: pointer;
  text-align: left; font: inherit; font-size: 12px;
  color: var(--vm-text);
  background: var(--vm-soft);
  border: 1px solid var(--vm-line);
}
.th-preset[aria-pressed="true"] { border-color: var(--vm-accent); box-shadow: 0 0 0 1px var(--vm-accent) inset; }
.th-preset .dots { display: flex; gap: 4px; }
.th-preset .dots span {
  width: 14px; height: 14px; border-radius: 50%;
  border: 1px solid rgba(127,127,127,.4);
}

.th-groups {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}
.th-group {
  padding: 10px 12px; border-radius: 10px;
  background: var(--vm-soft);
  border: 1px solid var(--vm-line);
}
.th-group h4 {
  margin: 0 0 8px;
  font: 10px/1 var(--vm-mono); letter-spacing: .18em; text-transform: uppercase;
  color: var(--vm-dim);
}

.th-row {
  display: grid; grid-template-columns: 1fr auto;
  align-items: center; gap: 10px;
  padding: 5px 0;
}
.th-row label { color: var(--vm-text); }
.th-row .val { font: 11px/1 var(--vm-mono); color: var(--vm-dim); min-width: 42px; text-align: right; }
.th-row.range { grid-template-columns: 1fr minmax(90px, 140px) auto; }
.th-row input[type="range"] { width: 100%; accent-color: var(--vm-accent); }
.th-row input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--vm-accent); }
.th-row input[type="color"] {
  width: 42px; height: 26px; padding: 0; cursor: pointer;
  border: 1px solid var(--vm-line); border-radius: 6px; background: none;
}
.th-row input[type="color"]:disabled { opacity: .35; cursor: not-allowed; }
.th-row.image { grid-template-columns: 1fr; }
.th-bg {
  display: grid; grid-template-columns: 96px 1fr; gap: 10px; align-items: center;
}
.th-bg-preview {
  width: 96px; height: 60px; border-radius: 8px;
  border: 1px solid var(--vm-line);
  background: var(--vm-bg) center / cover no-repeat;
  display: grid; place-items: center;
  font-size: 10px; color: var(--vm-dim); text-align: center;
}
.th-bg-actions { display: flex; flex-wrap: wrap; gap: 6px; }
.th-bg-actions .btn { padding: 8px 10px; font-size: 10px; }
.th-bg-actions input[type="file"] { display: none; }
.th-bg-url {
  grid-column: 1 / -1;
  width: 100%; box-sizing: border-box;
  font: inherit; font-size: 12px; padding: 7px 9px;
  color: var(--vm-text); background: var(--vm-bg);
  border: 1px solid var(--vm-line); border-radius: 7px;
}
.th-row select {
  font: inherit; font-size: 12px; padding: 5px 8px;
  color: var(--vm-text); background: var(--vm-bg);
  border: 1px solid var(--vm-line); border-radius: 7px;
}

.th-actions {
  display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px;
  margin-top: 14px;
}
.btn {
  font: 600 11px/1 var(--vm-mono); letter-spacing: .14em; text-transform: uppercase;
  padding: 10px 14px; border-radius: 9px; cursor: pointer;
  color: var(--vm-text); background: var(--vm-soft);
  border: 1px solid var(--vm-line);
}
.btn:hover { border-color: var(--vm-accent); }
.btn.primary { color: var(--vm-bg); background: var(--vm-accent); border-color: var(--vm-accent); }
.btn.danger { margin-right: auto; color: var(--vm-bad); }
.btn:disabled { opacity: .5; cursor: progress; }

/* ---- panoul Costuri ---- */
.btn.c-export { padding: 7px 10px; font-size: 10px; }
.c-year {
  font: inherit; font-size: 12px; padding: 5px 8px;
  color: var(--vm-text); background: var(--vm-bg);
  border: 1px solid var(--vm-line); border-radius: 7px;
}
.c-tiles {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px; margin-bottom: 12px;
}
.c-tile {
  padding: 10px 12px; border-radius: 10px;
  background: var(--vm-soft); border: 1px solid var(--vm-line);
}
.c-tile .k {
  font: 10px/1.2 var(--vm-mono); letter-spacing: .14em; text-transform: uppercase;
  color: var(--vm-dim);
}
.c-tile .v { font-size: calc(20px * var(--vm-fs)); font-weight: 700; margin-top: 4px; }
.c-bars { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.c-bar {
  display: grid; grid-template-columns: 20px minmax(80px, 140px) 1fr auto;
  gap: 8px; align-items: center; font-size: 12px;
}
.c-bar ha-icon { --mdc-icon-size: 16px; color: var(--vm-dim); }
.c-bar .track {
  display: block; height: 8px; border-radius: 4px; overflow: hidden;
  background: color-mix(in srgb, var(--vm-line) 50%, transparent);
}
.c-bar .fill {
  display: block; height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, var(--vm-accent), var(--vm-accent-2));
}
.c-bar .amt { font-weight: 600; white-space: nowrap; }
.c-form {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px; align-items: end; padding: 10px; margin-bottom: 12px;
  border-radius: 10px; background: var(--vm-soft); border: 1px solid var(--vm-line);
}
.c-form label { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.c-form label > span {
  font: 10px/1.2 var(--vm-mono); letter-spacing: .12em; text-transform: uppercase;
  color: var(--vm-dim);
}
.c-form input, .c-form select {
  font: inherit; font-size: 13px;
  min-width: 0; padding: 7px 8px;
  color: var(--vm-text); background: var(--vm-bg);
  border: 1px solid var(--vm-line); border-radius: 7px;
}
.c-form .c-note { grid-column: span 2; }
.c-form .c-fuel[hidden] { display: none; }
.c-form label.c-check { flex-direction: row; align-items: center; gap: 8px; padding-bottom: 8px; }
.c-form label.c-check input { width: 18px; height: 18px; accent-color: var(--vm-accent); }
.c-list { display: flex; flex-direction: column; gap: 6px; max-height: 360px; overflow: auto; }
.c-row {
  display: grid; grid-template-columns: 22px minmax(0, 1fr) auto auto;
  gap: 10px; align-items: center; padding: 8px 10px; font-size: 13px;
  border-radius: 9px; border: 1px solid var(--vm-line);
  background: color-mix(in srgb, var(--vm-bg) 55%, transparent);
}
.c-row ha-icon { --mdc-icon-size: 18px; color: var(--vm-dim); }
.c-row .main { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.c-row .t1 { font-weight: 600; }
.c-row .t2 {
  font-size: 11px; color: var(--vm-dim);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.c-row .amt { font-weight: 700; white-space: nowrap; }
.btn.c-del { padding: 6px 8px; font-size: 10px; }
.btn.c-del[data-confirm="true"] { color: var(--vm-bad); border-color: var(--vm-bad); }
.c-empty { color: var(--vm-dim); font-size: 12px; padding: 8px 2px; }
@media (max-width: 480px) {
  .c-form .c-note { grid-column: 1 / -1; }
  .c-bar { grid-template-columns: 18px minmax(70px, 100px) 1fr auto; }
}

/* ---- mod compact ---- */
.urgent { display: none; }
.open-btn { display: none; }

.vm.compact .specs,
.vm.compact .docs,
.vm.compact .foot,
.vm.compact .themes,
.vm.compact .themes-btn,
.vm.compact .costs,
.vm.compact .costs-btn,
.vm.compact .files,
.vm.compact .files-btn,
.vm.compact .settings,
.vm.compact .hud,
.vm.compact .bracket,
.vm.compact .stage-actions { display: none !important; }

.vm.compact .top { padding-bottom: calc(10px * var(--vm-sp)); gap: 10px; }
.vm.compact .top[data-nav="true"] .brand { cursor: pointer; }
.vm.compact .top[data-nav="true"] .open-btn { display: inline-flex; }
/* numele ocupa spatiul ramas (se taie cu "…"), ca antetul sa ramana pe un rand */
.vm.compact .brand { flex: 1 1 0; min-width: 0; }
.vm.compact .top-spacer { display: none; }
.vm.compact .titles .s { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vm.compact .plate { font-size: calc(11px * var(--vm-fs)); padding: 6px 8px; }
.vm.compact .picker { order: 9; flex: 1 1 100%; min-width: 0; }

.vm.compact .body {
  grid-template-columns: minmax(120px, 0.9fr) minmax(0, 1.4fr);
  gap: calc(10px * var(--vm-sp));
  padding-top: calc(10px * var(--vm-sp));
}
.vm.compact .stage { order: 0; min-height: 132px; }
.vm.compact .urgent {
  display: flex; flex-direction: column; gap: calc(6px * var(--vm-sp));
  padding: calc(8px * var(--vm-sp));
}

.u-item {
  display: grid; grid-template-columns: 10px minmax(0, 1fr); align-items: center; gap: 8px;
  width: 100%; padding: calc(7px * var(--vm-sp)) 8px;
  border-radius: calc(9px * var(--vm-r)); cursor: pointer;
  text-align: left; color: inherit; font: inherit;
  background: color-mix(in srgb, var(--vm-bg) 55%, transparent);
  border: 1px solid var(--vm-line);
}
.u-item:hover { background: color-mix(in srgb, var(--vm-accent) 8%, transparent); }
.u-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--vm-dim); }
.u-item[data-status="ok"] .u-dot { background: var(--vm-ok); }
.u-item[data-status="warning"] .u-dot { background: var(--vm-warn); box-shadow: 0 0 calc(8px * var(--vm-glow)) var(--vm-warn); }
.u-item[data-status="expired"] .u-dot { background: var(--vm-bad); box-shadow: 0 0 calc(8px * var(--vm-glow)) var(--vm-bad); }
.u-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.u-name {
  font: calc(9.5px * var(--vm-fs))/1.2 var(--vm-mono);
  letter-spacing: .12em; text-transform: uppercase; color: var(--vm-dim);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.u-val {
  font-size: calc(13px * var(--vm-fs)); font-weight: 650;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.u-item[data-status="warning"] .u-val { color: var(--vm-warn); }
.u-item[data-status="expired"] .u-val { color: var(--vm-bad); }
.u-all-ok {
  display: flex; align-items: center; gap: 8px;
  font-size: calc(12px * var(--vm-fs)); color: var(--vm-ok);
}
.u-all-ok ha-icon { --mdc-icon-size: 18px; }

/* ---- responsive ---- */
@media (max-width: 880px) {
  .body { grid-template-columns: 1fr; }
  .stage { order: -1; min-height: calc(var(--vm-stage-h) * 0.8); }
}
@media (max-width: 880px) {
  .vm.compact .body { grid-template-columns: minmax(110px, 0.9fr) minmax(0, 1.4fr); }
  .vm.compact .stage { order: 0; min-height: 132px; }
}
@media (max-width: 340px) {
  .vm.compact .body { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .th-row.range { grid-template-columns: 1fr auto; }
  .th-row.range input[type="range"] { grid-column: 1 / -1; grid-row: 2; }
  .btn.danger { margin-right: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .led[data-status="expired"] { animation: none; }
}
`;

/* ------------------------------------------------------------------ */
/* Cardul                                                             */
/* ------------------------------------------------------------------ */

class VehicleManagerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._selected = null;
    this._signature = null;
    this._vehicleKeys = null;
    this._photoMode = false;
    this._built = false;
    this._savedTheme = null;
    this._themeDraft = null;
    this._themeUnsub = null;
  }

  static getConfigElement() {
    return document.createElement("vehicle-manager-card-editor");
  }

  static getStubConfig() {
    return { type: "custom:vehicle-manager-card", auto_rotate: true };
  }

  setConfig(config) {
    this._config = {
      auto_rotate: true,
      rotate_speed: 0.35,
      show_photo_toggle: true,
      show_theme_button: true,
      show_costs_button: true,
      show_files_button: true,
      compact: false,
      compact_items: 3,
      three_src: DEFAULT_THREE,
      ...config,
    };
    this._signature = null;
    if (this._built) {
      this._el.themeBtn.hidden = this._config.show_theme_button === false;
      this._el.costsBtn.hidden = this._config.show_costs_button === false;
      this._el.filesBtn.hidden = this._config.show_files_button === false;
      this._applyLayout();
      this._applyTheme();
      this._viewer?.setOptions({
        autoRotate: this._config.auto_rotate !== false,
        rotateSpeed: Number(this._config.rotate_speed) || 0.35,
      });
      this._update();
    }
  }

  getCardSize() {
    return this._config?.compact ? 4 : 14;
  }

  set hass(hass) {
    setLanguage(hass);
    this._hass = hass;
    if (!this._built) this._build();
    this._subscribeTheme();
    this._update();
  }

  connectedCallback() {
    if (this._hass && !this._built) this._build();
    if (this._hass) this._subscribeTheme();
    /* Abia acum se pot citi culorile calculate (ex. tema Home Assistant). */
    if (this._built) this._applyTheme();
  }

  disconnectedCallback() {
    this._viewer?.dispose();
    this._viewer = null;
    this._built = false;
    this._signature = null;
    this._themeDraft = null;
    this._unsubscribeTheme();
    this._unsubscribeCosts();
    this._costs = null;
    this._unsubscribeFiles();
    this._files = null;
  }

  /* --------------------------------------------------------------- */
  /* Descoperirea vehiculelor                                         */
  /* --------------------------------------------------------------- */
  _vehicles() {
    const hass = this._hass;
    if (!hass) return [];

    const explicit = this._config.vehicles;
    let ids;
    if (Array.isArray(explicit) && explicit.length) {
      ids = explicit.filter((id) => hass.states[id]);
    } else {
      ids = Object.keys(hass.states).filter(
        (id) => id.startsWith("sensor.") && hass.states[id].attributes?.vm_card === true
      );
    }

    return ids
      .map((id) => {
        const state = hass.states[id];
        return {
          id,
          name:
            state.attributes.vehicle_name ||
            state.attributes.friendly_name ||
            id,
          state,
        };
      })
      .sort((a, b) => a.name.localeCompare(b.name, "ro"));
  }

  _storageKey() {
    return "vehicle-manager-card.selected";
  }

  _readStoredSelection() {
    try {
      return window.localStorage.getItem(this._storageKey());
    } catch (err) {
      return null;
    }
  }

  _storeSelection(entityId) {
    try {
      window.localStorage.setItem(this._storageKey(), entityId);
    } catch (err) {
      /* modul privat sau storage blocat: selectia ramane doar in memorie */
    }
  }

  /* --------------------------------------------------------------- */
  /* Construirea DOM-ului                                             */
  /* --------------------------------------------------------------- */
  _build() {
    const style = document.createElement("style");
    style.textContent = STYLES;

    const card = document.createElement("ha-card");
    card.innerHTML = `
      <div class="bg-layer card-bg" hidden></div>
      <div class="vm">
        <header class="top">
          <div class="brand">
            <span class="led" data-status="unknown"></span>
            <span class="titles">
              <span class="t"></span>
              <span class="s"></span>
            </span>
          </div>
          <span class="top-spacer"></span>
          <div class="picker"><select aria-label="${t("Selecteaza vehiculul")}"></select></div>
          <span class="plate"></span>
          <button class="icon-btn costs-btn" title="${t("Costuri")}" aria-expanded="false">
            <ha-icon icon="mdi:cash-multiple"></ha-icon>
            <span>${t("Costuri")}</span>
          </button>
          <button class="icon-btn files-btn" title="${t("Dosarul masinii: polite, talon...")}" aria-expanded="false">
            <ha-icon icon="mdi:folder-file-outline"></ha-icon>
            <span>${t("Dosar")}</span>
          </button>
          <button class="icon-btn themes-btn" title="Themes" aria-expanded="false">
            <ha-icon icon="mdi:palette-outline"></ha-icon>
            <span>Themes</span>
          </button>
          <button class="icon-btn settings" title="${t("Editeaza vehiculele")}">
            <ha-icon icon="mdi:cog-outline"></ha-icon>
          </button>
          <button class="icon-btn open-btn" title="${t("Deschide pagina vehiculului")}">
            <ha-icon icon="mdi:chevron-right"></ha-icon>
          </button>
        </header>

        <section class="themes" hidden></section>
        <section class="costs" hidden></section>
        <section class="files" hidden></section>

        <div class="body">
          <section class="panel specs">
            <h3>${t("Caracteristici")}</h3>
            <div class="spec-list"></div>
          </section>

          <section class="stage">
            <div class="bg-layer stage-bg" hidden></div>
            <canvas></canvas>
            <img class="photo" alt="" hidden />
            <div class="stage-msg" hidden></div>
            <span class="bracket tl"></span>
            <span class="bracket tr"></span>
            <span class="bracket bl"></span>
            <span class="bracket br"></span>
            <div class="hud"></div>
            <div class="stage-actions">
              <button class="chip view-3d" aria-pressed="true">3D</button>
              <button class="chip view-photo" aria-pressed="false">${t("Poza")}</button>
            </div>
          </section>

          <section class="panel urgent"></section>

          <section class="panel docs">
            <h3>${t("Acte si scadente")}</h3>
            <div class="doc-list"></div>
          </section>
        </div>

        <footer class="foot">
          <span class="foot-left"></span>
          <span class="foot-right"></span>
        </footer>
      </div>
      <div class="empty" hidden></div>
    `;

    this.shadowRoot.replaceChildren(style, card);

    this._el = {
      card,
      root: card.querySelector(".vm"),
      empty: card.querySelector(".empty"),
      led: card.querySelector(".led"),
      title: card.querySelector(".titles .t"),
      subtitle: card.querySelector(".titles .s"),
      select: card.querySelector("select"),
      plate: card.querySelector(".plate"),
      settings: card.querySelector(".settings"),
      top: card.querySelector(".top"),
      brand: card.querySelector(".brand"),
      openBtn: card.querySelector(".open-btn"),
      urgent: card.querySelector(".urgent"),
      themeBtn: card.querySelector(".themes-btn"),
      themes: card.querySelector(".themes"),
      costs: card.querySelector(".costs"),
      costsBtn: card.querySelector(".costs-btn"),
      files: card.querySelector(".files"),
      filesBtn: card.querySelector(".files-btn"),
      cardBg: card.querySelector(".card-bg"),
      stageBg: card.querySelector(".stage-bg"),
      specList: card.querySelector(".spec-list"),
      docList: card.querySelector(".doc-list"),
      stage: card.querySelector(".stage"),
      canvas: card.querySelector("canvas"),
      photo: card.querySelector(".photo"),
      stageMsg: card.querySelector(".stage-msg"),
      hud: card.querySelector(".hud"),
      view3d: card.querySelector(".view-3d"),
      viewPhoto: card.querySelector(".view-photo"),
      footLeft: card.querySelector(".foot-left"),
      footRight: card.querySelector(".foot-right"),
    };

    this._el.select.addEventListener("change", (event) => {
      this._selected = event.target.value;
      this._storeSelection(this._selected);
      this._signature = null;
      this._update();
    });

    this._el.settings.addEventListener("click", () =>
      navigate("/config/integrations/integration/vehicle_manager")
    );

    this._el.view3d.addEventListener("click", () => this._setPhotoMode(false));
    this._el.viewPhoto.addEventListener("click", () => this._setPhotoMode(true));

    /* in modul compact, numele si sageata duc la pagina cu cardul complet */
    const openPage = () => {
      if (this._config.compact && this._config.navigation_path) {
        navigate(this._config.navigation_path);
      }
    };
    this._el.brand.addEventListener("click", openPage);
    this._el.openBtn.addEventListener("click", openPage);
    this._applyLayout();

    this._el.filesBtn.hidden = this._config.show_files_button === false;
    this._el.filesBtn.addEventListener("click", () =>
      this._el.files.hidden ? this._openFiles() : this._closeFiles()
    );

    this._el.costsBtn.hidden = this._config.show_costs_button === false;
    this._el.costsBtn.addEventListener("click", () =>
      this._el.costs.hidden ? this._openCosts() : this._closeCosts()
    );

    this._el.themeBtn.hidden = this._config.show_theme_button === false;
    this._el.themeBtn.addEventListener("click", () =>
      this._el.themes.hidden ? this._openThemes() : this._closeThemes()
    );

    this._applyTheme();
    this._built = true;
    this._startViewer();
  }

  _applyLayout() {
    const compact = Boolean(this._config.compact);
    this._el.root.classList.toggle("compact", compact);
    this._el.top.dataset.nav = String(compact && Boolean(this._config.navigation_path));
    if (compact && !this._el.themes.hidden) this._closeThemes();
    if (compact && this._costs) this._closeCosts();
    if (compact && !this._el.files.hidden) this._closeFiles();
  }

  /* --------------------------------------------------------------- */
  /* Dosar (documente scanate)                                        */
  /* --------------------------------------------------------------- */
  _subscribeFiles() {
    this._unsubscribeFiles();
    const entryId = this._entryId;
    const connection = this._hass?.connection;
    this._files = undefined;
    if (!entryId || !connection) return;

    this._filesEntry = entryId;
    this._filesUnsub = connection
      .subscribeMessage(
        (message) => {
          if (this._filesEntry !== entryId) return;
          this._files = message.files || [];
          /* agrafele din lista de acte + panoul, daca e deschis */
          this._signature = null;
          this._update();
          if (!this._el.files.hidden) this._renderFiles();
        },
        { type: FILES_WS_SUBSCRIBE, entry_id: entryId }
      )
      .catch(() => {
        /* integrare veche: fara dosar */
        this._files = null;
        if (!this._el.files.hidden) this._renderFiles();
        return null;
      });
  }

  _unsubscribeFiles() {
    const pending = this._filesUnsub;
    this._filesUnsub = null;
    this._filesEntry = null;
    pending?.then((unsub) => unsub?.()).catch(() => {});
  }

  _clipBadge(slot) {
    const count = (this._files || []).filter((f) => f.slot === slot).length;
    return count
      ? ` <span class="clip" title="${t("{n} fisier(e) in dosar", { n: count })}"><ha-icon icon="mdi:paperclip"></ha-icon>${count}</span>`
      : "";
  }

  _openFiles() {
    if (!this._el.themes.hidden) this._closeThemes();
    if (this._costs) this._closeCosts();
    this._el.filesBtn.setAttribute("aria-expanded", "true");
    this._el.files.hidden = false;
    this._renderFiles();
  }

  _closeFiles() {
    this._el.filesBtn.setAttribute("aria-expanded", "false");
    this._el.files.hidden = true;
    this._el.files.replaceChildren();
  }

  _setFilesStatus(text) {
    const status = this._el.files.querySelector(".f-status");
    if (status) status.textContent = text;
  }

  _renderFiles() {
    const root = this._el.files;
    const previous = root.querySelector(".f-status")?.textContent;
    const docs = this._visibleDocuments(this._documents || {});
    const slots = [...docs.map((d) => [d.key, t(d.label), d.icon]), [FILES_GENERAL[0], t(FILES_GENERAL[1]), FILES_GENERAL[2]]];

    const head = document.createElement("div");
    head.className = "th-head";
    head.innerHTML = `<h2>${t("Dosar")}</h2><span class="th-status f-status"></span>`;
    head.querySelector(".f-status").textContent =
      previous ||
      (this._files === null
        ? t("Dosarul nu poate fi incarcat (actualizeaza integrarea si restarteaza Home Assistant).")
        : this._files === undefined
        ? t("Se incarca...")
        : t("Poze sau PDF-uri cu actele masinii. Se deschid doar din Home Assistant."));

    const list = document.createElement("div");
    list.className = "f-list";
    for (const [slot, label, icon] of slots) {
      const row = document.createElement("div");
      row.className = "f-slot";
      row.innerHTML = `<ha-icon></ha-icon><span class="lbl"></span><span class="f-chips"></span>`;
      row.querySelector("ha-icon").setAttribute("icon", icon);
      row.querySelector(".lbl").textContent = label;

      const chips = row.querySelector(".f-chips");
      const items = (this._files || []).filter((f) => f.slot === slot);
      if (!items.length) {
        const empty = document.createElement("span");
        empty.className = "f-empty";
        empty.textContent = t("niciun fisier");
        chips.append(empty);
      }
      for (const item of items) chips.append(this._fileChip(item));

      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*,application/pdf";
      const add = this._themeButton(t("Adauga"), "btn", () => input.click());
      input.addEventListener("change", async () => {
        const file = input.files?.[0];
        if (!file) return;
        add.disabled = true;
        await this._uploadFile(slot, file);
        add.disabled = false;
        input.value = "";
      });
      row.append(add, input);
      list.append(row);
    }
    root.replaceChildren(head, list);
  }

  _fileChip(item) {
    const chip = document.createElement("span");
    chip.className = "f-chip";
    chip.innerHTML = `<button class="open" type="button"><ha-icon></ha-icon><span></span></button>
      <button class="del" type="button" title="${t("Sterge")}">×</button>`;
    chip.querySelector("ha-icon").setAttribute(
      "icon",
      item.mime === "application/pdf" ? "mdi:file-pdf-box" : "mdi:file-image-outline"
    );
    chip.querySelector(".open span").textContent = item.name;
    chip.querySelector(".open").title = `${item.name} · ${formatNumber(Math.round(item.size / 1024))} KB`;
    chip.querySelector(".open").addEventListener("click", () => this._openFile(item));
    const del = chip.querySelector(".del");
    del.addEventListener("click", async () => {
      /* primul click cere confirmare, al doilea sterge */
      if (del.dataset.confirm !== "true") {
        del.dataset.confirm = "true";
        del.textContent = t("sterge?");
        setTimeout(() => {
          if (del.isConnected) {
            del.dataset.confirm = "false";
            del.textContent = "×";
          }
        }, 3000);
        return;
      }
      try {
        await this._hass.callWS({ type: FILES_WS_DELETE, file_id: item.id });
      } catch (err) {
        this._setFilesStatus(t("Fisierul nu a putut fi sters: {err}", { err: err?.message || err?.code || err }));
      }
    });
    return chip;
  }

  async _openFile(item) {
    try {
      const signed = await this._hass.callWS({
        type: "auth/sign_path",
        path: `${FILES_URL}/${this._filesEntry}/${item.id}`,
        expires: 60,
      });
      window.open(this._hass.hassUrl ? this._hass.hassUrl(signed.path) : signed.path, "_blank");
    } catch (err) {
      this._setFilesStatus(t("Fisierul nu a putut fi deschis: {err}", { err: err?.message || err?.code || err }));
    }
  }

  async _uploadFile(slot, file) {
    this._setFilesStatus(t("Se incarca..."));
    try {
      const prepared = file.type.startsWith("image/") ? await shrinkImage(file) : file;
      const form = new FormData();
      form.append("file", prepared, file.name || "document");
      const url = `${FILES_URL}/${this._filesEntry}/${slot}`;
      const response = this._hass.fetchWithAuth
        ? await this._hass.fetchWithAuth(url, { method: "POST", body: form })
        : await fetch(url, {
            method: "POST",
            body: form,
            headers: { Authorization: `Bearer ${this._hass.auth?.data?.access_token}` },
          });
      if (response.status === 404 && !this._files) {
        throw new Error(t("serverul ruleaza o versiune veche a integrarii"));
      }
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.message || `HTTP ${response.status}`);
      this._setFilesStatus(t("Incarcat: {name}.", { name: body.name }));
    } catch (err) {
      this._setFilesStatus(t("Fisierul nu a putut fi incarcat: {err}", { err: err?.message || err }));
    }
  }

  /* --------------------------------------------------------------- */
  /* Costuri                                                          */
  /* --------------------------------------------------------------- */
  _openCosts() {
    if (!this._el.themes.hidden) this._closeThemes();
    if (!this._el.files.hidden) this._closeFiles();
    this._costs = {
      expenses: [],
      currency: null,
      year: String(new Date().getFullYear()),
      loaded: false,
    };
    this._el.costsBtn.setAttribute("aria-expanded", "true");
    this._el.costs.hidden = false;
    this._buildCosts();
    this._subscribeCosts();
  }

  _closeCosts() {
    this._unsubscribeCosts();
    this._costs = null;
    this._el.costsBtn.setAttribute("aria-expanded", "false");
    this._el.costs.hidden = true;
    this._el.costs.replaceChildren();
  }

  _subscribeCosts() {
    this._unsubscribeCosts();
    const entryId = this._entryId;
    const connection = this._hass?.connection;
    if (!entryId || !connection) return;

    this._costsEntry = entryId;
    this._costsUnsub = connection
      .subscribeMessage(
        (message) => {
          if (!this._costs || this._costsEntry !== entryId) return;
          this._costs.expenses = message.expenses || [];
          this._costs.currency = message.currency || null;
          this._costs.fuel = message.fuel || null;
          this._costs.loaded = true;
          this._renderCostsData();
        },
        { type: EXPENSES_WS_SUBSCRIBE, entry_id: entryId }
      )
      .catch((err) => {
        this._setCostsStatus(
          err?.code === "unknown_command"
            ? t("Serverul ruleaza o versiune veche a integrarii (fara Costuri). Actualizeaza integrarea si restarteaza Home Assistant.")
            : t("Costurile nu pot fi incarcate: {err}", { err: err?.message || err?.code || err })
        );
        return null;
      });
  }

  _unsubscribeCosts() {
    const pending = this._costsUnsub;
    this._costsUnsub = null;
    this._costsEntry = null;
    pending?.then((unsub) => unsub?.()).catch(() => {});
  }

  _setCostsStatus(text) {
    const status = this._el.costs.querySelector(".c-status");
    if (status) status.textContent = text;
  }

  _money(value) {
    const currency = this._costs?.currency || "RON";
    const language = this._hass?.locale?.language || "ro-RO";
    try {
      return new Intl.NumberFormat(language, { style: "currency", currency }).format(value);
    } catch (err) {
      return `${formatNumber(Math.round(value * 100) / 100)} ${currency}`;
    }
  }

  /* Scheletul panoului; formularul ramane intact cand se schimba datele. */
  _buildCosts() {
    const root = this._el.costs;
    root.innerHTML = `
      <div class="th-head">
        <h2>${t("Costuri")}</h2>
        <select class="c-year" aria-label="${t("Perioada")}"></select>
        <button class="btn c-export" type="button" title="${t("Descarca perioada aleasa ca fisier CSV (Excel)")}">${t("Export CSV")}</button>
        <span class="th-status c-status">${t("Se incarca...")}</span>
      </div>
      <div class="c-tiles"></div>
      <div class="c-bars"></div>
      <form class="c-form">
        <label><span>${t("Data")}</span><input type="date" name="date" required></label>
        <label><span>${t("Categorie")}</span><select name="category"></select></label>
        <label><span>${t("Suma")}</span><input type="number" name="amount" min="0" step="0.01" inputmode="decimal" required></label>
        <label><span>${t("Kilometraj")}</span><input type="number" name="mileage" min="0" step="1" inputmode="numeric"></label>
        <label class="c-fuel" hidden><span class="c-qty-label">${t("Cantitate")}</span><input type="number" name="quantity" min="0" step="0.01" inputmode="decimal"></label>
        <label class="c-fuel c-check" hidden><input type="checkbox" name="full_tank" checked><span>${t("Plin complet")}</span></label>
        <label class="c-note"><span>${t("Nota")}</span><input type="text" name="note" maxlength="200" placeholder="${t("optional")}"></label>
        <button class="btn primary" type="submit">${t("Adauga")}</button>
      </form>
      <div class="c-list"></div>
    `;

    const form = root.querySelector(".c-form");
    const category = form.elements.category;
    for (const [key, [label]] of Object.entries(EXPENSE_CATEGORIES)) {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = t(label);
      category.append(option);
    }
    form.elements.date.value = todayIso();
    form.querySelector(".c-qty-label").textContent = this._electric ? t("Cantitate (kWh)") : t("Cantitate (l)");
    /* campurile de alimentare apar doar la categoria Combustibil */
    const toggleFuel = () => {
      const fuel = category.value === "combustibil";
      form.querySelectorAll(".c-fuel").forEach((el) => (el.hidden = !fuel));
    };
    category.addEventListener("change", toggleFuel);
    toggleFuel();
    if (this._mileage !== null && this._mileage !== undefined) {
      form.elements.mileage.value = this._mileage;
    }
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      this._addExpense(form);
    });

    root.querySelector(".c-export").addEventListener("click", () => this._exportCosts());

    root.querySelector(".c-year").addEventListener("change", (event) => {
      this._costs.year = event.target.value;
      this._renderCostsData();
    });

    this._renderCostsData();
  }

  async _addExpense(form) {
    const amount = Number(form.elements.amount.value);
    if (!(amount > 0)) {
      this._setCostsStatus(t("Introdu o suma mai mare decat zero."));
      return;
    }
    const message = {
      type: EXPENSES_WS_ADD,
      entry_id: this._costsEntry,
      category: form.elements.category.value,
      amount,
      date: form.elements.date.value || todayIso(),
    };
    if (form.elements.mileage.value !== "") message.mileage = Number(form.elements.mileage.value);
    const note = form.elements.note.value.trim();
    if (note) message.note = note;
    if (message.category === "combustibil" && form.elements.quantity.value !== "") {
      message.quantity = Number(form.elements.quantity.value);
      message.full_tank = form.elements.full_tank.checked;
    }
    const noMileageForFuel = message.quantity !== undefined && message.mileage === undefined;

    const submit = form.querySelector("button[type=submit]");
    submit.disabled = true;
    try {
      await this._hass.callWS(message);
      form.elements.amount.value = "";
      form.elements.note.value = "";
      form.elements.quantity.value = "";
      form.elements.full_tank.checked = true;
      this._setCostsStatus(
        t("Adaugat: {what}, {amount}.", { what: t(EXPENSE_CATEGORIES[message.category][0]), amount: this._money(amount) }) +
          (noMileageForFuel ? " " + t("Fara kilometraj, alimentarea nu intra in calculul consumului.") : "")
      );
    } catch (err) {
      this._setCostsStatus(t("Cheltuiala nu a putut fi salvata: {err}", { err: err?.message || err?.code || err }));
    } finally {
      submit.disabled = false;
    }
  }

  /*
   * Fisierul CSV vine de la server; un link semnat (valabil un minut) il face
   * descarcabil si din aplicatia mobila, fara antetul de autentificare.
   */
  async _exportCosts() {
    if (!this._costsEntry) return;
    const period = this._costs?.year || "all";
    try {
      const signed = await this._hass.callWS({
        type: "auth/sign_path",
        path: `/api/vehicle_manager/expenses/${this._costsEntry}/${period}.csv`,
        expires: 60,
      });
      const url = this._hass.hassUrl ? this._hass.hassUrl(signed.path) : signed.path;
      window.open(url, "_blank");
    } catch (err) {
      this._setCostsStatus(t("Exportul nu a reusit: {err}", { err: err?.message || err?.code || err }));
    }
  }

  async _deleteExpense(button, expense) {
    /* primul click cere confirmare, al doilea sterge */
    if (button.dataset.confirm !== "true") {
      button.dataset.confirm = "true";
      button.textContent = t("Sigur?");
      setTimeout(() => {
        if (button.isConnected) {
          button.dataset.confirm = "false";
          button.textContent = t("Sterge");
        }
      }, 3000);
      return;
    }
    button.disabled = true;
    try {
      await this._hass.callWS({ type: EXPENSES_WS_DELETE, expense_id: expense.id });
    } catch (err) {
      button.disabled = false;
      this._setCostsStatus(t("Cheltuiala nu a putut fi stearsa: {err}", { err: err?.message || err?.code || err }));
    }
  }

  _renderCostsData() {
    const costs = this._costs;
    const root = this._el.costs;
    if (!costs || root.hidden) return;
    const all = costs.expenses;
    const language = this._hass?.locale?.language || "ro-RO";

    /* perioada: anii cu cheltuieli + anul curent, sau tot istoricul */
    const yearSelect = root.querySelector(".c-year");
    const years = new Set([String(new Date().getFullYear())]);
    for (const item of all) years.add(item.date.slice(0, 4));
    const choices = [...[...years].sort().reverse().map((y) => [y, t("Anul {year}", { year: y })]), ["all", t("Toti anii")]];
    yearSelect.replaceChildren(
      ...choices.map(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        return option;
      })
    );
    if (!choices.some(([value]) => value === costs.year)) costs.year = choices[0][0];
    yearSelect.value = costs.year;

    const items = costs.year === "all" ? all : all.filter((e) => e.date.startsWith(`${costs.year}-`));
    const sum = (list) => list.reduce((total, e) => total + e.amount, 0);

    /* rezumat */
    const tiles = costs.year === "all"
      ? [
          [t("Total"), this._money(sum(all))],
          [t("Medie pe an"), this._money(sum(all) / Math.max(1, new Set(all.map((e) => e.date.slice(0, 4))).size))],
          [t("Cheltuieli"), String(all.length)],
        ]
      : [
          [t("Anul {year}", { year: costs.year }), this._money(sum(items))],
          [t("Total general"), this._money(sum(all))],
          [t("Cheltuieli in an"), String(items.length)],
        ];
    /* consumul, din intervalele "plin la plin" calculate pe server */
    const segments = (costs.fuel?.segments || []).filter(
      (seg) => costs.year === "all" || seg.date.startsWith(`${costs.year}-`)
    );
    const fuelKm = segments.reduce((total, seg) => total + seg.km, 0);
    const unit = this._electric ? "kWh" : "l";
    if (fuelKm > 0) {
      const quantity = segments.reduce((total, seg) => total + seg.quantity, 0);
      const fuelCost = segments.reduce((total, seg) => total + seg.cost, 0);
      tiles.push(
        [t("Consum mediu"), `${formatNumber(Math.round((quantity / fuelKm) * 1000) / 10)} ${unit}/100 km`],
        [t("Combustibil pe km"), this._money(fuelCost / fuelKm)],
        [t("Km masurati"), `${formatNumber(fuelKm)} km`]
      );
    }
    const consumptionById = new Map(segments.map((seg) => [seg.id, seg.consumption]));

    root.querySelector(".c-tiles").replaceChildren(
      ...tiles.map(([key, value]) => {
        const tile = document.createElement("div");
        tile.className = "c-tile";
        tile.innerHTML = `<div class="k"></div><div class="v"></div>`;
        tile.querySelector(".k").textContent = key;
        tile.querySelector(".v").textContent = value;
        return tile;
      })
    );

    /* pe categorii */
    const byCategory = new Map();
    for (const e of items) byCategory.set(e.category, (byCategory.get(e.category) || 0) + e.amount);
    const ranked = [...byCategory.entries()].sort((a, b) => b[1] - a[1]);
    const max = ranked.length ? ranked[0][1] : 0;
    root.querySelector(".c-bars").replaceChildren(
      ...ranked.map(([key, amount]) => {
        const [rawLabel, icon] = EXPENSE_CATEGORIES[key] || [key, "mdi:cash"];
        const label = t(rawLabel);
        const row = document.createElement("div");
        row.className = "c-bar";
        row.innerHTML = `<ha-icon></ha-icon><span class="lbl"></span>
          <span class="track"><span class="fill"></span></span><span class="amt"></span>`;
        row.querySelector("ha-icon").setAttribute("icon", icon);
        row.querySelector(".lbl").textContent = label;
        row.querySelector(".fill").style.width = `${max ? Math.max(2, (amount / max) * 100) : 0}%`;
        row.querySelector(".amt").textContent = this._money(amount);
        return row;
      })
    );

    /* lista */
    const list = root.querySelector(".c-list");
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "c-empty";
      empty.textContent = costs.loaded
        ? t("Nicio cheltuiala in perioada aleasa. Adaug-o din formularul de mai sus.")
        : t("Se incarca...");
      list.replaceChildren(empty);
    } else {
      list.replaceChildren(
        ...items.map((expense) => {
          const [rawLabel, icon] = EXPENSE_CATEGORIES[expense.category] || [expense.category, "mdi:cash"];
          const label = t(rawLabel);
          const row = document.createElement("div");
          row.className = "c-row";
          row.innerHTML = `<ha-icon></ha-icon>
            <span class="main"><span class="t1"></span><span class="t2"></span></span>
            <span class="amt"></span>`;
          row.querySelector("ha-icon").setAttribute("icon", icon);
          row.querySelector(".t1").textContent = label;
          row.querySelector(".t2").textContent = [
            formatDate(expense.date, language),
            expense.mileage !== null && expense.mileage !== undefined
              ? `${formatNumber(expense.mileage)} km`
              : null,
            expense.quantity
              ? `${formatNumber(expense.quantity)} ${unit}${expense.full_tank === false ? " (partial)" : ""}`
              : null,
            consumptionById.has(expense.id)
              ? `${formatNumber(consumptionById.get(expense.id))} ${unit}/100 km`
              : null,
            expense.note || null,
          ]
            .filter(Boolean)
            .join(" · ");
          row.querySelector(".amt").textContent = this._money(expense.amount);
          const remove = this._themeButton(t("Sterge"), "btn c-del", () =>
            this._deleteExpense(remove, expense)
          );
          remove.title = t("Sterge (id {id})", { id: expense.id });
          row.append(remove);
          return row;
        })
      );
    }

    if (costs.loaded) {
      this._setCostsStatus(
        all.length ? "" : t("Inca nu ai inregistrat cheltuieli pentru acest vehicul.")
      );
    }
  }

  /* --------------------------------------------------------------- */
  /* Teme                                                             */
  /* --------------------------------------------------------------- */
  _subscribeTheme() {
    const connection = this._hass?.connection;
    if (this._themeUnsub || !connection || !this.isConnected) return;

    this._themeUnsub = connection
      .subscribeMessage(
        (message) => {
          this._savedTheme = message.theme || null;
          if (!this._themeDraft) this._applyTheme();
        },
        { type: THEME_WS_SUBSCRIBE }
      )
      .catch((err) => {
        /* integrare veche sau neincarcata: ramane tema implicita */
        console.warn("vehicle-manager-card: tema nu poate fi incarcata", err);
        return null;
      });
  }

  _unsubscribeTheme() {
    const pending = this._themeUnsub;
    this._themeUnsub = null;
    pending?.then((unsub) => unsub?.()).catch(() => {});
  }

  /* Tema salvata, peste culorile din configurarea cardului (compatibilitate). */
  _baseTheme() {
    const legacy = {};
    if (this._config.accent) legacy.accent = this._config.accent;
    if (this._config.accent2) legacy.accent2 = this._config.accent2;
    return normalizeTheme({ ...legacy, ...(this._savedTheme || {}) });
  }

  _currentTheme() {
    return this._themeDraft || this._baseTheme();
  }

  _applyTheme() {
    const el = this._el;
    if (!el) return;
    const theme = this._currentTheme();

    for (const [name, value] of Object.entries(themeToCss(theme))) {
      el.card.style.setProperty(name, value);
    }
    el.cardBg.hidden = !theme.bg_image || theme.bg_target !== "card";
    el.stageBg.hidden = !theme.bg_image || theme.bg_target !== "stage";

    /* three.js reface mediul si scena doar cand se schimba culorile */
    const colors = this._sceneColors(theme);
    const colorKey = `${colors.accent}|${colors.accent2}|${colors.bg}`;
    if (this._viewer && colorKey !== this._sceneColorKey) {
      this._sceneColorKey = colorKey;
      this._viewer.setTheme(colors);
    }
  }

  /* Culorile efective pentru three.js (rezolva si variabilele temei HA). */
  _sceneColors(theme) {
    const computed = this.isConnected ? getComputedStyle(this._el.card) : null;
    const read = (name, fallback) => {
      const value = computed?.getPropertyValue(name).trim();
      return value && !value.startsWith("var(") ? value : fallback;
    };
    return {
      accent: read("--vm-accent", theme.accent),
      accent2: read("--vm-accent-2", theme.accent2),
      bg: read("--vm-bg", theme.bg),
    };
  }

  _openThemes() {
    if (this._costs) this._closeCosts();
    if (!this._el.files.hidden) this._closeFiles();
    this._themeDraft = { ...this._baseTheme() };
    this._el.themeBtn.setAttribute("aria-expanded", "true");
    this._el.themes.hidden = false;
    this._renderThemes();
  }

  _closeThemes() {
    this._themeDraft = null;
    this._el.themeBtn.setAttribute("aria-expanded", "false");
    this._el.themes.hidden = true;
    this._el.themes.replaceChildren();
    this._applyTheme();
  }

  _setDraft(changes, rerender) {
    this._themeDraft = { ...this._themeDraft, ...changes };
    this._applyTheme();
    if (rerender) this._renderThemes();
  }

  _renderThemes() {
    const draft = this._themeDraft;
    const root = this._el.themes;

    const head = document.createElement("div");
    head.className = "th-head";
    head.innerHTML = `<h2>Themes</h2><span class="th-status"></span>`;
    const status = head.querySelector(".th-status");
    this._themeStatus = status;
    status.textContent =
      t("Modificarile se vad imediat; apasa Salveaza ca sa le pastrezi pe toate dispozitivele.");

    /* presetari */
    const presets = document.createElement("div");
    presets.className = "th-presets";
    for (const preset of THEME_PRESETS) {
      const values = { ...THEME_DEFAULTS, ...preset.values };
      const button = document.createElement("button");
      button.type = "button";
      button.className = "th-preset";
      button.setAttribute("aria-pressed", String(draft.preset === preset.id));
      const dots = preset.values.follow_ha
        ? [HA_COLOR_VARS.accent, HA_COLOR_VARS.accent2, HA_COLOR_VARS.bg, HA_COLOR_VARS.text]
        : [values.accent, values.accent2, values.bg, values.text];
      button.innerHTML = `<span class="dots">${dots
        .map((color) => `<span style="background:${color}"></span>`)
        .join("")}</span><span></span>`;
      button.lastElementChild.textContent = preset.name;
      button.addEventListener("click", () => {
        const layout = Object.fromEntries(THEME_LAYOUT_KEYS.map((key) => [key, draft[key]]));
        this._themeDraft = { ...THEME_DEFAULTS, ...layout, ...preset.values, preset: preset.id };
        this._applyTheme();
        this._renderThemes();
      });
      presets.append(button);
    }

    /* grupuri de setari */
    const groups = document.createElement("div");
    groups.className = "th-groups";
    for (const group of THEME_GROUPS) {
      const box = document.createElement("div");
      box.className = "th-group";
      const title = document.createElement("h4");
      title.textContent = t(group.title);
      box.append(title, ...group.items.map((item) => this._renderThemeControl(item, draft)));
      groups.append(box);
    }

    /* actiuni */
    const actions = document.createElement("div");
    actions.className = "th-actions";
    const reset = this._themeButton(t("Implicit"), "btn danger", () => {
      this._themeDraft = { ...THEME_DEFAULTS };
      this._applyTheme();
      this._renderThemes();
    });
    const cancel = this._themeButton(t("Renunta"), "btn", () => this._closeThemes());
    const save = this._themeButton(t("Salveaza"), "btn primary", async () => {
      save.disabled = true;
      status.textContent = t("Se salveaza...");
      try {
        await this._hass.callWS({ type: THEME_WS_SAVE, theme: this._themeDraft });
        this._savedTheme = { ...this._themeDraft };
        this._closeThemes();
      } catch (err) {
        save.disabled = false;
        status.textContent =
          err?.code === "unknown_command"
            ? t("Serverul ruleaza o versiune veche a integrarii (fara Themes). Copiaza tot folderul custom_components/vehicle_manager, inclusiv theme.py, si restarteaza Home Assistant.")
            : t("Tema nu a putut fi salvata: {err}", { err: err?.message || err?.code || err });
      }
    });
    actions.append(reset, cancel, save);

    root.replaceChildren(head, presets, groups, actions);
  }

  _renderBackgroundControl(row, draft) {
    const box = document.createElement("div");
    box.className = "th-bg";

    const preview = document.createElement("div");
    preview.className = "th-bg-preview";
    if (draft.bg_image) preview.style.backgroundImage = `url("${draft.bg_image}")`;
    else preview.textContent = t("fara imagine");

    const actions = document.createElement("div");
    actions.className = "th-bg-actions";
    const file = document.createElement("input");
    file.type = "file";
    file.accept = "image/jpeg,image/png,image/webp,image/gif";
    const upload = this._themeButton(t("Incarca imagine"), "btn", () => file.click());
    const remove = this._themeButton(t("Elimina"), "btn", () =>
      this._setDraft({ bg_image: "" }, true)
    );
    remove.hidden = !draft.bg_image;
    file.addEventListener("change", async () => {
      const chosen = file.files?.[0];
      if (!chosen) return;
      upload.disabled = true;
      await this._uploadBackground(chosen);
      upload.disabled = false;
    });
    actions.append(upload, remove, file);

    const url = document.createElement("input");
    url.type = "text";
    url.className = "th-bg-url";
    url.placeholder = t("sau un URL: /local/fundal.jpg, https://...");
    url.value = draft.bg_image;
    url.addEventListener("change", () => {
      const value = url.value.trim();
      if (value && !BG_URL_RE.test(value)) {
        this._themeStatus.textContent =
          t("URL invalid: trebuie sa inceapa cu / sau https:// si sa nu contina spatii, ghilimele sau paranteze.");
        return;
      }
      this._setDraft({ bg_image: value }, true);
    });

    box.append(preview, actions, url);
    row.append(box);
    return row;
  }

  async _uploadBackground(file) {
    const status = this._themeStatus;
    status.textContent = t("Se pregateste imaginea...");
    try {
      const prepared = await shrinkImage(file);
      const form = new FormData();
      form.append("file", prepared, file.name || "fundal");
      status.textContent = t("Se incarca imaginea...");

      const hass = this._hass;
      const response = hass.fetchWithAuth
        ? await hass.fetchWithAuth(THEME_BG_UPLOAD, { method: "POST", body: form })
        : await fetch(THEME_BG_UPLOAD, {
            method: "POST",
            body: form,
            headers: { Authorization: `Bearer ${hass.auth?.data?.access_token}` },
          });

      if (response.status === 404) {
        throw new Error(
          t("serverul ruleaza o versiune veche a integrarii; copiaza theme.py nou si restarteaza Home Assistant")
        );
      }
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.message || `HTTP ${response.status}`);

      if (!this._themeDraft) return; /* panoul a fost inchis intre timp */
      this._setDraft({ bg_image: body.url }, true);
      this._themeStatus.textContent = t("Imagine incarcata. Apasa Salveaza ca sa o pastrezi.");
    } catch (err) {
      status.textContent = t("Imaginea nu a putut fi incarcata: {err}", { err: err?.message || err });
    }
  }

  _themeButton(label, className, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    button.addEventListener("click", onClick);
    return button;
  }

  _renderThemeControl(item, draft) {
    const row = document.createElement("div");
    row.className = `th-row ${item.type}`;
    const label = document.createElement("label");
    label.textContent = t(item.label);

    if (item.type === "image") return this._renderBackgroundControl(row, draft);

    let input;
    if (item.type === "color") {
      input = document.createElement("input");
      input.type = "color";
      input.value = draft[item.key];
      input.disabled = draft.follow_ha;
      input.addEventListener("input", () =>
        this._setDraft({ [item.key]: input.value, preset: "custom" })
      );
      row.append(label, input);
    } else if (item.type === "bool") {
      input = document.createElement("input");
      input.type = "checkbox";
      input.checked = Boolean(draft[item.key]);
      /* follow_ha activeaza/dezactiveaza selectoarele de culoare */
      input.addEventListener("change", () =>
        this._setDraft({ [item.key]: input.checked, preset: "custom" }, item.key === "follow_ha")
      );
      row.append(label, input);
    } else if (item.type === "select") {
      input = document.createElement("select");
      for (const [value, text] of item.options) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = t(text);
        input.append(option);
      }
      input.value = draft[item.key];
      input.addEventListener("change", () => this._setDraft({ [item.key]: input.value }));
      row.append(label, input);
    } else {
      input = document.createElement("input");
      input.type = "range";
      input.min = item.min;
      input.max = item.max;
      input.step = item.step;
      input.value = draft[item.key];
      const value = document.createElement("span");
      value.className = "val";
      value.textContent = formatThemeValue(item, draft[item.key]);
      input.addEventListener("input", () => {
        const number = Number(input.value);
        value.textContent = formatThemeValue(item, number);
        this._setDraft({ [item.key]: number });
      });
      row.append(label, input, value);
    }
    /* id-urile sunt izolate in shadow DOM-ul fiecarui card */
    input.id = `vm-th-${item.key}`;
    label.htmlFor = input.id;
    return row;
  }

  async _startViewer() {
    const config = this._config;
    this._sceneColorKey = null;
    const base = config.three_src || DEFAULT_THREE;
    this._viewer = new CarViewer(this._el.canvas, {
      ...this._sceneColors(this._currentTheme()),
      threeSrc: base,
      gltfLoaderSrc:
        config.gltf_loader_src || `${base}/examples/jsm/loaders/GLTFLoader.js`,
      autoRotate: config.auto_rotate !== false,
      rotateSpeed: Number(config.rotate_speed) || 0.35,
    });

    try {
      await this._viewer.init();
      this._applyStageSource(true);
    } catch (err) {
      this._el.canvas.hidden = true;
      this._showStageFallback();
    }
  }

  _showStageFallback() {
    const hasPhoto = Boolean(this._currentPhoto);
    if (hasPhoto) {
      this._photoMode = true;
      this._applyStageSource();
      return;
    }
    this._el.stageMsg.hidden = false;
    this._el.stageMsg.textContent =
      t("Modelul 3D nu a putut fi incarcat (biblioteca three.js nu este accesibila). Adauga o poza vehiculului sau seteaza three_src catre o copie locala.");
  }

  _setPhotoMode(enabled) {
    this._photoMode = enabled;
    this._applyStageSource();
  }

  _applyStageSource(force) {
    const el = this._el;
    if (!el) return;

    const photo = this._currentPhoto;
    const canUse3d = Boolean(this._viewer && !this._viewer.failed);
    const showPhoto = (this._photoMode && photo) || (!canUse3d && photo);

    el.photo.hidden = !showPhoto;
    el.canvas.hidden = Boolean(showPhoto) || !canUse3d;
    if (showPhoto && (force || el.photo.getAttribute("src") !== photo)) {
      el.photo.setAttribute("src", photo);
    }

    const showToggle = this._config.show_photo_toggle !== false && Boolean(photo);
    el.view3d.hidden = !showToggle || !canUse3d;
    el.viewPhoto.hidden = !showToggle;
    el.view3d.setAttribute("aria-pressed", String(!showPhoto));
    el.viewPhoto.setAttribute("aria-pressed", String(Boolean(showPhoto)));

    if (canUse3d || photo) el.stageMsg.hidden = true;
  }

  /* --------------------------------------------------------------- */
  /* Actualizarea datelor                                             */
  /* --------------------------------------------------------------- */
  _update() {
    if (!this._built || !this._hass) return;

    const vehicles = this._vehicles();
    const el = this._el;

    if (!vehicles.length) {
      el.root.hidden = true;
      el.empty.hidden = false;
      el.empty.innerHTML =
        t("Niciun vehicul gasit. Adauga unul din <code>Setari &rsaquo; Dispozitive si servicii &rsaquo; Adauga integrare &rsaquo; Vehicle Manager</code>.");
      return;
    }
    el.root.hidden = false;
    el.empty.hidden = true;

    /* selectie valida */
    const ids = vehicles.map((v) => v.id);
    if (!this._selected || !ids.includes(this._selected)) {
      const stored = this._readStoredSelection();
      this._selected =
        (ids.includes(this._config.default_vehicle) && this._config.default_vehicle) ||
        (stored && ids.includes(stored) ? stored : ids[0]);
      this._signature = null;
    }

    /* dropdown doar cand lista s-a schimbat */
    const keys = vehicles.map((v) => `${v.id}:${v.name}`).join("|");
    if (keys !== this._vehicleKeys) {
      this._vehicleKeys = keys;
      el.select.replaceChildren(
        ...vehicles.map((vehicle) => {
          const option = document.createElement("option");
          option.value = vehicle.id;
          option.textContent = vehicle.name;
          return option;
        })
      );
    }
    el.select.value = this._selected;
    el.select.parentElement.hidden = vehicles.length < 2 && !this._config.always_show_picker;

    const state = this._hass.states[this._selected];
    if (!state) return;

    const signature = `${state.state}|${state.last_updated}|${this._selected}`;
    if (signature === this._signature) return;
    this._signature = signature;

    this._renderVehicle(state);
  }

  _renderVehicle(state) {
    const el = this._el;
    const attributes = state.attributes || {};
    const vehicle = attributes.vehicle || {};
    const documents = attributes.documents || {};
    const entities = attributes.entities || {};
    const language = this._hass.locale?.language || "ro-RO";
    const status = state.state;

    /* --- cap --- */
    el.led.dataset.status = status;
    el.title.textContent =
      this._config.title || attributes.vehicle_name || state.attributes.friendly_name || t("Vehicul");
    const subtitleParts = [vehicle.make, vehicle.model, vehicle.year].filter(Boolean);
    el.subtitle.textContent = subtitleParts.join(" · ") || t(STATUS_LABEL[status] || "");
    el.plate.textContent = vehicle.license_plate || "";
    el.plate.hidden = !vehicle.license_plate;

    /* --- caracteristici --- */
    el.specList.replaceChildren(
      ...this._visibleSpecs()
        .filter((row) => row.key !== "parking" || vehicle.parking || this._config.specs?.includes("parking"))
        .map((row) => this._renderSpec(row, vehicle, entities))
    );

    /* --- acte --- */
    el.docList.replaceChildren(
      ...this._visibleDocuments(documents).map((document_) =>
        this._renderDocument(document_, entities, language)
      )
    );

    /* --- acte urgente (modul compact) --- */
    this._renderUrgent(documents, entities);

    /* --- costuri: la schimbarea vehiculului, panoul deschis trece pe noul vehicul --- */
    this._entryId = attributes.entry_id || null;
    this._mileage = vehicle.mileage ?? null;
    this._electric = vehicle.fuel_type === "electric";
    this._documents = documents;
    /* fisierele se urmaresc mereu (pentru agrafele din lista de acte) */
    if (this._filesEntry !== this._entryId) this._subscribeFiles();
    if (this._costs && this._costsEntry !== this._entryId) {
      this._costs.expenses = [];
      this._costs.loaded = false;
      this._buildCosts();
      this._subscribeCosts();
    }

    /* --- scena --- */
    this._currentPhoto = attributes.photo || null;
    this._viewer?.setVehicle({
      model3d: attributes.model_3d || null,
      colorHex: vehicle.color_hex || "#9aa4af",
    });
    this._applyStageSource();

    el.hud.textContent = attributes.model_3d
      ? t("model 3d · trage pentru rotire")
      : t("randare procedurala · trage pentru rotire");

    /* --- subsol --- */
    const attention = attributes.attention || [];
    el.footLeft.textContent = attention.length
      ? t("Necesita atentie: {list}", { list: attention.map((a) => t(a)).join(", ") })
      : `Toate actele sunt in regula`;
    el.footRight.textContent = t("prag {days}z / {km}km", {
      days: attributes.warn_days,
      km: formatNumber(attributes.warn_km),
    });
  }

  /*
   * Actele bifate in editor (config "documents"), in ordinea integrarii.
   * Fara bife: cele 5 de baza plus orice alt act care are o data completata.
   */
  _visibleDocuments(documents) {
    const all = Object.values(documents);
    const chosen = this._config.documents;
    if (Array.isArray(chosen) && chosen.length) {
      return all.filter((d) => chosen.includes(d.key));
    }
    return all.filter((d) => CLASSIC_DOCUMENTS.includes(d.key) || d.status !== "unknown");
  }

  /* Caracteristicile bifate in editor (config "specs"); fara bife, toate. */
  _visibleSpecs() {
    const chosen = this._config.specs;
    return Array.isArray(chosen) && chosen.length
      ? SPEC_ROWS.filter((row) => chosen.includes(row.key))
      : SPEC_ROWS;
  }

  _renderUrgent(documents, entities) {
    const limit = clamp(Math.round(Number(this._config.compact_items) || 3), 1, 5);
    /*
     * In ordinea urgentei. La aceeasi stare decide timpul ramas; actele urmarite
     * doar pe km sunt convertite grosier in zile (~50 km/zi) ca sa poata fi comparate.
     */
    const remaining = (d) =>
      d.days ?? (d.km_remaining !== null && d.km_remaining !== undefined ? d.km_remaining / 50 : Infinity);
    const items = this._visibleDocuments(documents)
      .filter((d) => d.status !== "unknown")
      .sort(
        (a, b) =>
          (STATUS_RANK[a.status] ?? 9) - (STATUS_RANK[b.status] ?? 9) || remaining(a) - remaining(b)
      )
      .slice(0, limit);

    const nodes = items.map((document_) => {
      const node = document.createElement("button");
      node.type = "button";
      node.className = "u-item";
      node.dataset.status = document_.status;
      node.innerHTML = `<span class="u-dot"></span><span class="u-text"><span class="u-name"></span><span class="u-val"></span></span>`;
      node.querySelector(".u-name").textContent = t(document_.label);
      node.querySelector(".u-val").textContent = this._shortRemaining(document_);
      const entityId =
        entities[`${document_.key}_date`] || entities[`${document_.key}_km`] || null;
      node.addEventListener("click", () => moreInfo(this, entityId));
      return node;
    });

    if (!items.some((d) => d.status === "warning" || d.status === "expired")) {
      const ok = document.createElement("div");
      ok.className = "u-all-ok";
      ok.innerHTML = `<ha-icon icon="mdi:shield-check"></ha-icon><span>${t("Toate actele sunt in regula")}</span>`;
      nodes.unshift(ok);
    }
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "u-name";
      empty.textContent = t("Nicio scadenta completata");
      nodes.push(empty);
    }
    this._el.urgent.replaceChildren(...nodes);
  }

  _shortRemaining(document_) {
    return shortRemaining(document_);
  }

  _renderParking(row, parking) {
    const node = document.createElement("div");
    node.className = "spec";
    node.innerHTML = `<ha-icon></ha-icon><span class="k"></span><span class="v"><span class="when"></span></span>`;
    node.querySelector("ha-icon").setAttribute("icon", row.icon);
    node.querySelector(".k").textContent = t(row.label);
    const when = node.querySelector(".when");

    if (!parking) {
      when.textContent = "—";
      return node;
    }
    if (parking.state === "driving") {
      when.textContent = t("in mers");
    } else {
      when.textContent = timeAgo(parking.time) || t("parcata");
    }
    if (parking.latitude != null && parking.longitude != null) {
      const link = document.createElement("a");
      link.className = "nav";
      link.href = `https://www.google.com/maps/search/?api=1&query=${parking.latitude},${parking.longitude}`;
      link.target = "_blank";
      link.rel = "noopener";
      link.title = parking.state === "driving" ? t("Ultimul loc de parcare") : t("Navigheaza pana la masina");
      link.innerHTML = `<ha-icon icon="mdi:navigation-variant"></ha-icon>`;
      node.querySelector(".v").append(link);
    }
    return node;
  }

  _renderSpec(row, vehicle, entities) {
    if (row.key === "parking") return this._renderParking(row, vehicle.parking);
    /* combustibilul vine de la server in romana */
    const raw = row.useLabel ? t(String(vehicle[row.useLabel] ?? "")) || null : vehicle[row.key];
    const entityId = row.entity ? entities[row.entity] : null;
    const clickable = Boolean(entityId);

    const node = document.createElement(clickable ? "button" : "div");
    node.className = "spec";
    node.dataset.clickable = String(clickable);

    const value =
      raw === null || raw === undefined || raw === ""
        ? "—"
        : row.unit
        ? `${formatNumber(raw)} ${row.unit}`
        : String(raw);

    node.innerHTML = `
      <ha-icon icon="${row.key === "fuel_type" && vehicle.fuel_icon ? vehicle.fuel_icon : row.icon}"></ha-icon>
      <span class="k">${t(row.label)}</span>
      <span class="v">
        ${row.swatch && vehicle.color_hex ? `<span class="swatch" style="background:${vehicle.color_hex}"></span>` : ""}
        ${row.auto && vehicle[row.auto] ? `<span class="auto" title="${t("Preluat automat din senzor")}">auto</span>` : ""}
        <span>${value}</span>
      </span>
    `;

    if (clickable) {
      node.type = "button";
      node.addEventListener("click", () => moreInfo(this, entityId));
    }
    return node;
  }

  _renderDocument(document_, entities, language) {
    const status = document_.status;
    const days = document_.days;
    const kmRemaining = document_.km_remaining;

    /* fractiunea afisata pe inel: prioritar zile, altfel kilometri */
    let fraction = 0;
    if (days !== null && days !== undefined) {
      fraction = clamp(days / (document_.horizon || 365), 0, 1);
    } else if (kmRemaining !== null && kmRemaining !== undefined) {
      fraction = clamp(kmRemaining / (KM_HORIZON[document_.key] || 15000), 0, 1);
    }

    const radius = 19;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference * (1 - fraction);

    let badge = "—";
    if (days !== null && days !== undefined) badge = String(days);
    else if (kmRemaining !== null && kmRemaining !== undefined) {
      badge = `${Math.round(kmRemaining / 1000)}k`;
    }

    const dateText = formatDate(document_.date, language);
    const lines = [];
    if (days !== null && days !== undefined) {
      lines.push(days < 0 ? t("expirat acum {n} zile", { n: Math.abs(days) }) : t("{n} zile ramase", { n: days }));
    }
    if (kmRemaining !== null && kmRemaining !== undefined) {
      lines.push(
        kmRemaining < 0
          ? t("depasit cu {km} km", { km: formatNumber(Math.abs(kmRemaining)) })
          : t("{km} km ramasi", { km: formatNumber(kmRemaining) })
      );
    }

    const entityId =
      entities[`${document_.key}_date`] ||
      entities[`${document_.key}_km`] ||
      null;

    const node = document.createElement("button");
    node.className = "doc";
    node.type = "button";
    node.dataset.status = status;
    node.innerHTML = `
      <span class="ring">
        <svg viewBox="0 0 44 44" aria-hidden="true">
          <circle class="trk" cx="22" cy="22" r="${radius}"></circle>
          <circle class="val" cx="22" cy="22" r="${radius}"
                  stroke-dasharray="${circumference.toFixed(2)}"
                  stroke-dashoffset="${offset.toFixed(2)}"></circle>
        </svg>
        <span class="num">${badge}</span>
      </span>
      <span class="meta">
        <span class="name">${t(document_.label)}${this._clipBadge(document_.key)}</span>
        <span class="main">${dateText || t(STATUS_LABEL[status] || "Necompletat")}</span>
        <span class="sub">${lines.join(" · ") || t("fara scadenta setata")}</span>
      </span>
      <ha-icon icon="${document_.icon}"></ha-icon>
    `;

    node.addEventListener("click", () => moreInfo(this, entityId));
    return node;
  }
}

/* Fisierul poate fi incarcat de doua ori (automat + resursa manuala). */
if (!customElements.get("vehicle-manager-card")) {
  customElements.define("vehicle-manager-card", VehicleManagerCard);
}

/* ------------------------------------------------------------------ */
/* Editor grafic                                                      */
/* ------------------------------------------------------------------ */

const editorSchema = () => [
  { name: "title", selector: { text: {} } },
  {
    name: "default_vehicle",
    selector: { entity: { domain: "sensor", integration: "vehicle_manager" } },
  },
  {
    type: "grid",
    name: "",
    schema: [
      { name: "auto_rotate", selector: { boolean: {} } },
      { name: "show_photo_toggle", selector: { boolean: {} } },
    ],
  },
  {
    name: "rotate_speed",
    selector: { number: { min: 0, max: 1.5, step: 0.05, mode: "slider" } },
  },
  {
    type: "grid",
    name: "",
    schema: [
      { name: "show_theme_button", selector: { boolean: {} } },
      { name: "show_costs_button", selector: { boolean: {} } },
      { name: "show_files_button", selector: { boolean: {} } },
    ],
  },
  {
    type: "grid",
    name: "",
    schema: [
      { name: "compact", selector: { boolean: {} } },
      { name: "compact_items", selector: { number: { min: 1, max: 5, mode: "box" } } },
    ],
  },
  { name: "navigation_path", selector: { navigation: {} } },
  {
    name: "documents",
    selector: {
      select: {
        multiple: true,
        mode: "list",
        options: DOCUMENT_OPTIONS.map(([value, label]) => ({ value, label: t(label) })),
      },
    },
  },
  {
    name: "specs",
    selector: {
      select: {
        multiple: true,
        mode: "list",
        options: SPEC_ROWS.map((row) => ({ value: row.key, label: t(row.label) })),
      },
    },
  },
  { name: "three_src", selector: { text: {} } },
];

const EDITOR_LABELS = {
  title: "Titlu (gol = numele vehiculului)",
  default_vehicle: "Vehicul implicit",
  auto_rotate: "Rotire automata",
  show_photo_toggle: "Buton comutare poza",
  rotate_speed: "Viteza de rotire",
  show_theme_button: "Buton Themes (culorile se aleg din card)",
  show_costs_button: "Buton Costuri (istoricul cheltuielilor)",
  show_files_button: "Buton Dosar (poze si PDF-uri cu actele)",
  compact: "Mod compact (pentru pagina principala)",
  compact_items: "Acte afisate in modul compact",
  navigation_path: "Pagina deschisa din modul compact (ex. /lovelace/masini)",
  documents: "Acte afisate (nimic bifat: cele 5 de baza + actele completate)",
  specs: "Caracteristici afisate (nimic bifat: toate)",
  three_src: "Sursa three.js",
};

class VehicleManagerCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) this._form.hass = hass;
  }

  _render() {
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) => (EDITOR_LABELS[schema.name] ? t(EDITOR_LABELS[schema.name]) : schema.name);
      this._form.addEventListener("value-changed", (event) => {
        event.stopPropagation();
        fireEvent(this, "config-changed", { config: event.detail.value });
      });
      this.replaceChildren(this._form);
    }
    this._form.schema = editorSchema();
    this._form.data = this._config;
    if (this._hass) this._form.hass = this._hass;
  }
}

if (!customElements.get("vehicle-manager-card-editor")) {
  customElements.define("vehicle-manager-card-editor", VehicleManagerCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "vehicle-manager-card")) window.customCards.push({
  type: "vehicle-manager-card",
  name: "Vehicle Manager Card",
  description:
    "Card futurist pentru vehicule: model 3D rotativ, caracteristici si acte (RCA, ITP, rovinieta, revizie, distributie).",
  preview: true,
  documentationURL: "https://github.com/alinalecu2013/ha-vehicle-manager",
});

/* ------------------------------------------------------------------ */
/* Cardul Garaj: toate vehiculele pe scurt                             */
/* ------------------------------------------------------------------ */

const GARAGE_STYLES = `
:host { display: block; }
ha-card {
  display: block; position: relative; overflow: hidden;
  padding: calc(14px * var(--vm-sp, 1)) calc(16px * var(--vm-sp, 1));
  color: var(--vm-text, var(--primary-text-color));
  font-family: var(--vm-font, inherit);
  border: 1px solid var(--vm-line, var(--divider-color));
  border-radius: calc(12px * var(--vm-r, 1));
  background:
    radial-gradient(900px 300px at 50% -20%, color-mix(in srgb, var(--vm-accent, #00e5ff) var(--vm-glow-1, 16%), transparent), transparent 70%),
    var(--vm-bg, var(--card-background-color));
}
h2 {
  margin: 0 0 12px; display: flex; align-items: center; gap: 10px;
  font: 600 calc(11px * var(--vm-fs, 1))/1 var(--vm-mono, monospace);
  letter-spacing: .2em; text-transform: uppercase; color: var(--vm-accent, var(--primary-color));
}
h2::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, var(--vm-accent, var(--primary-color)), transparent); opacity: .5; }
.list { display: flex; flex-direction: column; gap: calc(8px * var(--vm-sp, 1)); }
.row {
  /* coloane proportionale: aceleasi pe toate randurile, deci aliniate */
  display: grid; grid-template-columns: 12px minmax(0, 1.1fr) minmax(0, 1fr) minmax(0, 1.5fr);
  gap: 12px; align-items: center; width: 100%; text-align: left; cursor: pointer;
  padding: calc(10px * var(--vm-sp, 1)) 12px; font: inherit; color: inherit;
  border-radius: calc(11px * var(--vm-r, 1));
  background: color-mix(in srgb, var(--vm-panel-c, #121822) var(--vm-panel-p, 68%), transparent);
  border: 1px solid color-mix(in srgb, var(--vm-line-c, #82aac8) 22%, transparent);
}
.row:hover { border-color: var(--vm-accent, var(--primary-color)); }
.led { width: 10px; height: 10px; border-radius: 50%; background: var(--vm-dim, var(--secondary-text-color)); }
.led[data-status="ok"] { background: var(--vm-ok, #22d38a); box-shadow: 0 0 calc(10px * var(--vm-glow, 1)) var(--vm-ok, #22d38a); }
.led[data-status="warning"] { background: var(--vm-warn, #ffb020); box-shadow: 0 0 calc(10px * var(--vm-glow, 1)) var(--vm-warn, #ffb020); }
.led[data-status="expired"] { background: var(--vm-bad, #ff4d5e); box-shadow: 0 0 calc(10px * var(--vm-glow, 1)) var(--vm-bad, #ff4d5e); }
.who, .next { min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.name { font-weight: 650; font-size: calc(14px * var(--vm-fs, 1)); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sub, .k {
  font: calc(10px * var(--vm-fs, 1))/1.3 var(--vm-mono, monospace); letter-spacing: .12em; text-transform: uppercase;
  color: var(--vm-dim, var(--secondary-text-color)); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.v { font-size: calc(13px * var(--vm-fs, 1)); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.v[data-status="warning"] { color: var(--vm-warn, #ffb020); }
.v[data-status="expired"] { color: var(--vm-bad, #ff4d5e); }
.stats { display: flex; gap: 14px; justify-content: flex-end; }
.stat { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; }
.empty { color: var(--vm-dim, var(--secondary-text-color)); font-size: 13px; padding: 10px 2px; }
@media (max-width: 560px) {
  .row { grid-template-columns: 12px minmax(0, 1fr) auto; }
  .stats { grid-column: 2 / -1; justify-content: flex-start; }
}
`;

class VehicleManagerGarageCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._themeUnsub = null;
  }

  static getConfigElement() {
    return document.createElement("vehicle-manager-garage-card-editor");
  }

  static getStubConfig() {
    return { type: "custom:vehicle-manager-garage-card" };
  }

  setConfig(config) {
    this._config = { title: t("Garaj"), ...config };
    this._signature = null;
    if (this._hass) this._render();
  }

  getCardSize() {
    return 2 + this._vehicles().length;
  }

  set hass(hass) {
    setLanguage(hass);
    this._hass = hass;
    this._subscribeTheme();
    this._render();
  }

  connectedCallback() {
    if (this._hass) this._subscribeTheme();
  }

  disconnectedCallback() {
    const pending = this._themeUnsub;
    this._themeUnsub = null;
    pending?.then((unsub) => unsub?.()).catch(() => {});
  }

  /* aceeasi tema ca in cardul principal (salvata din Themes) */
  _subscribeTheme() {
    const connection = this._hass?.connection;
    if (this._themeUnsub || !connection || !this.isConnected) return;
    this._themeUnsub = connection
      .subscribeMessage(
        (message) => {
          this._theme = normalizeTheme(message.theme || null);
          this._applyTheme();
        },
        { type: THEME_WS_SUBSCRIBE }
      )
      .catch(() => null);
  }

  _applyTheme() {
    const card = this.shadowRoot.querySelector("ha-card");
    if (!card || !this._theme) return;
    for (const [name, value] of Object.entries(themeToCss(this._theme))) {
      card.style.setProperty(name, value);
    }
  }

  _vehicles() {
    const hass = this._hass;
    if (!hass) return [];
    const explicit = this._config?.vehicles;
    const ids = Array.isArray(explicit) && explicit.length
      ? explicit.filter((id) => hass.states[id])
      : Object.keys(hass.states).filter(
          (id) => id.startsWith("sensor.") && hass.states[id].attributes?.vm_card === true
        );
    return ids
      .map((id) => hass.states[id])
      .sort((a, b) =>
        String(a.attributes.vehicle_name || a.entity_id).localeCompare(
          String(b.attributes.vehicle_name || b.entity_id),
          "ro"
        )
      );
  }

  _render() {
    const vehicles = this._vehicles();
    const related = (state, key) => this._hass.states[state.attributes.entities?.[key]];
    const signature = vehicles
      .map((s) => {
        const cost = related(s, "expenses_year");
        const fuel = related(s, "fuel_consumption");
        return `${s.entity_id}|${s.last_updated}|${cost?.state}|${fuel?.state}`;
      })
      .join(";") + `|${this._config.title}|${this._config.navigation_path}`;
    if (signature === this._signature) return;
    this._signature = signature;

    if (!this.shadowRoot.querySelector("ha-card")) {
      const style = document.createElement("style");
      style.textContent = GARAGE_STYLES;
      const card = document.createElement("ha-card");
      card.innerHTML = `<h2></h2><div class="list"></div>`;
      this.shadowRoot.replaceChildren(style, card);
      this._applyTheme();
    }
    const card = this.shadowRoot.querySelector("ha-card");
    card.querySelector("h2").textContent = this._config.title || t("Garaj");
    const list = card.querySelector(".list");

    if (!vehicles.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = t("Niciun vehicul. Adauga unul din Setari › Dispozitive si servicii › Vehicle Manager.");
      list.replaceChildren(empty);
      return;
    }
    list.replaceChildren(...vehicles.map((state) => this._renderRow(state, related)));
  }

  _renderRow(state, related) {
    const a = state.attributes;
    const vehicle = a.vehicle || {};
    const docs = Object.values(a.documents || {}).filter((d) => d.status !== "unknown");
    /* cel mai urgent act: intai starea, apoi timpul ramas */
    const remaining = (d) =>
      d.days ?? (d.km_remaining !== null && d.km_remaining !== undefined ? d.km_remaining / 50 : Infinity);
    docs.sort((x, y) => (STATUS_RANK[x.status] ?? 9) - (STATUS_RANK[y.status] ?? 9) || remaining(x) - remaining(y));
    const next = docs[0];
    const attention = (a.attention || []).length;

    const row = document.createElement("button");
    row.type = "button";
    row.className = "row";
    row.innerHTML = `
      <span class="led"></span>
      <span class="who"><span class="name"></span><span class="sub"></span></span>
      <span class="next"><span class="k"></span><span class="v"></span></span>
      <span class="stats"></span>`;
    row.querySelector(".led").dataset.status = state.state;
    row.querySelector(".name").textContent = a.vehicle_name || state.entity_id;
    row.querySelector(".sub").textContent =
      [vehicle.license_plate, [vehicle.make, vehicle.model].filter(Boolean).join(" ")].filter(Boolean).join(" · ");

    if (next) {
      row.querySelector(".k").textContent =
        attention > 1 ? t("{label} (+{n} acte)", { label: t(next.label), n: attention - 1 }) : t(next.label);
      const value = row.querySelector(".v");
      value.textContent = shortRemaining(next);
      value.dataset.status = next.status;
    } else {
      row.querySelector(".k").textContent = t("Acte");
      row.querySelector(".v").textContent = t("necompletate");
    }

    const stats = row.querySelector(".stats");
    const addStat = (label, value) => {
      const stat = document.createElement("span");
      stat.className = "stat";
      stat.innerHTML = `<span class="k"></span><span class="v"></span>`;
      stat.querySelector(".k").textContent = label;
      stat.querySelector(".v").textContent = value;
      stats.append(stat);
    };
    const cost = related(state, "expenses_year");
    if (cost && !["unknown", "unavailable"].includes(cost.state)) {
      const unit = cost.attributes.unit_of_measurement || "";
      addStat(t("Costuri {year}", { year: new Date().getFullYear() }), `${formatNumber(Math.round(Number(cost.state)))} ${unit}`);
    }
    const fuel = related(state, "fuel_consumption");
    if (fuel && !["unknown", "unavailable"].includes(fuel.state)) {
      addStat(t("Consum"), `${formatNumber(Number(fuel.state))} ${fuel.attributes.unit_of_measurement || ""}`);
    }
    const parking = vehicle.parking;
    if (parking) {
      addStat(t("Parcare"), parking.state === "driving" ? t("in mers") : timeAgo(parking.time));
    }

    row.addEventListener("click", () => {
      if (this._config.navigation_path) navigate(this._config.navigation_path);
      else moreInfo(this, state.entity_id);
    });
    return row;
  }
}

if (!customElements.get("vehicle-manager-garage-card")) {
  customElements.define("vehicle-manager-garage-card", VehicleManagerGarageCard);
}

class VehicleManagerGarageCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) this._form.hass = hass;
  }

  _render() {
    if (!this._form) {
      this._form = document.createElement("ha-form");
      const labels = {
        title: t("Titlu"),
        navigation_path: t("Pagina deschisa la atingerea unui vehicul (gol = detaliile vehiculului)"),
      };
      this._form.computeLabel = (schema) => labels[schema.name] || schema.name;
      this._form.addEventListener("value-changed", (event) => {
        event.stopPropagation();
        fireEvent(this, "config-changed", { config: event.detail.value });
      });
      this.replaceChildren(this._form);
    }
    this._form.schema = [
      { name: "title", selector: { text: {} } },
      { name: "navigation_path", selector: { navigation: {} } },
    ];
    this._form.data = this._config;
    if (this._hass) this._form.hass = this._hass;
  }
}

if (!customElements.get("vehicle-manager-garage-card-editor")) {
  customElements.define("vehicle-manager-garage-card-editor", VehicleManagerGarageCardEditor);
}

if (!window.customCards.some((card) => card.type === "vehicle-manager-garage-card")) window.customCards.push({
  type: "vehicle-manager-garage-card",
  name: "Vehicle Manager Garage",
  description: "Toate vehiculele pe scurt: starea actelor, urmatoarea scadenta, costurile anului, consumul si parcarea.",
  preview: true,
  documentationURL: "https://github.com/alinalecu2013/ha-vehicle-manager",
});
