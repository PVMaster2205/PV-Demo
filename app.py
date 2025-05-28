# --- app.py ---
import streamlit as st
import json
import pandas as pd
import re

st.set_page_config(page_title="PV-Angebotsrechner", layout="wide")

# Netzbetreiber laden
@st.cache_data
def lade_netzbetreiber():
    df = pd.read_csv("netzbetreiber.csv", dtype={"plz": str})
    return dict(zip(df["plz"], df["netzbetreiber"]))

netzbetreiber_lookup = lade_netzbetreiber()

st.title("PV-Angebotsrechner Demo")

# Eingaben
plz = st.text_input("Postleitzahl")

netzbetreiber = "unbekannt"
if isinstance(plz, str) and plz.strip():
    if not re.fullmatch(r"\d{5}", plz.strip()):
        st.warning("Bitte geben Sie eine gültige 5-stellige deutsche Postleitzahl ein.")
        netzbetreiber = "ungültig"
    else:
        netzbetreiber = netzbetreiber_lookup.get(plz.strip(), "unbekannt")

verbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=500, max_value=15000, value=5000)
strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.1, max_value=1.0, value=0.35)

# Neue Dachdaten-Eingabe
mit_dachdaten = st.checkbox("Ich kenne Daten zur Dachfläche und -ausrichtung")

if mit_dachdaten:
    dachflaeche = st.number_input("Dachfläche nutzbar (m²)", min_value=5, max_value=200)
    neigung = st.slider("Dachneigung (Grad)", 0, 90, 30)
    ausrichtung = st.selectbox("Dachausrichtung", ["Süd", "Südost/Südwest", "Ost/West", "Nord"])
else:
    dachflaeche = None
    neigung = None
    ausrichtung = None

speicher = st.checkbox("Speicher gewünscht?")
wallbox = st.checkbox("Wallbox vorhanden?")
waermepumpe = st.checkbox("Wärmepumpe vorhanden?")
heizstab = st.checkbox("Heizstab vorhanden?")
email = st.text_input("Ihre E-Mail-Adresse")

# Ertragsberechnung
if dachflaeche:
    anlagenleistung = dachflaeche / 7
    faktor = {
        "Süd": 1.0,
        "Südost/Südwest": 0.95,
        "Ost/West": 0.85,
        "Nord": 0.7
    }[ausrichtung]
    ertrag = anlagenleistung * 950 * faktor
else:
    anlagenleistung = verbrauch / 950
    ertrag = anlagenleistung * 950

# Eigenverbrauch berechnen
eigenverbrauch = 0.3
if speicher: eigenverbrauch += 0.3
if wallbox: eigenverbrauch += 0.1
if waermepumpe: eigenverbrauch += 0.1
eigenverbrauch = min(eigenverbrauch, 0.95)

# Finanzen
ersparnis = ertrag * eigenverbrauch * strompreis
amortisation = 8000 / ersparnis if ersparnis else 0

# Speicherempfehlung
if speicher:
    if verbrauch < 3000:
        speicher_empf = "3–4 kWh"
    elif verbrauch < 5000:
        speicher_empf = "5–6 kWh"
    elif verbrauch < 7000:
        speicher_empf = "6–8 kWh"
    else:
        speicher_empf = "8–10 kWh"
else:
    speicher_empf = "Nicht gewünscht"

# Investitionsschätzung (nur PV)
grundpreis_kwp = 1300
invest_pv = anlagenleistung * grundpreis_kwp
aufschlag = 0
if speicher: aufschlag += 6000
if wallbox: aufschlag += 1200
if waermepumpe: aufschlag += 4000
if heizstab: aufschlag += 800
investition_gesamt = invest_pv + aufschlag

# Ergebnisse
st.subheader("Simulationsergebnis")
st.metric("Geplante Anlagenleistung", f"{anlagenleistung:.1f} kWp")
st.metric("Ertrag (kWh/Jahr)", f"{ertrag:.0f}")
st.metric("Eigenverbrauchsanteil", f"{eigenverbrauch*100:.0f}%")
st.metric("Ersparnis (€ / Jahr)", f"{ersparnis:,.0f}")
st.metric("Investition ohne Speicher", f"{invest_pv:,.0f} €")
st.metric("Gesamtkosten mit Extras", f"{investition_gesamt:,.0f} €")
st.metric("Empfohlene Speichergröße", speicher_empf)
st.metric("Amortisation (Jahre)", f"{amortisation:.1f}")

# DSGVO-konformes Opt-in
zustimmung = st.checkbox("Ich stimme der Datenverarbeitung gemäß Datenschutzerklärung zu", value=False)

# Anfrage senden
if st.button("Anfrage senden"):
    if not zustimmung:
        st.warning("Bitte stimmen Sie der Datenverarbeitung zu.")
    else:
        st.success("Anfrage erfolgreich simuliert – (Demo-Modus)")
        anfrage = {
            "plz": plz,
            "verbrauch": verbrauch,
            "strompreis": strompreis,
            "speicher": speicher,
            "wallbox": wallbox,
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
            "investition_ohne_speicher": round(invest_pv),
            "amortisation": round(amortisation, 1),
            "netzbetreiber": netzbetreiber
        }

        st.download_button("🗂 Anfrage als JSON herunterladen", data=json.dumps(anfrage, indent=2), file_name="anfrage.json")

        from pdf_export import erstelle_pdf_varianten
        pfad = erstelle_pdf_varianten(anfrage)

        with open(pfad, "rb") as f:
            st.download_button("📄 Angebot als PDF herunterladen", f, file_name="angebot.pdf")
