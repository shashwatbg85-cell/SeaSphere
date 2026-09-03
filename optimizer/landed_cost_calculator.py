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
