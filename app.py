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

# Netzbetreiber laden
@st.cache_data
def lade_netzbetreiber():
    df = pd.read_csv("netzbetreiber.csv", dtype={"plz": str})
    return dict(zip(df["plz"], df["netzbetreiber"]))

netzbetreiber_lookup = lade_netzbetreiber()

st.title("🔆 PV-Angebotsrechner Demo")

# 📋 Kundendaten
title_block = st.container()
with title_block:
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
        except Exception as e:
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
        default_leistung = verbrauch / 950
        anlagenleistung = st.slider("Geplante PV-Anlagengröße (kWp)", min_value=2.7, max_value=19.8, value=round(default_leistung, 2), step=0.45)
        ausrichtung = "Süd"
        neigung = 30

email = st.text_input("📧 Ihre E-Mail-Adresse")

# Ertragsberechnung
faktor = {
    "Süd": 1.0,
    "Südost/Südwest": 0.95,
    "Ost/West": 0.85,
    "Nord": 0.7
}[ausrichtung]
ertrag = anlagenleistung * 950 * faktor

# Eigenverbrauch berechnen
eigenverbrauch = 0.3
if speicher: eigenverbrauch += 0.3
if wallbox_geplant or wallbox_bestehend: eigenverbrauch += 0.1
if waermepumpe: eigenverbrauch += 0.1
eigenverbrauch = min(eigenverbrauch, 0.95)

# Speicherempfehlung
if speicher:
    if verbrauch < 3000:
        speicher_empf = "3–4 kWh"
        speicher_kosten = 4000
    elif verbrauch < 5000:
        speicher_empf = "5–6 kWh"
        speicher_kosten = 6000
    elif verbrauch < 7000:
        speicher_empf = "6–8 kWh"
        speicher_kosten = 7500
    else:
        speicher_empf = "8–10 kWh"
        speicher_kosten = 9000
else:
    speicher_empf = "Nicht gewünscht"
    speicher_kosten = 0

# Investitionsschätzung (mit Komponenten + gestaffelten Montagekosten)
def montagekosten_pro_kwp(kWp):
    if kWp < 5:
        return 600
    elif kWp < 6:
        return 550
    elif kWp < 7:
        return 520
    elif kWp < 8:
        return 490
    elif kWp < 9:
        return 460
    elif kWp < 10:
        return 430
    elif kWp < 11:
        return 400
    elif kWp < 12:
        return 380
    elif kWp < 13:
        return 360
    elif kWp < 14:
        return 340
    elif kWp < 15:
        return 320
    else:
        return 300

komponenten = anlagenleistung * 700
montage = montagekosten_pro_kwp(anlagenleistung) * anlagenleistung
aufschlag = speicher_kosten
if wallbox_geplant: aufschlag += 1200
if waermepumpe: aufschlag += 4000
if heizstab: aufschlag += 800

zusatzkosten = 1200 + 800  # Gerüst + AC-Verkabelung

grundsystem = komponenten + montage
investition_gesamt = grundsystem + zusatzkosten + aufschlag

# Finanzen
ersparnis = ertrag * eigenverbrauch * strompreis
amortisation = investition_gesamt / ersparnis if ersparnis else 0

# Eigenverbrauchsberechnung
verbrauchter_pv_strom = min(ertrag * eigenverbrauch, verbrauch)
einspeisung = max(ertrag - verbrauchter_pv_strom, 0)
einspeiseverguetung = einspeisung * 0.08  # 8 Cent/kWh, anpassbar

ersparnis = verbrauchter_pv_strom * strompreis + einspeiseverguetung
amortisation = investition_gesamt / ersparnis if ersparnis else 0

# Ergebnisse visuell
st.subheader("📊 Simulationsergebnisse")
col1, col2, col3 = st.columns(3)
col1.metric("Anlagenleistung", f"{anlagenleistung:.1f} kWp")
col2.metric("Eigenverbrauchsanteil", f"{verbrauchter_pv_strom:,.0f} kWh / {verbrauch:,.0f} kWh")
col3.metric("Amortisation", f"{amortisation:.1f} Jahre")

col4, col5, col6 = st.columns(3)
col4.metric("Ertrag", f"{ertrag:,.0f} kWh")
col5.metric("Ersparnis", f"{ersparnis:,.0f} € / Jahr")
col6.metric("Investition", f"{investition_gesamt:,.0f} €")

# Kreisdiagramm Eigenverbrauchsdeckung
st.markdown("### 🧁 Verbrauchsdeckung durch PV")
fig, ax = plt.subplots(figsize=(3, 3))
verbrauchsdeckung = verbrauchter_pv_strom / verbrauch if verbrauch else 0
ax.pie([verbrauchsdeckung, 1 - verbrauchsdeckung], labels=["PV-Strom", "Netzbezug"], autopct="%1.0f%%", colors=["#4CAF50", "#f44336"])
ax.axis("equal")
st.pyplot(fig)

# Balkendiagramm Verbrauch vs Ertrag
st.markdown("### 📶 Verbrauch vs. PV-Ertrag")
df_chart = pd.DataFrame({
    "Kategorie": ["Stromverbrauch", "PV-Ertrag", "Eigenverbrauch"],
    "kWh": [verbrauch, ertrag, verbrauchter_pv_strom]
})
chart = alt.Chart(df_chart).mark_bar().encode(
    x=alt.X("Kategorie", sort=None),
    y="kWh",
    color=alt.Color("Kategorie", legend=None)
).properties(width=500, height=300)
st.altair_chart(chart, use_container_width=True)

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
            "empfohlene_speichergröße": speicher_empf,
            "eigenverbrauch": round(eigenverbrauch, 2),
            "ertrag": round(ertrag),
            "ersparnis": round(ersparnis),
            "investition_gesamt": round(investition_gesamt),
            "investition_ohne_speicher": round(grundsystem),
            "amortisation": round(amortisation, 1),
            "netzbetreiber": netzbetreiber
        }

        st.download_button("🗂 JSON-Daten", data=json.dumps(anfrage, indent=2), file_name="anfrage.json")

        from pdf_export import erstelle_pdf_varianten
        pfad = erstelle_pdf_varianten(anfrage)

        with open(pfad, "rb") as f:
            st.download_button("📄 Angebot als PDF", f, file_name="angebot.pdf")
