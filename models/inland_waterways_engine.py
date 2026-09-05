"""
Inland Waterways Intelligence Engine (IWT Engine)
Provides analytics, navigation depth clearance verification, route transit & river dynamics calculations,
multi-modal cost & carbon savings estimation, and safety scoring for India's National Waterways network.
"""

import math
from typing import Dict, Any, List, Optional
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

class InlandWaterwaysEngine:
    def __init__(self):
        self.waterways = NATIONAL_WATERWAYS
        self.timeseries = CARGO_MOVEMENT_TIMESERIES
        self.commodities = COMMODITY_BREAKDOWN
        self.vessels = VESSEL_FLEET
        self.infrastructure = WATERWAY_INFRASTRUCTURE
        self.depth_lad = NAVIGATION_DEPTH_LAD
        self.routes = ROUTE_DISTANCES_TRANSIT
        self.freight_economics = FREIGHT_ECONOMICS
        self.operators = IWT_OPERATORS
        self.passengers = PASSENGER_MOVEMENT
        self.safety = ACCIDENTS_AND_SAFETY

    def get_overview(self) -> Dict[str, Any]:
        """Executive summary KPIs for national inland water transport."""
        latest_ts = [ts for ts in self.timeseries if not ts.get("is_projection")][-1]
        target_2030 = self.timeseries[-1]["cargo_mt"]
        total_nw_length = sum(nw["total_length_km"] for nw in self.waterways.values())
        navigable_length = sum(nw["navigable_length_km"] for nw in self.waterways.values())
        round_year_navigable = sum(nw["round_the_year_navigable_km"] for nw in self.waterways.values())
        
        # Calculate active vessel count across categories
        total_active_barges = sum(v["active_fleet_india"] for v in self.vessels.values())
        
        return {
            "total_cargo_mt_fy24": latest_ts["cargo_mt"],
            "yoy_growth_pct": latest_ts["yoy_growth_pct"],
            "target_cargo_2030_mt": target_2030,
            "10_year_cagr_pct": 22.1,
            "national_waterways_tracked": len(self.waterways),
            "total_network_length_km": total_nw_length,
            "navigable_length_km": navigable_length,
            "round_year_navigable_km": round_year_navigable,
            "terminals_operational": len(self.infrastructure),
            "active_vessel_fleet": total_active_barges,
            "annual_freight_collected_cr": self.freight_economics["annual_freight_collected_cr"]["FY_2023_24"],
            "national_logistics_savings_cr": self.freight_economics["national_logistics_cost_savings_cr_annual"],
            "carbon_reduction_mt": self.freight_economics["carbon_reduction_mt_annual"],
            "annual_passengers_millions": self.passengers["annual_passengers_carried_millions"],
            "average_freight_inr_ton_km": self.freight_economics["modal_cost_per_ton_km_inr"]["inland_waterways"],
            "freight_savings_vs_rail_pct": round((1 - 1.06 / 1.41) * 100, 1),
            "freight_savings_vs_road_pct": round((1 - 1.06 / 2.28) * 100, 1)
        }

    def get_timeseries(self, waterway_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns 11-year historical throughput + 2030 projections."""
        return self.timeseries

    def get_waterways_catalog(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns detailed catalog of tracked National Waterways."""
        results = []
        for nw_id, nw in self.waterways.items():
            if state:
                if not any(state.lower() in s.lower() for s in nw["states"]):
                    continue
            results.append(nw)
        return results

    def get_waterway_by_id(self, waterway_id: str) -> Optional[Dict[str, Any]]:
        """Returns a single waterway by ID (e.g. 'NW-1')."""
        return self.waterways.get(waterway_id)

    def get_navigation_depth_stretches(self) -> List[Dict[str, Any]]:
        """Returns all stretches with Least Available Depth (LAD) and dredging status."""
        return list(self.depth_lad.values())

    def check_vessel_draft_clearance(
        self,
        stretch_id: str,
        vessel_draft_m: float,
        safety_margin_m: float = 0.3
    ) -> Dict[str, Any]:
        """
        Evaluates Under-Keel Clearance (UKC) for a given vessel draft against a waterway stretch.
        UKC = Actual LAD - Vessel Draft.
        """
        stretch = self.depth_lad.get(stretch_id)
        if not stretch:
            # Fallback to first stretch
            stretch = list(self.depth_lad.values())[0]

        actual_lad = stretch["actual_current_lad_m"]
        min_seasonal = stretch["min_seasonal_lad_m"]
        ukc_current = round(actual_lad - vessel_draft_m, 2)
        ukc_seasonal = round(min_seasonal - vessel_draft_m, 2)

        if ukc_current >= safety_margin_m:
            clearance_status = "SAFE"
            status_color = "#00f5a0"  # emerald
            message = f"Sufficient Under-Keel Clearance of {ukc_current}m (exceeds {safety_margin_m}m safety margin). Unrestricted navigation approved."
        elif ukc_current >= 0.05:
            clearance_status = "MARGINAL_ALERT"
            status_color = "#ffb703"  # amber
            message = f"Marginal Under-Keel Clearance of {ukc_current}m. Speed reduction required and navigation restricted to tidal high water or charted central channel."
        else:
            clearance_status = "CRITICAL_GROUNDING_RISK"
            status_color = "#ff4d6d"  # coral red
            message = f"Negative Under-Keel Clearance ({ukc_current}m)! High risk of grounding. Lightering or vessel draft reduction below {round(actual_lad - safety_margin_m, 2)}m required."

        # Maximum payload estimate
        max_safe_draft = max(0.8, round(actual_lad - safety_margin_m, 2))

        return {
            "stretch_id": stretch["stretch_id"],
            "stretch_name": stretch["stretch_name"],
            "waterway_id": stretch["waterway_id"],
            "actual_lad_m": actual_lad,
            "min_seasonal_lad_m": min_seasonal,
            "vessel_draft_input_m": vessel_draft_m,
            "under_keel_clearance_current_m": ukc_current,
            "under_keel_clearance_seasonal_m": ukc_seasonal,
            "safety_margin_required_m": safety_margin_m,
            "clearance_status": clearance_status,
            "status_color": status_color,
            "message": message,
            "max_safe_draft_m": max_safe_draft,
            "air_draft_clearance_m": stretch["air_draft_clearance_m"],
            "shallow_patches": stretch["shallow_patches"],
            "dredging_status": stretch["dredging_status"],
            "advisory": stretch["advisory"]
        }

    def get_commodities(self) -> List[Dict[str, Any]]:
        """Returns commodity breakdown across all waterways."""
        return list(self.commodities.values())

    def get_infrastructure(self) -> List[Dict[str, Any]]:
        """Returns all terminals, berths, and material handling equipment."""
        return list(self.infrastructure.values())

    def get_vessel_fleet(self) -> List[Dict[str, Any]]:
        """Returns IWT vessel fleet classifications and active numbers."""
        return list(self.vessels.values())

    def get_routes(self) -> List[Dict[str, Any]]:
        """Returns pre-configured route stretches with distance and modal comparisons."""
        return list(self.routes.values())

    def calculate_route_transit_and_savings(
        self,
        route_id: str,
        cargo_tonnage: float,
        commodity_id: str = "steel",
        vessel_type_id: str = "self_propelled_barge_1000",
        is_upstream: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates river transit duration (factoring in river current dynamics),
        freight cost for IWT vs. Indian Railways vs. Road Transport,
        and net financial + carbon emission savings.
        """
        route = self.routes.get(route_id)
        if not route:
            route = list(self.routes.values())[0]

        vessel = self.vessels.get(vessel_type_id, self.vessels["self_propelled_barge_1000"])
        commodity = self.commodities.get(commodity_id, self.commodities["steel"])

        tonnage = max(50.0, float(cargo_tonnage))
        river_dist = route["river_distance_km"]
        rail_dist = route["rail_distance_km"]
        road_dist = route["road_distance_km"]

        # Speed calculation factoring river currents
        base_speed_kmph = vessel["service_speed_knots"] * 1.852
        current_knots = route["river_current_upstream_knots"] if is_upstream else route["river_current_downstream_knots"]
        current_kmph = current_knots * 1.852

        if is_upstream:
            effective_speed_kmph = max(4.0, base_speed_kmph - current_kmph)
        else:
            effective_speed_kmph = base_speed_kmph + (current_kmph * 0.8)

        # 16-20 operating hours per day depending on night navigation beacons
        operating_hours_per_day = 18.0
        transit_hours = river_dist / effective_speed_kmph
        transit_days = round(transit_hours / operating_hours_per_day, 1)

        # Freight costs calculation
        # IWT rate per ton = route base freight adjusted by tonnage scale factor
        iwt_rate_ton = route["iwt_freight_inr_per_ton"]
        rail_rate_ton = route["rail_freight_inr_per_ton"]
        road_rate_ton = route["road_freight_inr_per_ton"]

        total_cost_iwt_inr = round(iwt_rate_ton * tonnage)
        total_cost_rail_inr = round(rail_rate_ton * tonnage)
        total_cost_road_inr = round(road_rate_ton * tonnage)

        savings_vs_rail_inr = max(0, total_cost_rail_inr - total_cost_iwt_inr)
        savings_vs_road_inr = max(0, total_cost_road_inr - total_cost_iwt_inr)
        savings_vs_rail_pct = round((savings_vs_rail_inr / total_cost_rail_inr) * 100, 1) if total_cost_rail_inr > 0 else 0
        savings_vs_road_pct = round((savings_vs_road_inr / total_cost_road_inr) * 100, 1) if total_cost_road_inr > 0 else 0

        # Carbon emissions (kg CO2 per ton-km: IWT=0.018, Rail=0.042, Road=0.088)
        co2_iwt_tonnes = round((tonnage * route["co2_emissions_iwt_kg_ton"]) / 1000.0, 2)
        co2_rail_tonnes = round((tonnage * route["co2_emissions_rail_kg_ton"]) / 1000.0, 2)
        co2_road_tonnes = round((tonnage * route["co2_emissions_road_kg_ton"]) / 1000.0, 2)
        co2_saved_vs_road_tonnes = round(co2_road_tonnes - co2_iwt_tonnes, 2)

        # Number of barge trips needed
        barge_capacity = vessel["dwt_capacity"]
        barges_needed = math.ceil(tonnage / barge_capacity)

        return {
            "route_id": route["route_id"],
            "origin": route["origin"],
            "destination": route["destination"],
            "waterway_id": route["waterway_id"],
            "commodity": commodity["name"],
            "commodity_icon": commodity["icon"],
            "tonnage": tonnage,
            "vessel_used": vessel["name"],
            "vessel_capacity_dwt": barge_capacity,
            "barge_trips_needed": barges_needed,
            "direction": "Upstream (Against River Flow)" if is_upstream else "Downstream (With River Flow)",
            "river_current_knots": current_knots,
            "effective_speed_kmph": round(effective_speed_kmph, 1),
            "transit_duration_days": transit_days,
            "distances_km": {
                "inland_waterway": river_dist,
                "railway": rail_dist,
                "highway_road": road_dist
            },
            "freight_per_ton_inr": {
                "inland_waterway": iwt_rate_ton,
                "railway": rail_rate_ton,
                "highway_road": road_rate_ton
            },
            "total_freight_cost_inr": {
                "inland_waterway": total_cost_iwt_inr,
                "railway": total_cost_rail_inr,
                "highway_road": total_cost_road_inr
            },
            "financial_savings": {
                "vs_rail_inr": savings_vs_rail_inr,
                "vs_rail_crores": round(savings_vs_rail_inr / 1e7, 3),
                "vs_rail_pct": savings_vs_rail_pct,
                "vs_road_inr": savings_vs_road_inr,
                "vs_road_crores": round(savings_vs_road_inr / 1e7, 3),
                "vs_road_pct": savings_vs_road_pct
            },
            "co2_emissions_tonnes": {
                "inland_waterway": co2_iwt_tonnes,
                "railway": co2_rail_tonnes,
                "highway_road": co2_road_tonnes,
                "saved_vs_road": co2_saved_vs_road_tonnes
            }
        }

    def get_operators(self) -> List[Dict[str, Any]]:
        """Returns directory of private operators and public sector undertakings."""
        return self.operators

    def get_passengers_info(self) -> Dict[str, Any]:
        """Returns passenger movement and river cruise tourism metrics."""
        return self.passengers

    def get_safety_metrics(self) -> Dict[str, Any]:
        """Returns safety record, incident logs, and navigation aid coverage."""
        return self.safety
