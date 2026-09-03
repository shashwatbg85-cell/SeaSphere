"""
Crisis & What-If Scenario Stress-Testing Engine.
Simulates maritime logistics shocks:
1. Marine Bunker Fuel Shock (VLSFO price spike/collapse)
2. Monsoon Swells & Cyclone Delays (Demurrage surge)
3. Geopolitical Rerouting (Suez Canal closure / Cape of Good Hope rerouting)
4. Global Freight Tightness (Baltic Capesize/Panamax index surge)
Provides baseline vs. stressed comparisons and tactical mitigation recommendations.
"""

class ScenarioSimulator:
    def __init__(self, forecaster, landed_calculator, vessel_selector):
        self.forecaster = forecaster
        self.landed_calc = landed_calculator
        self.vessel_selector = vessel_selector

    def run_simulation(self, 
                       route_key="freight_aus_paradip_cape",
                       plant_id="sail_rourkela",
                       commodity_id="coking_coal",
                       cargo_tonnage=150000,
                       vessel_class="Capesize",
                       fuel_shock_pct=0.0,
                       port_delay_days=0.0,
                       bdi_shock_pct=0.0,
                       canal_rerouting_active=False):
        """
        Runs dual-pass calculation:
        - Baseline (standard current conditions)
        - Stressed Scenario (with user-applied shocks)
        Returns detailed comparison of unit rates, total procurement budgets, and tactical advice.
        """
        # Baseline Forecast
        base_forecast = self.forecaster.forecast_route(route_key=route_key)
        # Use projected 15-day fixture rate as benchmark
        base_spot = base_forecast["horizons"][1]["predicted_p50"] if len(base_forecast["horizons"]) > 1 else base_forecast["current_spot_rate"]
        
        # Stressed Forecast
        scenario_shocks = {
            "fuel_shock_pct": fuel_shock_pct,
            "port_delay_days": port_delay_days,
            "bdi_shock_pct": bdi_shock_pct
        }
        
        stressed_forecast = self.forecaster.forecast_route(route_key=route_key, scenario_shocks=scenario_shocks)
        stressed_model_spot = stressed_forecast["horizons"][1]["predicted_p50"] if len(stressed_forecast["horizons"]) > 1 else stressed_forecast["current_spot_rate"]
        
        # Add direct fuel and canal rerouting freight elasticity
        direct_fuel_impact = base_spot * (fuel_shock_pct * 0.0035)  # ~35% fuel share of voyage
        direct_bdi_impact = base_spot * (bdi_shock_pct * 0.0040)
        rerouting_freight_surcharge = 7.50 if canal_rerouting_active else 0.0
        
        stressed_spot_adj = round(max(base_spot * 0.5, stressed_model_spot + direct_fuel_impact + direct_bdi_impact + rerouting_freight_surcharge), 2)
        
        # Landed Cost - Baseline
        base_landed = self.landed_calc.calculate_landed_cost(
            plant_id=plant_id,
            origin_id="hay_point",
            commodity_id=commodity_id,
            cargo_tonnage=cargo_tonnage,
            vessel_class=vessel_class,
            custom_freight_rate=base_spot,
            bunker_vlsfo_price=650.0,
            extra_port_delay_days=0.0
        )
        
        # Landed Cost - Stressed
        stressed_vlsfo = 650.0 * (1.0 + fuel_shock_pct / 100.0)
        stressed_landed = self.landed_calc.calculate_landed_cost(
            plant_id=plant_id,
            origin_id="hay_point",
            commodity_id=commodity_id,
            cargo_tonnage=cargo_tonnage,
            vessel_class=vessel_class,
            custom_freight_rate=stressed_spot_adj,
            bunker_vlsfo_price=stressed_vlsfo,
            extra_port_delay_days=port_delay_days
        )
        
        # Delta Metrics
        unit_freight_delta = round(stressed_spot_adj - base_spot, 2)
        unit_landed_delta = round(stressed_landed["lowest_landed_cost_usd_ton"] - base_landed["lowest_landed_cost_usd_ton"], 2)
        total_procurement_delta = round(stressed_landed["total_procurement_budget_usd"] - base_landed["total_procurement_budget_usd"], 2)
        
        # Demurrage impact
        base_demurrage = base_landed["route_comparisons"][0]["cost_breakdown_usd_ton"]["demurrage_risk"]
        stressed_demurrage = stressed_landed["route_comparisons"][0]["cost_breakdown_usd_ton"]["demurrage_risk"]
        demurrage_delta = round(stressed_demurrage - base_demurrage, 2)
        
        # Mitigation Strategies
        mitigations = []
        if fuel_shock_pct >= 20.0:
            mitigations.append("Adopt Speed Slow-Steaming: Reducing vessel speed from 13.5 knots to 11.5 knots cuts daily fuel consumption by ~28%.")
            mitigations.append("Bunker Hedging: Execute forward paper bunker swap contracts (Sing 0.5% VLSFO) to cap fuel exposure.")
            
        if port_delay_days >= 3.0:
            mitigations.append(f"Diversion to Alternative Port: Consider routing via {stressed_landed['route_comparisons'][1]['port_name'] if len(stressed_landed['route_comparisons']) > 1 else 'Dhamra'} to avoid costly anchorage delays.")
            mitigations.append("24-Hour Notice of Readiness (NOR) renegotiation in charter party to extend laytime allowance.")
            
        if canal_rerouting_active:
            mitigations.append("Switch to Capesize via Cape of Good Hope: Larger parcel sizes (175k DWT) dilute the extra $7.50/T circumnavigation cost.")
            
        if bdi_shock_pct >= 25.0:
            mitigations.append("Contract of Affreightment (COA) Activation: Shift 40-50% of annual coking coal volume to long-term index-linked COAs with ceiling collars.")
            
        if not mitigations:
            mitigations.append("Conditions within normal operational tolerances. Maintain scheduled tender cycles.")

        return {
            "scenario_parameters": {
                "fuel_shock_pct": fuel_shock_pct,
                "port_delay_days": port_delay_days,
                "bdi_shock_pct": bdi_shock_pct,
                "canal_rerouting_active": canal_rerouting_active
            },
            "comparison": {
                "base_freight_usd_ton": round(base_spot, 2),
                "stressed_freight_usd_ton": round(stressed_spot_adj, 2),
                "freight_delta_usd_ton": unit_freight_delta,
                "freight_delta_pct": round((unit_freight_delta / base_spot) * 100, 2),
                
                "base_landed_usd_ton": base_landed["lowest_landed_cost_usd_ton"],
                "stressed_landed_usd_ton": stressed_landed["lowest_landed_cost_usd_ton"],
                "landed_delta_usd_ton": unit_landed_delta,
                
                "base_total_procurement_usd": base_landed["total_procurement_budget_usd"],
                "stressed_total_procurement_usd": stressed_landed["total_procurement_budget_usd"],
                "total_procurement_delta_usd": total_procurement_delta,
                
                "demurrage_delta_usd_ton": demurrage_delta,
                "demurrage_extra_cost_usd": round(demurrage_delta * cargo_tonnage, 2)
            },
            "best_port_baseline": base_landed["best_discharge_port"],
            "best_port_stressed": stressed_landed["best_discharge_port"],
            "mitigation_actions": mitigations
        }
