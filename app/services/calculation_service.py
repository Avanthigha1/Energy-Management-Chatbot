"""
calculation_service.py
"""
from typing import Dict, Any
from app.services.data_service import DataService


def classify_pue(pue: float) -> str:
    """
    PUE efficiency tiers (industry standard):
      ≤ 1.2  → Excellent
      ≤ 1.5  → Efficient
      ≤ 2.0  → Moderate
      > 2.0  → Inefficient
    """
    if pue <= 1.2:
        return "Excellent"
    if pue <= 1.5:
        return "Efficient"
    if pue <= 2.0:
        return "Moderate"
    return "Inefficient"


class CalculationService:

    def __init__(self):
        self.data = DataService()

    # Total energy for one date

    def single_day(self, date: str) -> Dict[str, Any]:
        m = self.data.get_metrics(date)

        return {
            "text": f"Total energy on {date} is {m['total_energy_kwh']} kWh.",
            "kpis": {
                "total_energy_kwh": m["total_energy_kwh"],
                "it_load_kwh":      m["it_load_kwh"],
                "non_it_kwh":       m["non_it_kwh"],
                "pue":              m["pue"],
            },
            "insights": {
                "efficiency_status": classify_pue(m["pue"]),
                "spike_flag":        False,
            },
        }

    # Energy by floor 

    def floor_breakdown(self, date: str) -> Dict[str, Any]:
        floor_df = self.data.get_floor_breakdown(date)
        m        = self.data.get_metrics(date)
        total    = m["total_energy_kwh"]

        floors     = []
        text_lines = [f"Floor-wise energy for {date}:"]

        for _, row in floor_df.iterrows():
            pct = round(row["total_kwh"] / total * 100, 1) if total else 0
            floors.append({
                "floor":      str(row["floor"]),
                "total_kwh":  round(row["total_kwh"],  2),
                "it_kwh":     round(row["it_kwh"],     2),
                "non_it_kwh": round(row["non_it_kwh"], 2),
                "percentage": pct,
            })
            text_lines.append(f"• Floor {row['floor']}: {row['total_kwh']:.1f} kWh ({pct}%)")

        return {
            "text": "\n".join(text_lines),
            "kpis": {
                "total_energy_kwh": m["total_energy_kwh"],
                "it_load_kwh":      m["it_load_kwh"],
                "non_it_kwh":       m["non_it_kwh"],
                "pue":              m["pue"],
            },
            "insights": {
                "efficiency_status": classify_pue(m["pue"]),
                "spike_flag":        False,
            },
            "floor_data": floors,
        }

    # Compare two dates

    def comparison(self, date_1: str, date_2: str) -> Dict[str, Any]:
    
        date_1, date_2 = min(date_1, date_2), max(date_1, date_2)
        m1 = self.data.get_metrics(date_1)
        m2 = self.data.get_metrics(date_2)

        
        change = round(
            ((m2["total_energy_kwh"] - m1["total_energy_kwh"]) / m1["total_energy_kwh"]) * 100, 2
        ) if m1["total_energy_kwh"] else 0


        spike     = abs(change) > 15
        direction = "increased" if change > 0 else "decreased"
        prefix    = "ENERGY SPIKE DETECTED! " if spike else ""

        return {
            "text": (
                f"{prefix}Energy {direction} by {abs(change)}% "
                f"from {date_1} ({m1['total_energy_kwh']} kWh) "
                f"to {date_2} ({m2['total_energy_kwh']} kWh)."
            ),
            "kpis": {
                "total_energy_kwh": m2["total_energy_kwh"],
                "it_load_kwh":      m2["it_load_kwh"],
                "non_it_kwh":       m2["non_it_kwh"],
                "pue":              m2["pue"],
            },
            "insights": {
                "efficiency_status": classify_pue(m2["pue"]),
                "spike_flag":        spike,
            },
            "comparison": {
                "date_1":           date_1,
                "date_2":           date_2,
                "total_change_pct": change,
                "spike_detected":   spike,
            },
        }

    # PUE analysis

    def pue_analysis(self, date: str) -> Dict[str, Any]:
        m          = self.data.get_metrics(date)
        efficiency = classify_pue(m["pue"])

        interpretation = {
            "Excellent":   "World-class efficiency (PUE ≤ 1.2).",
            "Efficient":   "Good performance (PUE 1.2–1.5). Above industry average.",
            "Moderate":    "Industry average (PUE 1.5–2.0). Room for improvement.",
            "Inefficient": "Below average (PUE > 2.0). Audit recommended.",
        }

        return {
            "text": f"PUE for {date} is {m['pue']} ({efficiency}). {interpretation[efficiency]}",
            "kpis": {
                "total_energy_kwh": m["total_energy_kwh"],
                "it_load_kwh":      m["it_load_kwh"],
                "non_it_kwh":       m["non_it_kwh"],
                "pue":              m["pue"],
            },
            "insights": {
                "efficiency_status": efficiency,
                "spike_flag":        False,
            },
        }

    # Cooling ratio 

    def cooling_ratio(self, date: str) -> Dict[str, Any]:
        m = self.data.get_metrics(date)

        return {
        "text": f"Cooling ratio for {date} is {m['cooling_ratio']}. Cooling load: {m['cooling_load_kwh']} kWh, IT load: {m['it_load_kwh']} kWh.",
        "kpis": {
            "total_energy_kwh": m["total_energy_kwh"],
            "it_load_kwh":      m["it_load_kwh"],
            "non_it_kwh":       m["non_it_kwh"],
            "pue":              m["pue"],
        },
        "insights": {
            "efficiency_status": classify_pue(m["pue"]),
            "spike_flag":        False,
        },
    }