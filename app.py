# --- app.py ---
import streamlit as st
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import re
import requests

st.set_page_config(page_title="PV-Angebotsrechner", layout="wide")

@st.cache_data
def lade_netzbetreiber():
    df = pd.read_csv("netzbetreiber.csv", dtype={"plz": str})
    return dict(zip(df["plz"], df["netzbetreiber"]))

netzbetreiber_lookup = lade_netzbetreiber()

st.title("🔆 PV-Angebotsrechner Demo")

# 📋 Kundendaten
with st.container():
    st.subheader("👤 Kundendaten")
    name = st.text_input("Ihr Name")
    telefon = st.text_input("Telefonnummer (optional)")
    gebaeudetyp = st.selectbox("Gebäudetyp", ["Einfamilienhaus", "Doppelhaushälfte", "Mehrfamilienhaus", "Gewerbe", "Sonstige"])
    eigentuemer = st.radio("Sind Sie Eigentümer*in des Gebäudes?", ["Ja", "Nein", "Unklar / in Abstimmung"])

    adresse_eingabe = st.text_input("Adresseingabe (Straße, Hausnummer, PLZ, Ort)")
    st.caption("🔒 Hinweis: Zur Adressvalidierung werden Vorschläge von OpenStreetMap geladen. Es erfolgt keine Speicherung.")

    vorschlaege = []
    plz = ""
    if len(adresse_eingabe) > 5:
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": adresse_eingabe, "format": "json", "addressdetails": 1, "limit": 5}
            headers = {"User-Agent": "PV-Angebotsrechner/1.0"}
            r = requests.get(url, params=params, headers=headers)
            daten = r.json()
            vorschlaege = [f"{d['display_name']}" for d in daten]
        except Exception:
            st.warning("Adressvalidierung aktuell nicht möglich.")

    validierte_adresse = st.selectbox("Vorschläge für Ihre Adresse", options=vorschlaege) if vorschlaege else ""

    if validierte_adresse:
        try:
            idx = vorschlaege.index(validierte_adresse)
            plz = daten[idx]['address'].get('postcode', '')
        except Exception:
            plz = ""

# Eingaben
with st.container():
    st.subheader("📍 Standort & Verbrauch")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Postleitzahl", value=plz, disabled=True)
    with col2:
        strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.1, max_value=1.0, value=0.35)

    netzbetreiber = "unbekannt"
    if isinstance(plz, str) and plz.strip():
        if not re.fullmatch(r"\d{5}", plz.strip()):
            st.warning("Bitte geben Sie eine gültige 5-stellige deutsche Postleitzahl ein.")
            netzbetreiber = "ungültig"
        else:
            netzbetreiber = netzbetreiber_lookup.get(plz.strip(), "unbekannt")

    verbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=500, max_value=15000, value=5000)

