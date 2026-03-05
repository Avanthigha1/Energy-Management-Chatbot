import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"

class DataService:# This makes sure CSV is loaded only once (not on every query)
    _instance = None

    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ready = False
        return cls._instance

    def __init__(self):
        if self._ready:
            return
        self._load()
        self._ready = True

    def _load(self):
        
        readings = pd.read_csv(DATA_DIR / "energy_meter_readings.csv")
        metadata = pd.read_csv(DATA_DIR / "meter_metadata.csv")
        self.df = readings.merge(metadata, on="meter_id", how="left")
        self.df["energy_kwh"] = self.df["energy_difference_wh"] / 1000
        self.df["date"] = pd.to_datetime(self.df["timestamp"]).dt.strftime("%Y-%m-%d")
        self.available_dates: List[str] = sorted(self.df["date"].unique().tolist())
        print(f"Data loaded — {len(self.df)} records, dates: {self.available_dates}")


    def _day(self, date: str) -> pd.DataFrame:
        """Get all rows for a single date. Raises error if date not found."""
        rows = self.df[self.df["date"] == date]
        if rows.empty:
            raise ValueError(f"Date '{date}' not found. Available: {self.available_dates}")
        return rows

    #  Core metrics 

    def get_metrics(self, date: str) -> Dict[str, Any]:

        day = self._day(date)

        total   = float(day["energy_kwh"].sum())
        it      = float(day[day["load_type"] == "IT"]["energy_kwh"].sum())
        cooling = float(day[day["meter_category"] == "CHILLER"]["energy_kwh"].sum())
        non_it  = total - it

        return {
            "date":             date,
            "total_energy_kwh": round(total,   2),
            "it_load_kwh":      round(it,      2),
            "non_it_kwh":       round(non_it,  2),
            "cooling_load_kwh": round(cooling, 2),
            "pue":              round(total / it,      2) if it else 0.0,
            "cooling_ratio":    round(cooling / it,    2) if it else 0.0,
        }

    def get_floor_breakdown(self, date: str) -> pd.DataFrame:
        """Returns energy grouped by floor with IT / Non-IT split."""
        day = self._day(date)

        totals = (
            day.groupby("floor")["energy_kwh"]
            .sum().reset_index()
            .rename(columns={"energy_kwh": "total_kwh"})
        )

        it_per_floor = (
            day[day["load_type"] == "IT"]
            .groupby("floor")["energy_kwh"]
            .sum().rename("it_kwh")
        )

        result = totals.set_index("floor").join(it_per_floor).fillna(0)
        result["non_it_kwh"] = result["total_kwh"] - result["it_kwh"]
        return result.reset_index()
