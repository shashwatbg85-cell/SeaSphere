"""
Vessel Selection & Port Draft Feasibility Optimizer.
Calculates dynamic arrival draft based on actual cargo parcel deadweight:
Arrival Draft = Ballast Draft + (Design Draft - Ballast Draft) * (Cargo Tonnage / Typical DWT)
Accurately evaluates draft clearance, lightering penalties, and economies of scale.
"""

from data.maritime_knowledge import EAST_COAST_PORTS, VESSEL_CLASSES

class VesselSelector:
    def __init__(self):
        self.ports = EAST_COAST_PORTS
        self.vessels = VESSEL_CLASSES

    def evaluate_vessel_options(self, destination_port_id, cargo_tonnage, commodity_id="coking_coal", base_freight_rate_cape=16.5):
        """
        Evaluates all vessel classes for feasibility and landed unit freight ($/MT).
        Returns ranked list of vessels with feasibility status, dynamic operating draft clearance, and unit freight.
        """
        port = self.ports.get(destination_port_id, self.ports["paradip"])
        port_draft = port["max_draft_meters"]
        port_dwt = port["max_dwt"]
        
        results = []
        
        for vessel_name, spec in self.vessels.items():
            design_draft = spec["design_draft_meters"]
            ballast_draft = spec.get("ballast_draft_meters", design_draft * 0.55)
            typical_dwt = spec["typical_dwt"]
            cost_factor = spec["freight_cost_factor"]
            
            # Base freight calculation scaled by vessel size efficiency
            estimated_ocean_freight = round(base_freight_rate_cape * cost_factor, 2)
            
            # Realistic dynamic arrival draft calculation based on cargo parcel size
            utilization = min(1.0, max(0.5, cargo_tonnage / typical_dwt))
            operating_draft = round(ballast_draft + (design_draft - ballast_draft) * utilization, 2)
            
            # Draft and berthing feasibility checks
            draft_clearance = round(port_draft - operating_draft, 2)
            is_direct_berth_capable = (port_draft >= operating_draft) and (port_dwt >= (cargo_tonnage * 0.9))
            requires_lightering = not is_direct_berth_capable and port.get("lightering_required", False)
            
            lightering_surcharge = port.get("lightering_cost_usd_ton", 0.0) if requires_lightering else 0.0
            total_sea_freight = round(estimated_ocean_freight + lightering_surcharge, 2)
            
            # Parcel capacity fit
            parcels_needed = max(1, round(cargo_tonnage / typical_dwt, 1))
            
            status = "Optimal"
            reasons = []
            
            if is_direct_berth_capable:
                reasons.append(f"Full direct berthing clearance: {draft_clearance:+.1f}m under-keel safety margin (operating draft {operating_draft}m).")
            elif requires_lightering:
                status = "Restricted (Lightering Required)"
                reasons.append(f"Operating draft ({operating_draft}m) exceeds port draft ({port_draft}m) by {-draft_clearance:.1f}m. Requires offshore lightering (+${lightering_surcharge:.2f}/T).")
            else:
                status = "Infeasible (Draft Violation)"
                reasons.append(f"Port draft limit ({port_draft}m) strictly cannot accommodate vessel operating draft ({operating_draft}m).")

            # Check parcel volume fit
            if cargo_tonnage < typical_dwt * 0.55:
                if status == "Optimal":
                    status = "Suboptimal (Deadfreight Risk)"
                reasons.append(f"Cargo parcel ({cargo_tonnage:,.0f} MT) is too small for full utilization of {typical_dwt:,.0f} MT DWT.")
                
            results.append({
                "vessel_class": vessel_name,
                "status": status,
                "feasible": is_direct_berth_capable or (requires_lightering and port.get("lightering_required", False)),
                "design_draft_m": design_draft,
                "operating_draft_m": operating_draft,
                "port_draft_m": port_draft,
                "draft_clearance_m": draft_clearance,
                "typical_capacity_dwt": typical_dwt,
                "estimated_ocean_freight_usd_ton": estimated_ocean_freight,
                "lightering_usd_ton": lightering_surcharge,
                "effective_sea_freight_usd_ton": total_sea_freight,
                "voyages_required": parcels_needed,
                "notes": "; ".join(reasons)
            })

        # Rank feasible vessels by effective unit sea freight
        feasible_vessels = [v for v in results if v["feasible"]]
        feasible_vessels.sort(key=lambda x: x["effective_sea_freight_usd_ton"])
        
        best_vessel = feasible_vessels[0]["vessel_class"] if feasible_vessels else "Panamax"
        
        return {
            "destination_port": port["name"],
            "cargo_tonnage": cargo_tonnage,
            "best_recommended_vessel": best_vessel,
            "vessel_evaluations": results
        }
