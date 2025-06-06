# --- pdf_export.py ---
from fpdf import FPDF

def erstelle_pdf_varianten(anfrage_daten, pfad="angebot_varianten.pdf"):
    speicher_vergleich = anfrage_daten.get("speicher_vergleich", [])

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Photovoltaik-Angebotsvorschau", ln=True, align="C")
    pdf.ln(10)

    # Kundendaten
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Kundendaten", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Name: {anfrage_daten.get('name', '')}", ln=True)
    pdf.cell(0, 10, f"Telefon: {anfrage_daten.get('telefon', '')}", ln=True)
    pdf.cell(0, 10, f"Adresse: {anfrage_daten.get('adresse', '')}", ln=True)
    pdf.cell(0, 10, f"Gebäudetyp: {anfrage_daten.get('gebaeudetyp', '')}", ln=True)
    pdf.cell(0, 10, f"Eigentümerstatus: {anfrage_daten.get('eigentuemer', '')}", ln=True)
    pdf.ln(5)

    # Projektdaten
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Projektdaten", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"PLZ: {anfrage_daten['plz']}", ln=True)
    pdf.cell(0, 10, f"Netzbetreiber: {anfrage_daten['netzbetreiber']}", ln=True)
    pdf.cell(0, 10, f"Stromverbrauch: {anfrage_daten['verbrauch']} kWh", ln=True)
    pdf.cell(0, 10, f"Strompreis: {anfrage_daten['strompreis']:.2f} EUR/kWh", ln=True)
    pdf.ln(8)

    # Simulationsergebnisse aus der App
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Simulationsergebnisse", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Anlagenleistung: {anfrage_daten.get('anlagenleistung_kwp', '')} kWp", ln=True)
    if anfrage_daten.get('empfohlene_speichergröße'):
        pdf.cell(0, 10, f"Empfohlene Speichergröße: {anfrage_daten['empfohlene_speichergröße']}", ln=True)
    ev_prozent = int(anfrage_daten.get('eigenverbrauch', 0) * 100)
    pdf.cell(0, 10, f"Eigenverbrauch: {ev_prozent}%", ln=True)
    pdf.cell(0, 10, f"Ertrag: {anfrage_daten.get('ertrag', 0):,} kWh/Jahr", ln=True)
    pdf.cell(0, 10, f"Ersparnis: {anfrage_daten.get('ersparnis', 0):,} EUR/Jahr", ln=True)
    pdf.cell(0, 10, f"Investition (gesamt): {anfrage_daten.get('investition_gesamt', 0):,} EUR", ln=True)
    pdf.cell(0, 10, f"Investition ohne Speicher: {anfrage_daten.get('investition_ohne_speicher', 0):,} EUR", ln=True)
    pdf.cell(0, 10, f"Amortisation: {anfrage_daten.get('amortisation', 0)} Jahre", ln=True)
    pdf.cell(0, 10, f"20-Jahres-Rendite: {anfrage_daten.get('rendite20', 0):,} EUR", ln=True)
    # PDF generation uses Latin-1 encoding, so avoid special characters
    pdf.cell(0, 10, f"CO2-Einsparung: {anfrage_daten.get('co2_einsparung', 0):,} kg/Jahr", ln=True)
    pdf.ln(8)

    # Speicher-Vergleich
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Speicher-Variantenvergleich (20 Jahre)", ln=True)
    pdf.set_font("Arial", "", 12)
    if len(speicher_vergleich) >= 2:
        for v in speicher_vergleich:
            pdf.cell(0, 10, f"Variante {v.get('variante', '?')}: {v.get('kwh', '?')} kWh Speicher, ca. {int(v.get('preis', 0))} EUR", ln=True)
            pdf.cell(0, 10, f"  -> Eigenverbrauch: {int(v.get('ev', 0)*100)}%, Ersparnis: {v.get('ersparnis', 0):.0f} EUR/Jahr, Amortisation: {v.get('amortisation', 0):.1f} Jahre", ln=True)
            pdf.cell(0, 10, f"  -> 20-Jahres-Rendite: {v.get('rendite20', 0):,.0f} EUR", ln=True)
        pdf.ln(5)

        # Empfehlung
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Empfehlung", ln=True)
        pdf.set_font("Arial", "", 12)
        if speicher_vergleich[1]['rendite20'] > speicher_vergleich[0]['rendite20']:
            empfehlung = "Variante B (größerer Speicher) bietet über 20 Jahre die bessere Wirtschaftlichkeit."
        else:
            empfehlung = "Variante A (kleinerer Speicher) ist bei begrenztem Budget wirtschaftlich sinnvoller."
        pdf.multi_cell(0, 10, empfehlung)
    else:
        pdf.cell(0, 10, "Keine Vergleichsdaten verfügbar.", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 8, "Hinweis: Dies ist eine automatisch generierte Simulation. "
                        "Die tatsächliche Auslegung erfolgt nach technischer Prüfung.")

    pdf.output(pfad)
    return pfad
