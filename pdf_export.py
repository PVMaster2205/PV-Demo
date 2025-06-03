# --- pdf_export.py ---
from fpdf import FPDF

def erstelle_pdf_varianten(anfrage_daten, pfad="angebot_varianten.pdf"):
    verbrauch = anfrage_daten["verbrauch"]
    strompreis = anfrage_daten["strompreis"]

    # Variante A: 5 kWh Speicher
    ev_a = 0.65
    preis_a = 6000
    ersparnis_a = verbrauch * ev_a * strompreis
    amort_a = preis_a / ersparnis_a
    kapitalrendite_a = ersparnis_a * 20 - preis_a

    # Variante B: 8 kWh Speicher
    ev_b = 0.75
    preis_b = 9000
    ersparnis_b = verbrauch * ev_b * strompreis
    amort_b = preis_b / ersparnis_b
    kapitalrendite_b = ersparnis_b * 20 - preis_b

    if kapitalrendite_b > kapitalrendite_a:
        empfehlung = "Variante B bietet die höhere Wirtschaftlichkeit über 20 Jahre – ideal bei langfristiger Planung."
    else:
        empfehlung = "Variante A bietet die bessere Rentabilität bei geringeren Investitionskosten."

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
    pdf.cell(0, 10, f"Stromverbrauch: {verbrauch} kWh", ln=True)
    pdf.cell(0, 10, f"Strompreis: {strompreis:.2f} EUR/kWh", ln=True)
    pdf.ln(8)

    # Speicher-Vergleich
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Speicher-Variantenvergleich", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Variante A: 5 kWh Speicher (ca. {preis_a} EUR)", ln=True)
    pdf.cell(0, 10, f"  -> Eigenverbrauch: {int(ev_a*100)}%, Ersparnis: {ersparnis_a:.0f} EUR/Jahr, Amortisation: {amort_a:.1f} Jahre", ln=True)
    pdf.cell(0, 10, f"Variante B: 8 kWh Speicher (ca. {preis_b} EUR)", ln=True)
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
