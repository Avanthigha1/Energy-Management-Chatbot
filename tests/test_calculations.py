"""
tests/test_calculations.py — Verifies all formulas are correct.

Run with: python -m pytest tests/ -v
Tests only the calculation logic.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.services.data_service import DataService
from app.services.calculation_service import CalculationService,classify_pue


class TestHelpers:
    def test_pue_excellent(self):
        assert classify_pue(1.1) == "Excellent"
        assert classify_pue(1.2) == "Excellent"

    def test_pue_efficient(self):
        assert classify_pue(1.3) == "Efficient"
        assert classify_pue(1.5) == "Efficient"

    def test_pue_moderate(self):
        assert classify_pue(1.6) == "Moderate"
        assert classify_pue(2.0) == "Moderate"

    def test_pue_inefficient(self):
        assert classify_pue(2.1) == "Inefficient"


class TestDataService:
    def setup_method(self):
        self.ds = DataService()

    def test_dates_loaded(self):
        assert "2026-02-10" in self.ds.available_dates
        assert "2026-02-11" in self.ds.available_dates
        assert "2026-02-12" in self.ds.available_dates

    def test_pue_formula(self):
        """PUE = Total / IT"""
        m = self.ds.get_metrics("2026-02-11")
        assert m["pue"] == round(m["total_energy_kwh"] / m["it_load_kwh"], 2)

    def test_non_it_formula(self):
        """Non-IT = Total - IT"""
        m = self.ds.get_metrics("2026-02-11")
        assert abs(m["non_it_kwh"] - (m["total_energy_kwh"] - m["it_load_kwh"])) < 0.01

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            self.ds.get_metrics("2025-01-01")


class TestCalculationService:
    def setup_method(self):
        self.cs = CalculationService()

    def test_single_day(self):
        r = self.cs.single_day("2026-02-11")
        assert "text" in r
        assert r["kpis"]["total_energy_kwh"] > 0
        assert r["kpis"]["pue"] > 0

    def test_floor_breakdown(self):
        r = self.cs.floor_breakdown("2026-02-11")
        assert "floor_data" in r
        assert len(r["floor_data"]) > 0

    def test_comparison_spike_rule(self):
        """Spike = |% change| > 15%"""
        r = self.cs.comparison("2026-02-10", "2026-02-12")
        change = abs(r["comparison"]["total_change_pct"])
        if change > 15:
            assert r["insights"]["spike_flag"] is True
        else:
            assert r["insights"]["spike_flag"] is False

    def test_pct_change_formula(self):
        """((Day2 - Day1) / Day1) × 100"""
        m1 = self.cs.data.get_metrics("2026-02-10")
        m2 = self.cs.data.get_metrics("2026-02-11")
        expected = round(
            ((m2["total_energy_kwh"] - m1["total_energy_kwh"]) / m1["total_energy_kwh"]) * 100, 2
        )
        r = self.cs.comparison("2026-02-10", "2026-02-11")
        assert r["comparison"]["total_change_pct"] == expected

    def test_pue_analysis(self):
        r = self.cs.pue_analysis("2026-02-12")
        assert r["kpis"]["pue"] > 0
        assert r["insights"]["efficiency_status"] in ["Excellent", "Efficient", "Moderate", "Inefficient"]

    def test_cooling_ratio(self):
        r = self.cs.cooling_ratio("2026-02-12")
        assert "text" in r
        assert r["kpis"]["pue"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
