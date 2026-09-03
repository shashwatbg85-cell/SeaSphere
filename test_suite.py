"""
End-to-End Automated Test Suite for NAVI-STEEL
Validates domain data, ML models, optimization engines, and REST API endpoints.
"""

import os
import unittest
import json
import numpy as np
import pandas as pd

from data.maritime_knowledge import EAST_COAST_PORTS, ORIGIN_PORTS, VESSEL_CLASSES, STEEL_PLANTS, COMMODITIES
from models.forecaster import FreightForecaster
from optimizer.vessel_selector import VesselSelector
from optimizer.charter_recommender import CharterRecommender
from optimizer.landed_cost_calculator import LandedCostCalculator
from simulation.scenario_simulator import ScenarioSimulator
import app as flask_app_module

class TestNaviSteel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forecaster = FreightForecaster()
        cls.vessel_selector = VesselSelector()
        cls.charter_recommender = CharterRecommender()
        cls.landed_calculator = LandedCostCalculator()
        cls.scenario_simulator = ScenarioSimulator(cls.forecaster, cls.landed_calculator, cls.vessel_selector)
        cls.client = flask_app_module.app.test_client()

    def test_01_maritime_knowledge(self):
        """Verify port and vessel data integrity."""
        self.assertIn("paradip", EAST_COAST_PORTS)
        self.assertIn("visakhapatnam", EAST_COAST_PORTS)
        self.assertIn("haldia", EAST_COAST_PORTS)
        
        # Check draft restrictions
        self.assertGreaterEqual(EAST_COAST_PORTS["paradip"]["max_draft_meters"], 17.0)
        self.assertLessEqual(EAST_COAST_PORTS["haldia"]["max_draft_meters"], 9.0)
        self.assertTrue(EAST_COAST_PORTS["haldia"]["lightering_required"])
        
        # Check vessel classes
        self.assertIn("Capesize", VESSEL_CLASSES)
        self.assertIn("Panamax", VESSEL_CLASSES)
        self.assertGreater(VESSEL_CLASSES["Capesize"]["typical_dwt"], VESSEL_CLASSES["Panamax"]["typical_dwt"])

    def test_02_historical_data_exists(self):
        """Verify historical freight dataset exists and contains required features."""
        data_path = os.path.join(os.path.dirname(__file__), "data", "historical_freight.csv")
        self.assertTrue(os.path.exists(data_path), "historical_freight.csv must exist")
        
        df = pd.read_csv(data_path)
        self.assertGreater(len(df), 2000, "Should have over 2000 daily records")
        for col in ["bdi", "bci", "bpi", "bunker_vlsfo_singapore", "freight_aus_paradip_cape"]:
            self.assertIn(col, df.columns)

    def test_03_forecasting_engine(self):
        """Test multi-horizon probabilistic forecast and confidence intervals."""
        fc = self.forecaster.forecast_route("freight_aus_paradip_cape")
        self.assertIsNotNone(fc)
        self.assertIn("horizons", fc)
        self.assertEqual(len(fc["horizons"]), 5, "Must output 7, 15, 30, 60, 90 day horizons")
        
        # Check confidence intervals
        for h in fc["horizons"]:
            p10 = h["lower_p10"]
            p50 = h["predicted_p50"]
            p90 = h["upper_p90"]
            self.assertLessEqual(p10, p50, f"P10 ({p10}) must be <= P50 ({p50})")
            self.assertLessEqual(p50, p90, f"P50 ({p50}) must be <= P90 ({p90})")
            
        # Check daily trajectory continuity
        traj = fc["daily_trajectory"]
        self.assertEqual(len(traj), 91, "Daily trajectory should span Day 0 to 90")
        
        # Check Explainable AI drivers
        xai = fc["xai_drivers"]
        self.assertGreaterEqual(len(xai), 3, "Should provide at least 3 XAI drivers")

    def test_04_vessel_selector(self):
        """Test vessel selection and draft constraint enforcement."""
        # Deep port (Paradip) should favor Capesize for large 150k MT parcels
        eval_paradip = self.vessel_selector.evaluate_vessel_options("paradip", cargo_tonnage=150000)
        self.assertEqual(eval_paradip["best_recommended_vessel"], "Capesize")
        
        # Shallow port (Haldia) must flag Capesize draft restriction
        eval_haldia = self.vessel_selector.evaluate_vessel_options("haldia", cargo_tonnage=50000)
        haldia_cape = [v for v in eval_haldia["vessel_evaluations"] if v["vessel_class"] == "Capesize"][0]
        self.assertTrue(haldia_cape["lightering_usd_ton"] > 0 or not haldia_cape["feasible"])

    def test_05_charter_recommender(self):
        """Test charter strategy and optimal laycan window recommendations."""
        fc = self.forecaster.forecast_route("freight_aus_paradip_cape")
        strat = self.charter_recommender.recommend_charter_strategy(fc, cargo_tonnage=150000, max_lead_days=45)
        
        self.assertIn("market_action", strat)
        self.assertIn("optimal_laycan_window", strat)
        self.assertIn("contract_structures", strat)
        self.assertGreaterEqual(len(strat["contract_structures"]), 3)

    def test_06_landed_cost_calculator(self):
        """Test Total Landed Cost (TLC) calculations and multi-port ranking."""
        result = self.landed_calculator.calculate_landed_cost(
            plant_id="sail_rourkela",
            origin_id="hay_point",
            commodity_id="coking_coal",
            cargo_tonnage=150000,
            vessel_class="Capesize"
        )
        self.assertIsNotNone(result)
        self.assertIn("lowest_landed_cost_usd_ton", result)
        self.assertIn("route_comparisons", result)
        self.assertGreater(len(result["route_comparisons"]), 1)
        
        # Verify cost arithmetic
        best = result["route_comparisons"][0]
        breakdown = best["cost_breakdown_usd_ton"]
        expected_sum = (
            breakdown["fob_cargo"] +
            breakdown["ocean_freight"] +
            breakdown["bunker_surcharge_baf"] +
            breakdown["port_dues_and_handling"] +
            breakdown["lightering_transshipment"] +
            breakdown["demurrage_risk"] +
            breakdown["inland_rail_freight"]
        )
        self.assertAlmostEqual(best["landed_cost_usd_ton"], round(expected_sum, 2), places=1)

    def test_07_crisis_simulator(self):
        """Test crisis simulation and sensitivity deltas."""
        sim = self.scenario_simulator.run_simulation(
            route_key="freight_aus_paradip_cape",
            plant_id="sail_rourkela",
            commodity_id="coking_coal",
            cargo_tonnage=150000,
            fuel_shock_pct=30.0,
            port_delay_days=4.0
        )
        cmp = sim["comparison"]
        self.assertGreater(cmp["stressed_freight_usd_ton"], cmp["base_freight_usd_ton"])
        self.assertGreater(cmp["stressed_landed_usd_ton"], cmp["base_landed_usd_ton"])
        self.assertGreater(cmp["demurrage_extra_cost_usd"], 0)
        self.assertGreaterEqual(len(sim["mitigation_actions"]), 1)

    def test_08_rest_api_endpoints(self):
        """Verify all Flask REST endpoints respond with HTTP 200 and valid JSON."""
        # 1. Market Snapshot
        res = self.client.get("/api/market/snapshot")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # 2. Market History
        res = self.client.get("/api/market/history?days=30")
        self.assertEqual(res.status_code, 200)

        # 3. Forecast API
        res = self.client.get("/api/forecast?route=freight_aus_paradip_cape")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # 4. Vessel Optimizer API
        res = self.client.post("/api/optimizer/vessel", json={
            "port_id": "paradip",
            "cargo_tonnage": 150000
        })
        self.assertEqual(res.status_code, 200)

        # 5. Charter Recommender API
        res = self.client.post("/api/optimizer/charter", json={
            "route_key": "freight_aus_paradip_cape",
            "cargo_tonnage": 150000
        })
        self.assertEqual(res.status_code, 200)

        # 6. Landed Cost API
        res = self.client.post("/api/optimizer/landed-cost", json={
            "plant_id": "sail_rourkela",
            "commodity_id": "coking_coal",
            "cargo_tonnage": 150000
        })
        self.assertEqual(res.status_code, 200)

        # 7. Simulator API
        res = self.client.post("/api/simulator/run", json={
            "fuel_shock_pct": 20.0,
            "port_delay_days": 3.0
        })
        self.assertEqual(res.status_code, 200)

        # 8. Web Page View
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"NAVI-STEEL", res.data)

if __name__ == "__main__":
    unittest.main()
