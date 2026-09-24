"""
Total Landed Procurement Cost (TLC) Calculator for Indian Steel Plants.
Holistically calculates:
- FOB Overseas Cargo Price
- Ocean Freight (predictive or spot)
- Bunker Adjustment Factor (BAF)
- Port Handling Dues & Tariffs
- Offshore Lightering Surcharges (for shallow ports like Haldia)
- Demurrage Risk (based on real-time berth waiting queue)
- Inland Indian Railways Freight to end steel plant (Rourkela, Bokaro, Durgapur, Bhilai, Vizag)
- Multi-port route optimization and savings comparison.
"""

from data.maritime_knowledge import EAST_COAST_PORTS, ORIGIN_PORTS, STEEL_PLANTS, COMMODITIES, VESSEL_CLASSES

class LandedCostCalculator:
    def __init__(self):
        self.ports = EAST_COAST_PORTS
        self.origins = ORIGIN_PORTS
        self.plants = STEEL_PLANTS
        self.commodities = COMMODITIES
        self.vessels = VESSEL_CLASSES

    def calculate_landed_cost(self, plant_id, origin_id, commodity_id, cargo_tonnage=150000, 
                              vessel_class="Capesize", custom_fob_price=None, custom_freight_rate=None,
                              bunker_vlsfo_price=650.0, extra_port_delay_days=0.0):
        """
        Calculates and compares the Total Landed Cost across all feasible East Coast discharge ports
        for a specified steel plant.
        """
        plant = self.plants.get(plant_id, self.plants["sail_rourkela"])
        origin = self.origins.get(origin_id, self.origins["hay_point"])
        commodity = self.commodities.get(commodity_id, self.commodities["coking_coal"])
        vessel = self.vessels.get(vessel_class, self.vessels["Capesize"])
        
        fob_price = custom_fob_price if custom_fob_price is not None else commodity["benchmark_price_usd_ton"]
        vessel_cost_factor = vessel["freight_cost_factor"]
        
        # Base ocean freight benchmark
        base_freight = custom_freight_rate if custom_freight_rate is not None else 16.50
        vessel_ocean_freight = base_freight * vessel_cost_factor
        
        # Bunker Adjustment Factor (BAF) calculation relative to $600 baseline
        baf_per_ton = max(0.0, (bunker_vlsfo_price - 600.0) * 0.0075)
        
        port_evaluations = []
        
        for port_id, rail_info in plant["preferred_ports"].items():
            port = self.ports.get(port_id)
            if not port:
                continue
                
            # Draft & Lightering feasibility
            port_draft = port["max_draft_meters"]
            vessel_draft = vessel["design_draft_meters"]
            
            is_draft_capable = port_draft >= vessel_draft
            requires_lightering = not is_draft_capable
            
            lightering_cost = port.get("lightering_cost_usd_ton", 0.0) if requires_lightering else 0.0
            if requires_lightering and lightering_cost == 0.0:
                lightering_cost = 6.80  # Default lightering surcharge if restricted
                
            # Port Handling & Dues
            port_dues = port["port_dues_usd_ton"]
            handling = port["handling_charges_usd_ton"]
            total_port_charges = round(port_dues + handling + lightering_cost, 2)
            
            # Demurrage Risk
            # Expected waiting days + simulated delay
            waiting_days = port["avg_waiting_days"] + extra_port_delay_days
            daily_demurrage = port["demurrage_usd_day"]
            total_demurrage_cost = waiting_days * daily_demurrage
            demurrage_per_ton = round(total_demurrage_cost / cargo_tonnage, 2)
            
            # Inland Rail Rake Freight
            rail_freight_per_ton = rail_info["rail_freight_usd_ton"]
            transit_days = rail_info["transit_days"]
            distance_km = rail_info["distance_km"]
            
            # Total Landed Unit Cost ($/MT)
            landed_unit_cost = round(
                fob_price + 
                vessel_ocean_freight + 
                baf_per_ton + 
                total_port_charges + 
                demurrage_per_ton + 
                rail_freight_per_ton, 
                2
            )
            
            total_procurement_cost = round(landed_unit_cost * cargo_tonnage, 2)
            
            port_evaluations.append({
                "port_id": port_id,
                "port_name": port["name"],
                "draft_clearance_m": round(port_draft - vessel_draft, 2),
                "is_draft_feasible": is_draft_capable,
                "requires_lightering": requires_lightering,
                "rail_distance_km": distance_km,
                "rail_transit_days": transit_days,
                "cost_breakdown_usd_ton": {
                    "fob_cargo": round(fob_price, 2),
                    "ocean_freight": round(vessel_ocean_freight, 2),
                    "bunker_surcharge_baf": round(baf_per_ton, 2),
                    "port_dues_and_handling": round(port_dues + handling, 2),
                    "lightering_transshipment": round(lightering_cost, 2),
                    "demurrage_risk": round(demurrage_per_ton, 2),
                    "inland_rail_freight": round(rail_freight_per_ton, 2)
                },
                "landed_cost_usd_ton": landed_unit_cost,
                "total_cost_usd": total_procurement_cost
            })

        # Rank routes by lowest landed cost
        port_evaluations.sort(key=lambda x: x["landed_cost_usd_ton"])
        best_port = port_evaluations[0]
        runner_up = port_evaluations[1] if len(port_evaluations) > 1 else best_port
        
        unit_savings_vs_suboptimal = round(runner_up["landed_cost_usd_ton"] - best_port["landed_cost_usd_ton"], 2)
        total_savings_vs_suboptimal = round(unit_savings_vs_suboptimal * cargo_tonnage, 2)

        return {
            "plant_name": plant["name"],
            "commodity_name": commodity["name"],
            "origin_name": origin["name"],
            "cargo_tonnage": cargo_tonnage,
            "vessel_class": vessel_class,
            "best_discharge_port": best_port["port_name"],
            "lowest_landed_cost_usd_ton": best_port["landed_cost_usd_ton"],
            "total_procurement_budget_usd": best_port["total_cost_usd"],
            "savings_vs_alternative_usd": total_savings_vs_suboptimal,
            "route_comparisons": port_evaluations
        }

    def compare_rail_vs_iwt(self, plant_id="sail_rourkela", port_id="paradip", cargo_tonnage=15000, commodity_id="coking_coal"):
        """
        Directly integrates Inland Waterways (IWT) with Maritime bulk procurement:
        Calculates side-by-side:
        - Rail: Cost ₹/ton, Transit days, CO2 kg/ton
        - IWT:  Cost ₹/ton, Transit days, CO2 kg/ton
        Returns recommendation badge, net financial savings (₹ Lakhs) and emission reductions (%).
        """
        plant = self.plants.get(plant_id, self.plants["sail_rourkela"])
        port = self.ports.get(port_id, self.ports["paradip"])
        tonnage = max(500.0, float(cargo_tonnage))
        usd_to_inr = 83.50

        # Rail metrics from plant preferred ports or benchmark
        rail_info = plant.get("preferred_ports", {}).get(port_id)
        if rail_info:
            rail_dist_km = rail_info["distance_km"]
            rail_cost_usd = rail_info["rail_freight_usd_ton"]
            rail_cost_inr = round(rail_cost_usd * usd_to_inr)
            rail_transit_days = rail_info["transit_days"]
        else:
            rail_dist_km = 450
            rail_cost_inr = 1420
            rail_transit_days = 2.0

        # Rail carbon factor: 0.042 kg CO2 / ton-km
        rail_co2_kg_ton = round(rail_dist_km * 0.042, 1)

        # IWT route determination based on port and geography
        if port_id in ["haldia", "kolkata"]:
            waterway_id = "NW-1 (Ganga-Hooghly)"
            corridor_name = "Haldia MMT → Durgapur / Barh / Varanasi Gateway"
            iwt_dist_km = 680
            # IWT tariff ~₹1.06/ton-km vs Rail ₹1.41/ton-km
            iwt_cost_inr = round(iwt_dist_km * 1.06 * 0.85)  # ₹612/ton
            iwt_transit_days = round(iwt_dist_km / (14.0 * 18.0 / 24.0 * 1.2), 1)  # ~4.2 days
            iwt_co2_kg_ton = round(iwt_dist_km * 0.018, 1)
        elif port_id in ["paradip", "dhamra"]:
            waterway_id = "NW-5 (Mahanadi-Brahmani)"
            corridor_name = f"{port['name']} → Pankpal / Kalinganagar / Talcher Corridor"
            iwt_dist_km = 185
            iwt_cost_inr = 215  # Benchmark from NW-5
            # Rapid delta barge: 1.2 days
            iwt_transit_days = 1.2
            iwt_co2_kg_ton = 3.3
        else:
            waterway_id = "Coastal & Inland Feeder"
            corridor_name = f"{port['name']} Coastal Barging to Inland Hub"
            iwt_dist_km = 320
            iwt_cost_inr = 420
            iwt_transit_days = 2.5
            iwt_co2_kg_ton = round(iwt_dist_km * 0.018, 1)

        # Savings calculations
        total_rail_cost_inr = round(rail_cost_inr * tonnage)
        total_iwt_cost_inr = round(iwt_cost_inr * tonnage)
        
        diff_inr = total_rail_cost_inr - total_iwt_cost_inr
        is_iwt_cheaper = diff_inr > 0
        savings_inr = abs(diff_inr)
        savings_lakhs = round(savings_inr / 100000.0, 1)
        savings_pct = round((savings_inr / total_rail_cost_inr) * 100.0, 1) if total_rail_cost_inr > 0 else 0.0

        total_rail_co2_tonnes = round((rail_co2_kg_ton * tonnage) / 1000.0, 1)
        total_iwt_co2_tonnes = round((iwt_co2_kg_ton * tonnage) / 1000.0, 1)
        co2_cut_pct = round(((rail_co2_kg_ton - iwt_co2_kg_ton) / rail_co2_kg_ton) * 100.0, 1) if rail_co2_kg_ton > 0 else 0.0

        # Recommendation badge & reason
        if is_iwt_cheaper and iwt_transit_days <= 5.0:
            recommended_mode = "IWT"
            badge = f"IWT — ₹{savings_lakhs} Lakh cheaper + {co2_cut_pct}% lower emissions"
            reason = (f"Inland Waterways ({waterway_id}) provides an optimal balance: ₹{rail_cost_inr - iwt_cost_inr}/ton "
                      f"freight discount saving ₹{savings_lakhs} Lakhs, with a {co2_cut_pct}% reduction in transport carbon.")
        else:
            recommended_mode = "Rail"
            badge = f"Rail Recommended — {rail_transit_days}d transit for time-critical blast furnace stock"
            reason = (f"Indian Railways rake dispatch recommended for urgent feed: saves {round(iwt_transit_days - rail_transit_days, 1)} days "
                      f"transit time to prevent blast furnace stock depletion.")

        return {
            "status": "success",
            "plant_id": plant_id,
            "plant_name": plant["name"],
            "port_id": port_id,
            "port_name": port["name"],
            "commodity_id": commodity_id,
            "cargo_tonnage": tonnage,
            "corridor_name": corridor_name,
            "waterway_id": waterway_id,
            "rail": {
                "distance_km": rail_dist_km,
                "cost_inr_ton": rail_cost_inr,
                "transit_days": rail_transit_days,
                "co2_kg_ton": rail_co2_kg_ton,
                "total_cost_inr": total_rail_cost_inr,
                "total_co2_tonnes": total_rail_co2_tonnes
            },
            "iwt": {
                "distance_km": iwt_dist_km,
                "cost_inr_ton": iwt_cost_inr,
                "transit_days": iwt_transit_days,
                "co2_kg_ton": iwt_co2_kg_ton,
                "total_cost_inr": total_iwt_cost_inr,
                "total_co2_tonnes": total_iwt_co2_tonnes
            },
            "savings": {
                "savings_inr": savings_inr,
                "savings_lakhs": savings_lakhs,
                "savings_pct": savings_pct,
                "co2_reduction_kg_ton": round(rail_co2_kg_ton - iwt_co2_kg_ton, 1),
                "co2_reduction_pct": co2_cut_pct
            },
            "recommended_mode": recommended_mode,
            "recommendation_badge": badge,
            "recommendation_reason": reason
        }

