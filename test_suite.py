"""
End-to-End Automated Test Suite for SeaSphere
Validates domain data, ML models, optimization engines, and REST API endpoints.
"""

import os
import unittest
import json
import numpy as np
import pandas as pd

from data.maritime_knowledge import EAST_COAST_PORTS, ORIGIN_PORTS, VESSEL_CLASSES, STEEL_PLANTS, COMMODITIES, ALL_MAJOR_PORTS, find_major_port
from models.forecaster import FreightForecaster
from models.port_traffic_forecaster import PortTrafficForecaster
from models.port_weather_forecaster import PortWeatherForecaster
from optimizer.vessel_selector import VesselSelector
from optimizer.charter_recommender import CharterRecommender
from optimizer.landed_cost_calculator import LandedCostCalculator
from simulation.scenario_simulator import ScenarioSimulator
from models.inland_waterways_engine import InlandWaterwaysEngine
import app as flask_app_module

class TestSeaSphere(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forecaster = FreightForecaster()
        cls.port_forecaster = PortTrafficForecaster()
        cls.weather_forecaster = PortWeatherForecaster()
        cls.vessel_selector = VesselSelector()
        cls.charter_recommender = CharterRecommender()
        cls.landed_calculator = LandedCostCalculator()
        cls.scenario_simulator = ScenarioSimulator(cls.forecaster, cls.landed_calculator, cls.vessel_selector)
        cls.iwt_engine = InlandWaterwaysEngine()
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
        self.assertIn(b"SeaSphere", res.data)

    def test_09_major_ports_data_integrity(self):
        """Verify Indian Major Ports data integrity and consistency."""
        self.assertGreaterEqual(len(ALL_MAJOR_PORTS), 12)
        self.assertIn("deendayal", ALL_MAJOR_PORTS)
        self.assertIn("paradip", ALL_MAJOR_PORTS)
        self.assertIn("jl_nehru", ALL_MAJOR_PORTS)

        # Check aliases
        kandla_port = find_major_port("Kandla")
        self.assertIsNotNone(kandla_port)
        self.assertEqual(kandla_port["id"], "deendayal")

        jnpt_port = find_major_port("JNPT")
        self.assertIsNotNone(jnpt_port)
        self.assertEqual(jnpt_port["id"], "jl_nehru")

        tuticorin_port = find_major_port("Tuticorin")
        self.assertIsNotNone(tuticorin_port)
        self.assertEqual(tuticorin_port["id"], "vo_chidambaranar")

        # Verify 33-year historical dataset exists and loads
        history_path = os.path.join(os.path.dirname(__file__), "data", "port_traffic_timeseries_1990_2023.csv")
        self.assertTrue(os.path.exists(history_path))
        df_hist = pd.read_csv(history_path)
        self.assertEqual(len(df_hist), 33)
        self.assertEqual(float(df_hist["total_mt"].iloc[-1]), 784.30)

        # Verify FY 2022-23 cargo breakdown exists and sums
        breakdown_path = os.path.join(os.path.dirname(__file__), "data", "port_cargo_traffic_2022_23.csv")
        self.assertTrue(os.path.exists(breakdown_path))
        df_break = pd.read_csv(breakdown_path)
        all_ports_row = df_break[df_break["port"] == "All Ports"].iloc[0]
        self.assertEqual(int(all_ports_row["grand_total_000t"]), 784305)

    def test_10_port_traffic_forecaster(self):
        """Test port traffic forecast inference, confidence intervals, and metrics."""
        # Test national total forecast
        fc_total = self.port_forecaster.get_traffic_forecast("total_mt")
        self.assertIsNotNone(fc_total)
        self.assertEqual(fc_total["port_id"], "total_mt")
        self.assertIn("forecast_horizons", fc_total)
        self.assertEqual(len(fc_total["forecast_horizons"]), 7)

        # Confidence intervals check: P10 <= P50 <= P90
        for item in fc_total["forecast_horizons"]:
            p10 = item["lower_p10"]
            p50 = item["predicted_p50"]
            p90 = item["upper_p90"]
            self.assertLessEqual(p10, p50, f"P10 ({p10}) should be <= P50 ({p50})")
            self.assertLessEqual(p50, p90, f"P50 ({p50}) should be <= P90 ({p90})")

        # Test individual port (Paradip)
        fc_paradip = self.port_forecaster.get_traffic_forecast("paradip")
        self.assertEqual(fc_paradip["port_id"], "paradip")
        self.assertGreater(fc_paradip["model_metrics"]["r2"], 0.95)

        # Test rankings
        rankings = self.port_forecaster.get_port_rankings()
        self.assertGreaterEqual(rankings["total_ports"], 12)
        top1 = rankings["rankings"][0]
        self.assertEqual(top1["rank"], 1)
        self.assertIn(top1["port_id"], ["deendayal", "paradip"])

    def test_11_port_traffic_rest_endpoints(self):
        """Verify port traffic REST API endpoints return HTTP 200 and valid data."""
        # 1. Traffic History
        res = self.client.get("/api/ports/traffic/history?port=all")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        res_single = self.client.get("/api/ports/traffic/history?port=deendayal")
        self.assertEqual(res_single.status_code, 200)
        self.assertEqual(len(res_single.get_json()["data"]["historical"]), 33)

        # 2. Traffic Forecast
        res_fc = self.client.get("/api/ports/traffic/forecast?port=paradip")
        self.assertEqual(res_fc.status_code, 200)
        self.assertEqual(res_fc.get_json()["status"], "success")

        # 3. Cargo Breakdown
        res_bk = self.client.get("/api/ports/traffic/breakdown")
        self.assertEqual(res_bk.status_code, 200)
        self.assertEqual(res_bk.get_json()["status"], "success")

        # 4. Port Rankings
        res_rk = self.client.get("/api/ports/ranking")
        self.assertEqual(res_rk.status_code, 200)
        self.assertEqual(res_rk.get_json()["status"], "success")

        # 5. Port Catalog
        res_cat = self.client.get("/api/ports/all")
        self.assertEqual(res_cat.status_code, 200)
        self.assertEqual(res_cat.get_json()["status"], "success")

    def test_12_port_weather_intelligence(self):
        """Verify port weather forecaster engine and REST API endpoints."""
        # 1. Catalog
        ports = self.weather_forecaster.get_ports_catalog()
        self.assertEqual(len(ports), 7)
        port_names = [p["port_name"] for p in ports]
        self.assertIn("Paradip", port_names)
        self.assertIn("Dhamra", port_names)
        self.assertIn("Visakhapatnam", port_names)

        # 2. Port Forecast
        fc = self.weather_forecaster.get_port_forecast("paradip")
        self.assertEqual(fc["port_name"], "Paradip")
        self.assertEqual(len(fc["forecast_days"]), 30)
        self.assertIn("temperature_max_c", fc["forecast_days"][0])
        self.assertIn("max_wind_kmh", fc["forecast_days"][0])

        # 3. Weather Risk Score
        risk_score = self.weather_forecaster.compute_weather_risk_score()
        self.assertGreaterEqual(risk_score, 0.0)
        self.assertLessEqual(risk_score, 100.0)

        # 4. REST API: Forecast
        res_fc = self.client.get("/api/weather/forecast?port=paradip&days=7")
        self.assertEqual(res_fc.status_code, 200)
        data_fc = res_fc.get_json()["data"]
        self.assertEqual(len(data_fc["forecast_days"]), 7)

        # 5. REST API: Ports Catalog
        res_pts = self.client.get("/api/weather/ports")
        self.assertEqual(res_pts.status_code, 200)
        self.assertEqual(len(res_pts.get_json()["data"]), 7)

        # 6. REST API: Snapshot
        res_snap = self.client.get("/api/weather/snapshot?date=2026-08-04")
        self.assertEqual(res_snap.status_code, 200)
        self.assertEqual(res_snap.get_json()["data"]["ports_count"], 7)

        # 7. Health Check includes weather_forecaster
        res_h = self.client.get("/api/health")
        self.assertEqual(res_h.status_code, 200)
        self.assertEqual(res_h.get_json()["engines"]["weather_forecaster"], "active")

    def test_13_inland_waterways_knowledge(self):
        """Verify all 13 IWT data categories exist and maintain strict schema integrity."""
        from data.inland_waterways_knowledge import (
            NATIONAL_WATERWAYS,
            CARGO_MOVEMENT_TIMESERIES,
            COMMODITY_BREAKDOWN,
            VESSEL_FLEET,
            WATERWAY_INFRASTRUCTURE,
            NAVIGATION_DEPTH_LAD,
            ROUTE_DISTANCES_TRANSIT,
            FREIGHT_ECONOMICS,
            IWT_OPERATORS,
            PASSENGER_MOVEMENT,
            ACCIDENTS_AND_SAFETY
        )

        # 1. Cargo Movement & Time-Series
        self.assertGreaterEqual(len(CARGO_MOVEMENT_TIMESERIES), 11)
        latest_historical = [t for t in CARGO_MOVEMENT_TIMESERIES if not t.get("is_projection")][-1]
        self.assertGreaterEqual(latest_historical["cargo_mt"], 130.0)
        self.assertEqual(CARGO_MOVEMENT_TIMESERIES[-1]["year"], 2030)

        # 2. Cargo by Commodity
        for comm_key in ["coal", "fly_ash", "iron_ore", "steel", "cement", "sand_aggregates"]:
            self.assertIn(comm_key, COMMODITY_BREAKDOWN)
            self.assertGreater(COMMODITY_BREAKDOWN[comm_key]["annual_tonnage_mt"], 0.0)

        # 3. National Waterways & Navigable Stretches
        for nw_key in ["NW-1", "NW-2", "NW-3", "NW-4", "NW-5", "NW-86", "NW-97"]:
            self.assertIn(nw_key, NATIONAL_WATERWAYS)
            nw = NATIONAL_WATERWAYS[nw_key]
            self.assertGreater(nw["total_length_km"], 0)
            self.assertGreater(nw["navigable_length_km"], 0)
            self.assertLessEqual(nw["round_the_year_navigable_km"], nw["total_length_km"])

        # 4. Vessel Fleet
        self.assertIn("self_propelled_barge_1000", VESSEL_FLEET)
        self.assertIn("push_tow_dumb_barge_flotilla", VESSEL_FLEET)
        self.assertGreater(VESSEL_FLEET["self_propelled_barge_2000"]["dwt_capacity"], 1500)

        # 5. Waterway Infrastructure & Terminals
        self.assertIn("mmt_varanasi", WATERWAY_INFRASTRUCTURE)
        self.assertIn("mmt_haldia", WATERWAY_INFRASTRUCTURE)
        self.assertIn("pankpal_terminal", WATERWAY_INFRASTRUCTURE)
        self.assertGreater(WATERWAY_INFRASTRUCTURE["mmt_varanasi"]["quay_length_m"], 100)

        # 6. Navigation Depth (LAD) 5-Star Monitor
        self.assertIn("NW1_HAL_FRK", NAVIGATION_DEPTH_LAD)
        self.assertIn("NW5_PNK_PRD", NAVIGATION_DEPTH_LAD)
        self.assertGreater(NAVIGATION_DEPTH_LAD["NW1_HAL_FRK"]["actual_current_lad_m"], 2.0)

        # 7. Route Distances & Transit Dynamics
        self.assertIn("haldia_to_varanasi", ROUTE_DISTANCES_TRANSIT)
        self.assertIn("kalinganagar_to_paradip", ROUTE_DISTANCES_TRANSIT)
        r = ROUTE_DISTANCES_TRANSIT["haldia_to_varanasi"]
        self.assertGreater(r["river_distance_km"], r["rail_distance_km"])

        # 8. Freight Tariffs & Economics
        self.assertLess(
            FREIGHT_ECONOMICS["modal_cost_per_ton_km_inr"]["inland_waterways"],
            FREIGHT_ECONOMICS["modal_cost_per_ton_km_inr"]["railways"]
        )

        # 9. Private Companies & PSUs
        self.assertGreaterEqual(len(IWT_OPERATORS), 7)

        # 10. Passenger Movement & Safety
        self.assertGreater(PASSENGER_MOVEMENT["annual_passengers_carried_millions"], 50.0)
        self.assertEqual(ACCIDENTS_AND_SAFETY["fatalities"], 0)

    def test_14_inland_waterways_engine_calculations(self):
        """Verify calculations for Under-Keel Clearance, river flow dynamics, and modal cost savings."""
        # 1. Under-Keel Clearance (UKC) checks
        safe_res = self.iwt_engine.check_vessel_draft_clearance("NW1_HAL_FRK", vessel_draft_m=2.2, safety_margin_m=0.3)
        self.assertEqual(safe_res["clearance_status"], "SAFE")
        self.assertGreaterEqual(safe_res["under_keel_clearance_current_m"], 0.3)

        shallow_res = self.iwt_engine.check_vessel_draft_clearance("NW1_VRN_PRY", vessel_draft_m=1.5, safety_margin_m=0.3)
        self.assertIn(shallow_res["clearance_status"], ["MARGINAL_ALERT", "CRITICAL_GROUNDING_RISK"])

        grounding_res = self.iwt_engine.check_vessel_draft_clearance("NW1_VRN_PRY", vessel_draft_m=2.5, safety_margin_m=0.3)
        self.assertEqual(grounding_res["clearance_status"], "CRITICAL_GROUNDING_RISK")

        # 2. Upstream vs Downstream River Current Dynamics
        up_calc = self.iwt_engine.calculate_route_transit_and_savings("haldia_to_varanasi", cargo_tonnage=5000, is_upstream=True)
        down_calc = self.iwt_engine.calculate_route_transit_and_savings("haldia_to_varanasi", cargo_tonnage=5000, is_upstream=False)
        self.assertGreater(up_calc["transit_duration_days"], down_calc["transit_duration_days"])

        # 3. Freight Savings vs Rail and Road
        self.assertGreater(up_calc["financial_savings"]["vs_rail_inr"], 0)
        self.assertGreater(up_calc["financial_savings"]["vs_road_inr"], up_calc["financial_savings"]["vs_rail_inr"])
        self.assertGreater(up_calc["co2_emissions_tonnes"]["saved_vs_road"], 0)

    def test_15_inland_waterways_api_endpoints(self):
        """Verify all IWT REST endpoints respond with HTTP 200 and valid JSON schemas."""
        # 1. Overview
        res = self.client.get("/api/iwt/overview")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["data"]["total_cargo_mt_fy24"], 133.0)

        # 2. Time-series
        res = self.client.get("/api/iwt/timeseries")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.get_json()["data"]), 11)

        # 3. Waterways catalog & detail
        res = self.client.get("/api/iwt/waterways")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.get_json()["data"]), 7)

        res_dt = self.client.get("/api/iwt/waterway/NW-1")
        self.assertEqual(res_dt.status_code, 200)
        self.assertEqual(res_dt.get_json()["data"]["id"], "NW-1")

        # 4. Depth LAD & Draft Check POST
        res = self.client.get("/api/iwt/depth-lad")
        self.assertEqual(res.status_code, 200)

        res_chk = self.client.post("/api/iwt/depth-check", json={"stretch_id": "NW1_HAL_FRK", "vessel_draft_m": 2.2})
        self.assertEqual(res_chk.status_code, 200)
        self.assertEqual(res_chk.get_json()["data"]["clearance_status"], "SAFE")

        # 5. Commodities, Infrastructure, Vessels
        for endpoint in ["commodities", "infrastructure", "vessels", "routes", "operators", "passengers", "safety"]:
            res = self.client.get(f"/api/iwt/{endpoint}")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json()["status"], "success")

        # 6. Route Calculation POST
        res_calc = self.client.post("/api/iwt/route-calc", json={
            "route_id": "kalinganagar_to_paradip",
            "cargo_tonnage": 10000,
            "commodity_id": "steel",
            "is_upstream": False
        })
        self.assertEqual(res_calc.status_code, 200)
        calc_data = res_calc.get_json()["data"]
        self.assertGreater(calc_data["financial_savings"]["vs_rail_crores"], 0)

        # 7. Health check reports inland_waterways_engine active
        res_h = self.client.get("/api/health")
        self.assertEqual(res_h.status_code, 200)
        self.assertEqual(res_h.get_json()["engines"]["inland_waterways_engine"], "active")

    def test_16_ai_procurement_copilot(self):
        """Verify AI Procurement Copilot natural query parsing and executive decision output."""
        from optimizer.copilot_engine import ProcurementCopilot
        copilot = ProcurementCopilot(
            self.forecaster, self.vessel_selector, self.charter_recommender,
            self.landed_calculator, flask_app_module.risk_scorer, self.iwt_engine
        )
        
        # Test query parsing
        parsed = copilot.parse_query("150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai")
        self.assertEqual(parsed["commodity_id"], "coking_coal")
        self.assertEqual(parsed["cargo_tonnage"], 150000.0)
        self.assertEqual(parsed["origin_id"], "hay_point")
        self.assertEqual(parsed["plant_id"], "sail_rourkela")
        self.assertEqual(parsed["vessel_class"], "Capesize")

        # Test decision generation
        result = copilot.generate_recommendation("150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai")
        self.assertEqual(result["status"], "success")
        strategy = result["strategy"]
        self.assertEqual(strategy["discharge_port"], "Dhamra Port")
        self.assertEqual(strategy["vessel_class"], "Capesize")
        self.assertGreater(strategy["estimated_freight_usd_ton"], 10.0)
        self.assertGreater(strategy["expected_saving_crore"], 1.0)
        self.assertTrue(len(strategy["recommended_laycan"]) > 5)

        # Test Why reasoning
        why = result["why_reasoning"]
        self.assertGreaterEqual(len(why), 3)
        self.assertTrue(any("draft" in w.lower() for w in why))
        self.assertTrue(any("rail" in w.lower() for w in why))

    def test_17_early_warning_alert_engine(self):
        """Verify proactive early warning alert engine generation across 4 risk vectors."""
        from optimizer.alert_engine import EarlyWarningEngine
        alert_engine = EarlyWarningEngine(
            self.forecaster, self.weather_forecaster, self.port_forecaster, flask_app_module.risk_scorer
        )
        alerts_data = alert_engine.get_active_alerts()
        self.assertEqual(alerts_data["status"], "success")
        self.assertGreaterEqual(alerts_data["total_active_alerts"], 4)

        # Verify 4 alert types exist
        types = [a["type"] for a in alerts_data["alerts"]]
        self.assertIn("PORT_ALERT", types)
        self.assertIn("WEATHER_ALERT", types)
        self.assertIn("FREIGHT_ALERT", types)
        self.assertIn("FUEL_ALERT", types)

        # Verify Primary Directive
        directive = alerts_data["primary_directive"]
        self.assertIn("72 hours", directive["headline"])
        self.assertEqual(directive["urgency_hours"], 72)

    def test_18_modal_evacuation_comparison(self):
        """Verify side-by-side Rail vs IWT multi-modal evacuation calculations."""
        res = self.landed_calculator.compare_rail_vs_iwt(
            plant_id="sail_rourkela",
            port_id="paradip",
            cargo_tonnage=15000,
            commodity_id="coking_coal"
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("rail", res)
        self.assertIn("iwt", res)
        self.assertGreater(res["rail"]["cost_inr_ton"], res["iwt"]["cost_inr_ton"])
        self.assertGreater(res["savings"]["savings_lakhs"], 0)
        self.assertGreater(res["savings"]["co2_reduction_pct"], 50.0)
        self.assertIn("IWT", res["recommendation_badge"])

    def test_19_new_rest_endpoints(self):
        """Verify REST APIs for Copilot, Early Warnings, and Modal Comparison."""
        # 1. Copilot Query Endpoint
        res_cp = self.client.post("/api/copilot/query", json={
            "query": "150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai"
        })
        self.assertEqual(res_cp.status_code, 200)
        cp_data = res_cp.get_json()["data"]
        self.assertEqual(cp_data["strategy"]["discharge_port"], "Dhamra Port")
        self.assertGreater(cp_data["strategy"]["expected_saving_crore"], 0)

        # 2. Early Warnings Endpoint
        res_ew = self.client.get("/api/alerts/active")
        self.assertEqual(res_ew.status_code, 200)
        ew_data = res_ew.get_json()["data"]
        self.assertGreaterEqual(len(ew_data["alerts"]), 4)
        self.assertIn("72 hours", ew_data["primary_directive"]["headline"])

        # 3. Modal Compare Endpoint
        res_mc = self.client.post("/api/optimizer/modal-compare", json={
            "plant_id": "sail_rourkela",
            "port_id": "dhamra",
            "cargo_tonnage": 20000
        })
        self.assertEqual(res_mc.status_code, 200)
        mc_data = res_mc.get_json()["data"]
        self.assertIn("recommendation_badge", mc_data)

        # 4. Health check includes new engines
        res_h = self.client.get("/api/health")
        self.assertEqual(res_h.status_code, 200)
        engines = res_h.get_json()["engines"]
        self.assertEqual(engines["copilot_engine"], "active")
        self.assertEqual(engines["early_warning_engine"], "active")

    def test_20_copilot_user_data_collection_and_multi_strategy(self):
        """Verify Copilot accepts custom user parameters and returns 3 diverse strategic options and comparison matrix."""
        res = self.client.post("/api/copilot/query", json={
            "query": "Custom data collection query",
            "parameters": {
                "commodity_id": "thermal_coal",
                "cargo_tonnage": 75000,
                "plant_id": "sail_durgapur",
                "origin_id": "taboneo",
                "vessel_class": "Panamax",
                "lead_days": 35,
                "is_iwt_query": True
            }
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        
        # Verify custom user parameters honored
        self.assertEqual(data["strategy"]["cargo_tonnage"], 75000)
        self.assertIn("Durgapur", data["strategy"]["plant_name"])
        self.assertEqual(data["strategy"]["vessel_class"], "Panamax")

        # Verify 3 diverse strategy options returned
        self.assertIn("strategy_options", data)
        self.assertEqual(len(data["strategy_options"]), 3)
        option_ids = [opt["id"] for opt in data["strategy_options"]]
        self.assertIn("cost_optimal", option_ids)
        self.assertIn("fast_track", option_ids)
        self.assertIn("green_multimodal", option_ids)

        # Verify Decision Matrix Table returned
        self.assertIn("comparison_matrix", data)
        self.assertGreaterEqual(len(data["comparison_matrix"]), 7)

    def test_21_database_persistence_and_live_ingestion(self):
        """Verify SQLAlchemy database persistence and live market tick insertion."""
        from data.db_engine import db_manager
        from data.data_ingestion import live_ingestion_engine

        # Verify DB connection & stats
        stats = db_manager.get_database_stats()
        self.assertIn("engine", stats)
        self.assertGreaterEqual(stats["market_records_total"], 2000)
        self.assertGreaterEqual(stats["weather_records_total"], 100)

        # Ingest a live market tick
        tick = live_ingestion_engine.ingest_live_market_tick()
        self.assertIsNotNone(tick)
        self.assertTrue(tick["is_live"])
        self.assertIn("freight_aus_paradip_cape", tick)

        # Verify Forecaster reflects dynamic database
        fc = self.forecaster.forecast_route("freight_aus_paradip_cape")
        self.assertIsNotNone(fc)
        self.assertGreater(fc["current_spot_rate"], 0)

    def test_22_data_sync_and_status_apis(self):
        """Verify /api/data/status and /api/data/sync REST endpoints."""
        # 1. Test status API
        res_status = self.client.get("/api/data/status")
        self.assertEqual(res_status.status_code, 200)
        data_s = res_status.get_json()["data"]
        self.assertIn("database", data_s)
        self.assertIn("ingestion", data_s)

        # 2. Test manual sync API
        res_sync = self.client.post("/api/data/sync")
        self.assertEqual(res_sync.status_code, 200)
        data_sync = res_sync.get_json()["data"]
        self.assertIn("weather_records_updated", data_sync)
        self.assertGreater(data_sync["weather_records_updated"], 0)
        self.assertIsNotNone(data_sync["latest_market_tick"])

        # 3. Test logs API
        res_logs = self.client.get("/api/data/logs")
        self.assertEqual(res_logs.status_code, 200)
        logs = res_logs.get_json()["data"]
        self.assertGreaterEqual(len(logs), 1)

if __name__ == "__main__":
    unittest.main()

