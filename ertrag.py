# --- ertrag.py ---
"""Berechnungen rund um PV-Ertrag."""

from typing import Optional


def neigungsfaktor(neigung: float) -> float:
    """Einfache Abschätzung für den Einfluss der Dachneigung."""
    optimal = 30
    pro_grad = 0.005  # 0,5 % Verlust je Grad Abweichung
    return max(0.0, 1 - abs(neigung - optimal) * pro_grad)


def berechne_ertrag(anlage_kwp: float, ausrichtung: str, neigung: Optional[float]) -> float:
    """Berechnet den jährlichen PV-Ertrag in kWh."""
    faktor = {
        "Süd": 1.0,
        "Südost/Südwest": 0.95,
        "Ost/West": 0.85,
        "Nord": 0.7,
    }.get(ausrichtung, 1.0)

    n_faktor = neigungsfaktor(neigung) if neigung is not None else 1.0
    return anlage_kwp * 950 * faktor * n_faktor