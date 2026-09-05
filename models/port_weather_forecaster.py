"""
Port Metocean & Weather Intelligence Engine.
Loads hyper-local 30-day weather forecast data for Indian East Coast cargo ports:
Dhamra, Paradip, Visakhapatnam, Kolkata, Chennai, Kamarajar, and V.O. Chidambaranar.

Provides:
- Daily temperature, wind speed, precipitation, and WMO weather codes.
- Maritime operational impact assessments (crane gantry safety, bulk hatch moisture protection, lightering swell caution).
- Cross-port comparative metocean analysis for optimal vessel laycan routing.
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "data", "port_weather_forecast.json")
CSV_PATH = os.path.join(BASE_DIR, "data", "port_weather_forecast.csv")

PORT_ALIASES = {
    "dhamra": "Dhamra",
    "paradip": "Paradip",
    "visakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",
    "kolkata": "Kolkata",
    "haldia": "Kolkata",
    "smp_kolkata_haldia": "Kolkata",
    "chennai": "Chennai",
    "kamarajar": "Kamarajar",
    "ennore": "Kamarajar",
    "v.o.chidambaranar": "V.O.Chidambaranar",
    "vo_chidambaranar": "V.O.Chidambaranar",
    "voc": "V.O.Chidambaranar",
    "tuticorin": "V.O.Chidambaranar"
}

WMO_CODE_INFO = {
    1: {"condition": "Mainly Clear", "icon": "☀️", "risk": "Low", "description": "Clear skies, optimal berthing & conveyor discharge conditions."},
    2: {"condition": "Partly Cloudy", "icon": "⛅", "risk": "Low", "description": "Scattered clouds, stable winds, safe crane and bulk loading operations."},
    3: {"condition": "Overcast", "icon": "☁️", "risk": "Low-Moderate", "description": "Overcast marine layer; monitor wind shear during afternoon pilotage."},
    61: {"condition": "Slight Rain", "icon": "🌦️", "risk": "Moderate", "description": "Light showers; continuous moisture monitoring on coking coal & limestone hatches."},
    63: {"condition": "Moderate Rain", "icon": "🌧️", "risk": "Elevated", "description": "Precipitation exceeds threshold; recommended partial hatch tarping & conveyor cover."},
    80: {"condition": "Rain Showers / Wind Swell", "icon": "⛈️", "risk": "High Alert", "description": "Heavy marine squall & gusting wind; lightering suspension advisory and crane safety stop."}
}

class PortWeatherForecaster:
    def __init__(self):
        self.data = self._load_data()
        self.df = self._load_df()

    def _load_data(self):
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"meta": {}, "by_port": {}, "records": []}

    def _load_df(self):
        if os.path.exists(CSV_PATH):
            return pd.read_csv(CSV_PATH)
        return pd.DataFrame()

    def _resolve_port_name(self, port_key):
        if not port_key:
            return "Paradip"
        key_norm = str(port_key).lower().strip().replace(" ", "_")
        return PORT_ALIASES.get(key_norm, PORT_ALIASES.get(port_key, "Paradip"))

    def get_ports_catalog(self):
        """Returns summary of all monitored ports with operational status."""
        ports_summary = []
        by_port = self.data.get("by_port", {})
        for port_name, pdata in by_port.items():
            first_day = pdata["forecast_days"][0] if pdata["forecast_days"] else {}
            summary = pdata.get("summary", {})
            ports_summary.append({
                "port_name": port_name,
                "latitude": pdata.get("latitude"),
                "longitude": pdata.get("longitude"),
                "current_date": first_day.get("date"),
                "current_weather": {
                    "condition": first_day.get("condition"),
                    "icon": first_day.get("icon"),
                    "temp_max": first_day.get("temperature_max_c"),
                    "temp_min": first_day.get("temperature_min_c"),
                    "wind_kmh": first_day.get("max_wind_kmh"),
                    "precipitation_mm": first_day.get("precipitation_mm"),
                    "operational_risk": first_day.get("operational_risk"),
                    "operational_impact": first_day.get("operational_impact")
                },
                "summary_30d": summary
            })
        return ports_summary

    def get_port_forecast(self, port_key, horizon_days=None):
        """Returns 30-day forecast for a specific port."""
        port_name = self._resolve_port_name(port_key)
        by_port = self.data.get("by_port", {})
        port_data = by_port.get(port_name)
        
        if not port_data:
            # Fallback to first available port
            first_key = list(by_port.keys())[0] if by_port else None
            port_data = by_port.get(first_key, {"forecast_days": [], "summary": {}})
            port_name = first_key

        forecast_days = port_data.get("forecast_days", [])
        if horizon_days and str(horizon_days).isdigit():
            forecast_days = forecast_days[:int(horizon_days)]

        return {
            "port_name": port_name,
            "latitude": port_data.get("latitude"),
            "longitude": port_data.get("longitude"),
            "horizon_days": len(forecast_days),
            "summary": port_data.get("summary", {}),
            "forecast_days": forecast_days
        }

    def get_daily_snapshot(self, date=None):
        """Returns metocean snapshot across all 7 ports for a given date."""
        records = self.data.get("records", [])
        if not records:
            return []
        
        available_dates = sorted(list(set(r["date"] for r in records)))
        target_date = date if date in available_dates else available_dates[0]

        day_records = [r for r in records if r["date"] == target_date]
        return {
            "date": target_date,
            "ports_count": len(day_records),
            "ports": day_records
        }

    def compute_weather_risk_score(self):
        """
        Computes composite East Coast port weather risk score (0-100).
        Based on active precipitation and peak winds across Paradip, Dhamra, Vizag, and Kolkata.
        """
        records = self.data.get("records", [])
        if not records:
            return 25.0
        
        # Consider first 7 days across key bulk steel ports
        priority_ports = ["Dhamra", "Paradip", "Visakhapatnam", "Kolkata"]
        sample_records = [r for r in records if r["location"] in priority_ports and r["date"] <= records[6]["date"]]
        
        if not sample_records:
            return 25.0
        
        avg_wind = sum(r["max_wind_kmh"] for r in sample_records) / len(sample_records)
        total_precip = sum(r["precipitation_mm"] for r in sample_records)
        rain_ratio = sum(1 for r in sample_records if r["precipitation_mm"] > 0) / len(sample_records)
        
        # Risk formulas: wind factor (20 kmh = 20 pts, 30 kmh = 60 pts)
        wind_risk = min(50.0, max(0.0, (avg_wind - 15.0) / 15.0 * 50.0))
        precip_risk = min(50.0, (total_precip / 50.0) * 30.0 + rain_ratio * 20.0)
        
        composite = round(wind_risk + precip_risk, 1)
        return max(10.0, min(95.0, composite))
