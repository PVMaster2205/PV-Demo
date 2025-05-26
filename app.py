import streamlit as st
import json

st.set_page_config(page_title="PV-Angebotsrechner", layout="wide")

st.title("PV-Angebotsrechner Demo")

# Eingaben
plz = st.text_input("Postleitzahl")
verbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=500, max_value=15000, value=5000)
strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.1, max_value=1.0, value=0.35)
speicher = st.checkbox("Speicher gewünscht?")
wallbox = st.checkbox("Wallbox vorhanden?")
waermepumpe = st.checkbox("Wärmepumpe vorhanden?")
heizstab = st.checkbox("Heizstab vorhanden?")
email = st.text_input("Ihre E-Mail-Adresse")

# Berechnung
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

eigenverbrauch = 0.3
if speicher:
    eigenverbrauch += 0.3
if wallbox:
    eigenverbrauch += 0.1
if waermepumpe:
    eigenverbrauch += 0.1

eigenverbrauch = min(eigenverbrauch, 0.95)
ertrag = 1000 * (verbrauch / 0.7 / 1000)
ersparnis = ertrag * eigenverbrauch * strompreis
amortisation = 8000 / ersparnis if ersparnis else 0

# Ergebnisse
st.subheader("Simulationsergebnis")
st.metric("Ertrag (kWh/Jahr)", f"{ertrag:.0f}")
st.metric("Eigenverbrauchsanteil", f"{eigenverbrauch*100:.0f}%")
st.metric("Ersparnis (€ / Jahr)", f"{ersparnis:,.0f}")
st.metric("Empfohlene Speichergröße", speicher_empf)
st.metric("Amortisation (Jahre)", f"{amortisation:.1f}")

# PDF & Anfrage
if st.button("Anfrage senden"):
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
        "empfohlene_speichergröße": speicher_empf,
        "eigenverbrauch": round(eigenverbrauch, 2),
        "ertrag": round(ertrag),
        "ersparnis": round(ersparnis),
        "amortisation": round(amortisation, 1),
        "netzbetreiber": "unbekannt"  # Optional: ergänzen, wenn du Netzbetreiberlogik hast
    }

    # JSON-Download
    st.download_button("🗂 Anfrage als JSON herunterladen", data=json.dumps(anfrage, indent=2), file_name="anfrage.json")

    # 📄 PDF-Download vorbereiten
    from pdf_export import erstelle_pdf_varianten
    pfad = erstelle_pdf_varianten(anfrage)

    with open(pfad, "rb") as f:
        st.download_button("📄 Angebot als PDF herunterladen", f, file_name="angebot.pdf")
