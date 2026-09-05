"""
Composite Maritime Risk Index Scorer.
Calculates a 0-100 risk score based on:
1. Freight Volatility Risk (from rolling 14-day std of BDI/BCI)
2. Monsoon / Bay of Bengal Cyclone Seasonality Risk
3. Port Congestion Risk (East Coast berth waiting days)
4. Geopolitical Disruption Risk (Canal rerouting probability)
5. Bunker Fuel Volatility Risk (VLSFO price deviation from baseline)
Returns a traffic-light risk dashboard (Green/Amber/Red) with weighted scoring.
"""

class RiskScorer:
    """Maritime Procurement Risk Assessment Engine."""
    
    WEIGHTS = {
        "freight_volatility": 0.25,
        "monsoon_weather": 0.20,
        "port_congestion": 0.20,
        "geopolitical": 0.15,
        "bunker_fuel": 0.20
    }

    def __init__(self):
        pass

    def compute_risk_score(self, market_snapshot, scenario_overrides=None):
        """
        Computes composite risk score from latest market indicators.
        
        Args:
            market_snapshot: dict with keys: bdi, bci, bunker_vlsfo, 
                           port_congestion_days, monsoon_index, 
                           freight_vol_14d, canal_risk_active
            scenario_overrides: optional dict to override any field
        """
        data = dict(market_snapshot)
        if scenario_overrides:
            data.update(scenario_overrides)
            
        factors = {}
        
        # 1. Freight Volatility Risk (0-100)
        # Based on 14-day rolling std of BDI normalized against historical bounds
        bdi_vol = data.get("bdi_vol_14d", 45.0)
        # Historical range: 15 (calm) to 200 (extreme crisis)
        freight_risk = min(100, max(0, (bdi_vol - 15) / (200 - 15) * 100))
        factors["freight_volatility"] = {
            "label": "Freight Market Volatility",
            "score": round(freight_risk, 1),
            "value": f"σ={bdi_vol:.1f} pts",
            "description": "14-day rolling standard deviation of Baltic Dry Index"
        }
        
        # 2. Monsoon / Weather Risk (0-100)
        monsoon_idx = data.get("monsoon_index", 1.0)
        # Range: 0.5 (dry season) to 3.5 (peak cyclone/monsoon)
        monsoon_risk = min(100, max(0, (monsoon_idx - 0.5) / (3.5 - 0.5) * 100))
        factors["monsoon_weather"] = {
            "label": "Bay of Bengal Weather Risk",
            "score": round(monsoon_risk, 1),
            "value": f"{monsoon_idx:.2f} idx",
            "description": "Monsoon swell index affecting discharge rates and port operations"
        }
        
        # 3. Port Congestion Risk (0-100)
        congestion_days = data.get("port_congestion_days", 2.5)
        # Range: 1.0 (normal) to 8.0 (severe congestion)
        congestion_risk = min(100, max(0, (congestion_days - 1.0) / (8.0 - 1.0) * 100))
        factors["port_congestion"] = {
            "label": "East Coast Port Congestion",
            "score": round(congestion_risk, 1),
            "value": f"{congestion_days:.1f} days",
            "description": "Average berth waiting time across Paradip, Vizag, Haldia"
        }
        
        # 4. Geopolitical Disruption Risk (0-100)
        canal_active = data.get("canal_risk_active", False)
        bdi_current = data.get("bdi", 1800)
        # BDI above 2500 suggests tight global supply; canal risk amplifies
        geo_base = min(100, max(0, (bdi_current - 1200) / (3500 - 1200) * 80))
        if canal_active:
            geo_base = min(100, geo_base + 40)
        factors["geopolitical"] = {
            "label": "Geopolitical Route Disruption",
            "score": round(geo_base, 1),
            "value": "Active" if canal_active else "Normal",
            "description": "Risk of Suez/Red Sea disruption forcing Cape of Good Hope rerouting"
        }
        
        # 5. Bunker Fuel Volatility Risk (0-100)
        vlsfo = data.get("bunker_vlsfo", 650.0)
        # Baseline $600, high above $800, very high above $1000
        fuel_risk = min(100, max(0, (vlsfo - 500) / (1000 - 500) * 100))
        factors["bunker_fuel"] = {
            "label": "Marine Bunker Fuel Risk",
            "score": round(fuel_risk, 1),
            "value": f"${vlsfo:.0f}/MT",
            "description": "Singapore VLSFO 0.5% price deviation from procurement budget baseline"
        }
        
        # Composite Weighted Score
        composite = sum(
            factors[k]["score"] * self.WEIGHTS[k]
            for k in self.WEIGHTS
        )
        composite = round(composite, 1)
        
        # Traffic Light Classification
        if composite <= 30:
            level = "LOW"
            color = "green"
            advice = "Favorable procurement conditions. Execute scheduled tenders with standard risk parameters."
        elif composite <= 55:
            level = "MODERATE"
            color = "amber"
            advice = "Elevated uncertainty in freight markets. Consider split-parcel procurement and bunker hedging."
        elif composite <= 75:
            level = "HIGH"
            color = "coral"
            advice = "Significant supply chain stress detected. Accelerate critical procurements and activate contingency port diversions."
        else:
            level = "CRITICAL"
            color = "red"
            advice = "Extreme market conditions. Recommend emergency COA activation, slow-steaming mandates, and inventory buffer acceleration."
        
        return {
            "composite_score": composite,
            "risk_level": level,
            "risk_color": color,
            "advisory": advice,
            "factors": factors,
            "weights": self.WEIGHTS
        }
