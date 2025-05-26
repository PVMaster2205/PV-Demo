from fpdf import FPDF

def erstelle_pdf_varianten(anfrage_daten, pfad="angebot_varianten.pdf"):
    # Berechnungen für Varianten
    verbrauch = anfrage_daten["verbrauch"]
    strompreis = anfrage_daten["strompreis"]

    # Variante A (z. B. 5 kWh Speicher)
    ev_a = 0.65
    ersparnis_a = verbrauch * ev_a * strompreis
    amort_a = 8000 / ersparnis_a

    # Variante B (z. B. 8 kWh Speicher)
    ev_b = 0.75
    ersparnis_b = verbrauch * ev_b * strompreis
    amort_b = 10000 / ersparnis_b

    empfehlung = (
        "Variante B ist wirtschaftlicher bei höherem Eigenverbrauch, "
        "sofern Budget und Platz vorhanden."
    )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Photovoltaik-Angebotsvorschau", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Projektdaten", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"PLZ: {anfrage_daten['plz']}", ln=True)
    pdf.cell(0, 10, f"Netzbetreiber: {anfrage_daten['netzbetreiber']}", ln=True)
    pdf.cell(0, 10, f"Stromverbrauch: {verbrauch} kWh", ln=True)
    pdf.cell(0, 10, f"Strompreis: {strompreis:.2f} EUR/kWh", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Speicher-Variantenvergleich", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Variante A: 5 kWh Speicher", ln=True)
    pdf.cell(0, 10, f"  -> Eigenverbrauch: {int(ev_a*100)}%, Ersparnis: {ersparnis_a:.0f} EUR/Jahr, Amortisation: {amort_a:.1f} Jahre", ln=True)
    pdf.cell(0, 10, "Variante B: 8 kWh Speicher", ln=True)
    pdf.cell(0, 10, f"  -> Eigenverbrauch: {int(ev_b*100)}%, Ersparnis: {ersparnis_b:.0f} EUR/Jahr, Amortisation: {amort_b:.1f} Jahre", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Empfehlung", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, empfehlung)
    pdf.ln(8)

    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 8, "Hinweis: Dies ist eine automatisch generierte Simulation. "
                        "Die tatsächliche Auslegung erfolgt nach technischer Prüfung.")

    pdf.output(pfad)
    return pfad