# Technische Optionen
with st.expander("⚙️ Zusatzausstattung & Dachdaten (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        speicher = st.checkbox("Speicher gewünscht?")
        waermepumpe = st.checkbox("Wärmepumpe vorhanden?")
    with col2:
        wallbox_geplant = st.checkbox("Wallbox gewünscht?")
        wallbox_bestehend = st.checkbox("Wallbox vorhanden?")
        heizstab = st.checkbox("Heizstab vorhanden?")

    mit_dachdaten = st.checkbox("Ich kenne Daten zur Dachfläche und -ausrichtung")
    if mit_dachdaten:
        dachflaeche = st.number_input("Dachfläche nutzbar (m²)", min_value=5, max_value=200)
        neigung = st.slider("Dachneigung (Grad)", 0, 90, 30)
        ausrichtung = st.selectbox("Dachausrichtung", ["Süd", "Südost/Südwest", "Ost/West", "Nord"])
        anlagenleistung = dachflaeche / 7
    else:
        dachflaeche = None
        neigung = None
        ausrichtung = "Süd"
        default_leistung = verbrauch / 950
        anlagenleistung = st.slider("Geplante PV-Anlagengröße (kWp)", min_value=2.7, max_value=19.8, value=round(default_leistung, 2), step=0.45)

email = st.text_input("📧 Ihre E-Mail-Adresse")

# Ertragsberechnung
faktor = {
    "Süd": 1.0,
    "Südost/Südwest": 0.95,
    "Ost/West": 0.85,
    "Nord": 0.7
}[ausrichtung]
ertrag = anlagenleistung * 950 * faktor

# Empfehlung und Investition
speicher_staffel = [(3, 3000), (4, 4000), (6, 6000), (8, 7500), (10, 9000)]

def finde_index(verbrauch):
    if verbrauch < 3000: return 1
    elif verbrauch < 5000: return 2
    elif verbrauch < 7000: return 3
    else: return 4

idx = finde_index(verbrauch)
speicher_kwh_basis, speicher_kosten_basis = speicher_staffel[idx]
speicher_empf = f"{speicher_kwh_basis} kWh"
speicher_kwh_aktiv = speicher_kwh_basis if speicher else 0

wallbox_vorhanden = wallbox_geplant or wallbox_bestehend

def montagekosten_pro_kwp(kWp):
    if kWp < 5: return 600
    elif kWp < 6: return 550
    elif kWp < 7: return 520
    elif kWp < 8: return 490
    elif kWp < 9: return 460
    elif kWp < 10: return 430
    elif kWp < 11: return 400
    elif kWp < 12: return 380
    elif kWp < 13: return 360
    elif kWp < 14: return 340
    elif kWp < 15: return 320
    else: return 300

komponenten = anlagenleistung * 700
montage = montagekosten_pro_kwp(anlagenleistung) * anlagenleistung
aufschlag = speicher_kosten_basis if speicher else 0
if wallbox_geplant: aufschlag += 1200
if waermepumpe: aufschlag += 4000
if heizstab: aufschlag += 800
zusatzkosten = 2000

grundsystem = komponenten + montage
investition_gesamt = grundsystem + zusatzkosten + aufschlag

# Eigenverbrauch berechnen

def berechne_eigenverbrauch(verbrauch, ertrag, speicher_kwh, wp=False, wallbox=False):
    basis = min(verbrauch / ertrag, 1.0) * 0.25
    speicheranteil = min(speicher_kwh / 10, 1.0) * 0.5
    zusatz = 0.05 * int(wallbox) + 0.05 * int(wp)
    ev = basis + speicheranteil + zusatz
    return min(ev, 0.95)

eigenverbrauch = berechne_eigenverbrauch(
    verbrauch,
    ertrag,
    speicher_kwh_aktiv,
    wp=waermepumpe,
    wallbox=wallbox_vorhanden,
)
verbrauchter_pv_strom = min(ertrag * eigenverbrauch, verbrauch)
einspeisung = max(ertrag - verbrauchter_pv_strom, 0)
einspeiseverguetung = einspeisung * 0.08
ersparnis = verbrauchter_pv_strom * strompreis + einspeiseverguetung
amortisation = investition_gesamt / ersparnis if ersparnis else 0
co2_einsparung = ertrag * 0.7
rendite20 = ersparnis * 20 - investition_gesamt

# Variantenvergleich
speicher_vergleich = []
def speicher_variante(kwh, kosten):
    ev = berechne_eigenverbrauch(verbrauch, ertrag, kwh, wp=waermepumpe, wallbox=wallbox_vorhanden)
    verbrauchter_pv = min(ertrag * ev, verbrauch)
    einspeisung_v = max(ertrag - verbrauchter_pv, 0)
    ersparnis_v = verbrauchter_pv * strompreis + einspeisung_v * 0.08
    invest = grundsystem + zusatzkosten + kosten
    amort = invest / ersparnis_v if ersparnis_v else 0
    rendite = ersparnis_v * 20 - invest
    return {"ev": ev, "ersparnis": ersparnis_v, "amortisation": amort, "rendite20": rendite, "preis": invest, "kwh": kwh}

if speicher:
    idx_lower = max(idx - 1, 0)
    idx_upper = min(idx + 1, len(speicher_staffel) - 1)
    kwh_a, kosten_a = speicher_staffel[idx_lower]
    kwh_b, kosten_b = speicher_staffel[idx_upper]
    var_a = speicher_variante(kwh_a, kosten_a)
    var_b = speicher_variante(kwh_b, kosten_b)
    speicher_vergleich = [{"variante": "A", **var_a}, {"variante": "B", **var_b}]

# Visualisierung und Ausgabe

st.subheader("📊 Simulationsergebnisse")
col1, col2, col3 = st.columns(3)
col1.metric("Anlagenleistung", f"{anlagenleistung:.1f} kWp")
col2.metric(
    "Ertrag/Eigenverbrauch",
    f"{ertrag:,.0f} kWh / {verbrauchter_pv_strom:,.0f} kWh",
)
speicher_anzeige = f"{speicher_kwh_basis} kWh" if speicher else ""
col3.metric("Speichergröße", speicher_anzeige)

col4, col5, col6 = st.columns(3)
col4.metric(
    "Verbrauch/gedeckt durch PV",
    f"{verbrauch:,.0f} kWh / {verbrauchter_pv_strom:,.0f} kWh",
)
col5.metric("Investition", f"{investition_gesamt:,.0f} €")
col6.metric("Amortisation", f"{amortisation:.1f} Jahre")

col7, col8, col9 = st.columns(3)
col7.metric("Ersparnis (Eigenverbrauch)", f"{verbrauchter_pv_strom * strompreis:,.0f} €/Jahr")
col8.metric("Ersparnis (Einspeisung)", f"{einspeisung * 0.08:,.0f} €/Jahr")
col9.metric("20-Jahres-Rendite", f"{rendite20:,.0f} €")

st.metric("CO₂-Einsparung", f"{co2_einsparung:,.0f} kg/Jahr")

# Kreisdiagramme
st.markdown(f"### 🧁 Autarkiegrad ({verbrauchter_pv_strom:,.0f} kWh PV-Strom von {verbrauch:,.0f} kWh Verbrauch)")
fig1, ax1 = plt.subplots(figsize=(3, 3))
autarkie = verbrauchter_pv_strom / verbrauch if verbrauch else 0
ax1.pie([autarkie, 1 - autarkie], labels=["PV-Strom", "Netzbezug"], autopct="%1.0f%%", colors=["#4CAF50", "#f44336"])
ax1.axis("equal")
st.pyplot(fig1)

st.markdown(f"### ☀️ Eigenverbrauchsanteil ({verbrauchter_pv_strom:,.0f} kWh von {ertrag:,.0f} kWh Ertrag)")
fig2, ax2 = plt.subplots(figsize=(3, 3))
verbrauchsanteil = verbrauchter_pv_strom / ertrag if ertrag else 0
ax2.pie([verbrauchsanteil, 1 - verbrauchsanteil], labels=["direkt genutzt", "Einspeisung"], autopct="%1.0f%%", colors=["#2196F3", "#FFC107"])
ax2.axis("equal")
st.pyplot(fig2)

# DSGVO-konformes Opt-in
zustimmung = st.checkbox("Ich stimme der Datenverarbeitung gemäß Datenschutzerklärung zu", value=False)

# Anfrage senden
if st.button("📩 Anfrage senden"):
    if not zustimmung:
        st.warning("Bitte stimmen Sie der Datenverarbeitung zu.")
    elif not validierte_adresse:
        st.warning("Bitte wählen Sie eine Adresse aus den Vorschlägen.")
    else:
        st.success("Anfrage erfolgreich simuliert – (Demo-Modus)")
        anfrage = {
            "name": name,
            "telefon": telefon,
            "adresse": validierte_adresse,
            "gebaeudetyp": gebaeudetyp,
            "eigentuemer": eigentuemer,
            "plz": plz,
            "verbrauch": verbrauch,
            "strompreis": strompreis,
            "speicher": speicher,
            "wallbox_geplant": wallbox_geplant,
            "wallbox_bestehend": wallbox_bestehend,
            "waermepumpe": waermepumpe,
            "heizstab": heizstab,
            "email": email,
            "dachflaeche": dachflaeche,
            "neigung": neigung,
            "ausrichtung": ausrichtung,
            "anlagenleistung_kwp": round(anlagenleistung, 1),
            "empfohlene_speichergröße": speicher_empf if speicher else "",
            "eigenverbrauch": round(eigenverbrauch, 2),
            "ertrag": round(ertrag),
            "ersparnis": round(ersparnis),
            "investition_gesamt": round(investition_gesamt),
            "investition_ohne_speicher": round(grundsystem),
            "amortisation": round(amortisation, 1),
            "rendite20": round(rendite20),
            "co2_einsparung": round(co2_einsparung),
            "speicher_vergleich": speicher_vergleich,
            "netzbetreiber": netzbetreiber
        }

        st.download_button("🗂 JSON-Daten", data=json.dumps(anfrage, indent=2), file_name="anfrage.json")

        from pdf_export import erstelle_pdf_varianten
        pfad = erstelle_pdf_varianten(anfrage)

        with open(pfad, "rb") as f:
            st.download_button("📄 Angebot als PDF", f, file_name="angebot.pdf")
