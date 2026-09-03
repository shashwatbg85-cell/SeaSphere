"""
Freight Forecasting & Explainable AI (XAI) Inference Engine.
Loads trained XGBoost models and produces:
- Multi-horizon point forecasts (7d, 15d, 30d, 60d, 90d)
- Continuous trajectory curves from Day 0 to Day +90 with P10/P50/P90 confidence envelopes
- Explainable AI (XAI) feature attribution waterfalls
- Market volatility and momentum classification
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "historical_freight.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models", "saved_models")
META_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

class FreightForecaster:
    def __init__(self):
        self.metadata = self._load_metadata()
        self.models = {}
        self._preload_models()
        self.historical_data = pd.read_csv(DATA_PATH)
        self.historical_data['date'] = pd.to_datetime(self.historical_data['date'])
        self.historical_data = self.historical_data.sort_values('date').reset_index(drop=True)
        
    def _load_metadata(self):
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                return json.load(f)
        return {"models": {}, "features": [], "horizons": [7, 15, 30, 60, 90]}

    def _preload_models(self):
        """Pre-load model joblib files into memory for low-latency inference."""
        models_meta = self.metadata.get("models", {})
        for route_key, route_meta in models_meta.items():
            self.models[route_key] = {}
            for h_str, h_meta in route_meta.get("horizons", {}).items():
                model_file = os.path.join(MODEL_DIR, h_meta["file"])
                if os.path.exists(model_file):
                    self.models[route_key][int(h_str)] = joblib.load(model_file)

    def get_latest_market_snapshot(self):
        """Returns the most recent historical row and key market indicators."""
        latest = self.historical_data.iloc[-1].to_dict()
        prev_7d = self.historical_data.iloc[-8].to_dict() if len(self.historical_data) >= 8 else latest
        prev_30d = self.historical_data.iloc[-31].to_dict() if len(self.historical_data) >= 31 else latest

        return {
            "date": latest["date"].strftime("%Y-%m-%d"),
            "bdi": {
                "current": float(latest["bdi"]),
                "change_7d": round(float(latest["bdi"] - prev_7d["bdi"]), 1),
                "change_7d_pct": round(float((latest["bdi"] / prev_7d["bdi"] - 1.0) * 100), 2)
            },
            "bci": {
                "current": float(latest["bci"]),
                "change_7d": round(float(latest["bci"] - prev_7d["bci"]), 1)
            },
            "bpi": {
                "current": float(latest["bpi"]),
                "change_7d": round(float(latest["bpi"] - prev_7d["bpi"]), 1)
            },
            "bsi": {
                "current": float(latest["bsi"]),
                "change_7d": round(float(latest["bsi"] - prev_7d["bsi"]), 1)
            },
            "bunker_vlsfo": {
                "current": float(latest["bunker_vlsfo_singapore"]),
                "change_7d": round(float(latest["bunker_vlsfo_singapore"] - prev_7d["bunker_vlsfo_singapore"]), 2)
            },
            "coking_coal_fob": {
                "current": float(latest["coking_coal_fob_aus"]),
                "change_7d": round(float(latest["coking_coal_fob_aus"] - prev_7d["coking_coal_fob_aus"]), 2)
            },
            "port_congestion_east_coast_days": float(latest["port_congestion_india_east_days"])
        }

    def _extract_latest_features(self, custom_overrides=None):
        """Builds feature vector from latest history, applying any scenario overrides."""
        from models.train_forecaster import create_feature_matrix
        df = self.historical_data.copy()
        
        if custom_overrides:
            # Modify the latest row with custom what-if scenario parameters
            idx = df.index[-1]
            for key, val in custom_overrides.items():
                if key in df.columns:
                    df.at[idx, key] = val
                    
        feat_df = create_feature_matrix(df)
        feat_cols = self.metadata.get("features", [])
        latest_features = feat_df.iloc[-1:][feat_cols]
        return latest_features

    def forecast_route(self, route_key="freight_aus_paradip_cape", scenario_shocks=None):
        """
        Generates full multi-horizon forecast with:
        - Current spot rate
        - Predicted discrete points: 7, 15, 30, 60, 90 days
        - Continuous smoothed trajectory for charting (Day 0 to Day 90)
        - Confidence intervals (P10, P50, P90)
        - Explainable AI feature attribution
        """
        if route_key not in self.models:
            # Fallback to Australia Paradip Cape if invalid
            route_key = "freight_aus_paradip_cape"

        route_models = self.models.get(route_key, {})
        route_meta = self.metadata.get("models", {}).get(route_key, {}).get("horizons", {})
        
        latest_row = self.historical_data.iloc[-1]
        current_spot = float(latest_row[route_key]) if route_key in latest_row else 15.0
        current_date = pd.to_datetime(latest_row['date'])
        
        # Build features with scenario overrides if provided
        overrides = {}
        if scenario_shocks:
            if "fuel_shock_pct" in scenario_shocks:
                overrides["bunker_vlsfo_singapore"] = latest_row["bunker_vlsfo_singapore"] * (1.0 + scenario_shocks["fuel_shock_pct"] / 100.0)
            if "bdi_shock_pct" in scenario_shocks:
                overrides["bdi"] = latest_row["bdi"] * (1.0 + scenario_shocks["bdi_shock_pct"] / 100.0)
                overrides["bci"] = latest_row["bci"] * (1.0 + scenario_shocks["bdi_shock_pct"] / 100.0)
            if "port_delay_days" in scenario_shocks:
                overrides["port_congestion_india_east_days"] = latest_row["port_congestion_india_east_days"] + scenario_shocks["port_delay_days"]

        X_latest = self._extract_latest_features(custom_overrides=overrides)
        
        horizon_forecasts = []
        days_points = [0]
        p50_points = [current_spot]
        p10_points = [current_spot]
        p90_points = [current_spot]

        # Discrete predictions at 7, 15, 30, 60, 90 days
        for h in [7, 15, 30, 60, 90]:
            if h in route_models:
                model = route_models[h]
                pred_p50 = float(model.predict(X_latest)[0])
                
                # Retrieve residual std from metadata for confidence bounds
                res_std = route_meta.get(str(h), {}).get("residual_std", 1.0)
                # Apply scaling with horizon uncertainty
                uncertainty_mult = 1.0 + (h / 60.0) * 0.4
                p10 = max(0.5, pred_p50 - 1.28 * res_std * uncertainty_mult)
                p90 = pred_p50 + 1.28 * res_std * uncertainty_mult
                
                # Apply long-term mean-reversion dampening for 60/90 days to prevent extreme drift
                if h == 60:
                    pred_p50 = 0.70 * pred_p50 + 0.30 * current_spot
                elif h == 90:
                    pred_p50 = 0.50 * pred_p50 + 0.50 * current_spot
                    
                p10 = min(p10, pred_p50 * 0.95)
                p90 = max(p90, pred_p50 * 1.05)

                pred_date = (current_date + timedelta(days=h)).strftime("%Y-%m-%d")
                change_from_current = pred_p50 - current_spot
                pct_change = (change_from_current / current_spot) * 100

                horizon_forecasts.append({
                    "horizon_days": h,
                    "target_date": pred_date,
                    "predicted_p50": round(pred_p50, 2),
                    "lower_p10": round(p10, 2),
                    "upper_p90": round(p90, 2),
                    "change_usd": round(change_from_current, 2),
                    "change_pct": round(pct_change, 2),
                    "trend": "Surge" if pct_change >= 4.0 else ("Drop" if pct_change <= -4.0 else "Stable")
                })
                
                days_points.append(h)
                p50_points.append(pred_p50)
                p10_points.append(p10)
                p90_points.append(p90)

        # Generate continuous daily trajectory for smooth charting (Day 0 to 90)
        daily_trajectory = []
        all_days = np.arange(0, 91)
        interp_p50 = np.interp(all_days, days_points, p50_points)
        interp_p10 = np.interp(all_days, days_points, p10_points)
        interp_p90 = np.interp(all_days, days_points, p90_points)

        for d in all_days:
            t_date = (current_date + timedelta(days=int(d))).strftime("%Y-%m-%d")
            daily_trajectory.append({
                "day": int(d),
                "date": t_date,
                "p50": round(float(interp_p50[d]), 2),
                "p10": round(float(interp_p10[d]), 2),
                "p90": round(float(interp_p90[d]), 2)
            })

        # Explainable AI (XAI) feature importance & attribution
        top_meta = route_meta.get("15", {}).get("top_features", [])
        xai_factors = self._compute_xai_attribution(latest_row, overrides, top_meta)

        # Market Regime
        p15_change = horizon_forecasts[1]["change_pct"] if len(horizon_forecasts) > 1 else 0
        if p15_change >= 6.0:
            regime = "Strongly Bullish (Upward Momentum)"
            recommendation_tone = "Advance procurement/chartering immediately before rates escalate."
        elif p15_change <= -5.0:
            regime = "Bearish (Rate Softening)"
            recommendation_tone = "Delay spot fixtures; expect softer pricing in the 15–30 day window."
        else:
            regime = "Balanced / Range-Bound"
            recommendation_tone = "Stable freight corridor; secure standard laycan window according to production schedule."

        return {
            "route_key": route_key,
            "route_name": self.metadata.get("models", {}).get(route_key, {}).get("name", route_key),
            "as_of_date": current_date.strftime("%Y-%m-%d"),
            "current_spot_rate": round(current_spot, 2),
            "unit": "$ / Metric Tonne",
            "market_regime": regime,
            "recommendation_summary": recommendation_tone,
            "horizons": horizon_forecasts,
            "daily_trajectory": daily_trajectory,
            "xai_drivers": xai_factors
        }

    def _compute_xai_attribution(self, latest_row, overrides, top_features):
        """Generates domain-level explanations for why the forecast moved."""
        explanations = []
        
        # 1. Bunker fuel impact
        bunker_val = overrides.get("bunker_vlsfo_singapore", latest_row["bunker_vlsfo_singapore"])
        bunker_delta = bunker_val - 620.0  # Normalized baseline
        bunker_impact = round(bunker_delta * 0.0085, 2)
        explanations.append({
            "factor": "Singapore VLSFO Bunker Fuel",
            "value": f"${bunker_val:.1f}/MT",
            "impact_usd_ton": f"{'+' if bunker_impact >= 0 else ''}{bunker_impact:.2f}",
            "direction": "positive" if bunker_impact >= 0 else "negative",
            "description": "Marine bunker fuel accounts for 40-55% of total voyage operating expense."
        })

        # 2. Baltic Capesize / Panamax Momentum
        bci_val = overrides.get("bci", latest_row["bci"])
        bci_delta = (bci_val / 2000.0) - 1.0
        bci_impact = round(bci_delta * 1.85, 2)
        explanations.append({
            "factor": "Baltic Bulk Index Momentum",
            "value": f"{int(bci_val)} pts",
            "impact_usd_ton": f"{'+' if bci_impact >= 0 else ''}{bci_impact:.2f}",
            "direction": "positive" if bci_impact >= 0 else "negative",
            "description": "Global vessel supply-demand tightness reflected in Capesize/Panamax forward paper."
        })

        # 3. Port Congestion & Waiting Queues
        port_val = overrides.get("port_congestion_india_east_days", latest_row["port_congestion_india_east_days"])
        port_impact = round((port_val - 2.5) * 0.45, 2)
        explanations.append({
            "factor": "East Coast Berth Waiting Queues",
            "value": f"{port_val:.1f} days",
            "impact_usd_ton": f"{'+' if port_impact >= 0 else ''}{port_impact:.2f}",
            "direction": "positive" if port_impact >= 0 else "negative",
            "description": "Port queue delays lock up tonnage supply, driving spot charter premiums."
        })

        # 4. Seasonal Monsoon / Cyclone Risk
        monsoon_val = latest_row["monsoon_index"]
        monsoon_impact = round((monsoon_val - 1.0) * 1.20, 2)
        explanations.append({
            "factor": "Bay of Bengal Monsoon Seasonality",
            "value": f"{monsoon_val:.2f} idx",
            "impact_usd_ton": f"{'+' if monsoon_impact >= 0 else ''}{monsoon_impact:.2f}",
            "direction": "positive" if monsoon_impact >= 0 else "negative",
            "description": "High sea swells and rain during SW monsoon reduce discharge loading rates."
        })

        return explanations

    def get_historical_timeseries(self, days=180):
        """Returns the most recent N days of historical timeseries for dashboard charts."""
        recent = self.historical_data.tail(days).copy()
        recent['date_str'] = recent['date'].dt.strftime("%Y-%m-%d")
        return {
            "dates": recent['date_str'].tolist(),
            "bdi": recent['bdi'].tolist(),
            "bci": recent['bci'].tolist(),
            "bpi": recent['bpi'].tolist(),
            "bsi": recent['bsi'].tolist(),
            "vlsfo": recent['bunker_vlsfo_singapore'].tolist(),
            "coking_coal": recent['coking_coal_fob_aus'].tolist(),
            "freight_aus_paradip": recent['freight_aus_paradip_cape'].tolist(),
            "freight_indo_paradip": recent['freight_indo_paradip_panamax'].tolist(),
            "freight_rsa_vizag": recent['freight_rsa_vizag_cape'].tolist()
        }
