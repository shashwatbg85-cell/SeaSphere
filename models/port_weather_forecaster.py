"""
Port Metocean & Weather Intelligence Engine.
Loads hyper-local meteorological and oceanographic forecast data for Indian East Coast cargo ports:
Dhamra, Paradip, Visakhapatnam, Kolkata, Chennai, Kamarajar, and V.O. Chidambaranar.
Supports dynamic database querying (SQLite/PostgreSQL) and real-time Open-Meteo updates.

Provides:
- Daily temperature, wind speed, precipitation, and WMO weather codes.
- Maritime operational impact assessments (crane gantry safety, bulk hatch moisture protection, lightering swell caution).
- Cross-port comparative metocean analysis for optimal vessel laycan routing.
"""

import os
import json
import logging
import pandas as pd
from data.db_engine import db_manager

logger = logging.getLogger("SeaSphere.WeatherEngine")

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
    0: {"condition": "Clear Sky", "icon": "☀️", "risk": "Low", "description": "Clear skies, optimal berthing & conveyor discharge conditions."},
    1: {"condition": "Mainly Clear", "icon": "☀️", "risk": "Low", "description": "Clear skies, optimal berthing & conveyor discharge conditions."},
    2: {"condition": "Partly Cloudy", "icon": "⛅", "risk": "Low", "description": "Scattered clouds, stable winds, safe crane and bulk loading operations."},
    3: {"condition": "Overcast", "icon": "☁️", "risk": "Low-Moderate", "description": "Overcast marine layer; monitor wind shear during afternoon pilotage."},
    45: {"condition": "Foggy", "icon": "🌫️", "risk": "Moderate", "description": "Reduced visibility; enforce vessel speed restrictions and radar pilotage."},
    51: {"condition": "Light Drizzle", "icon": "🌦️", "risk": "Low-Moderate", "description": "Light drizzle; monitor sensitive dry bulk hatches."},
    61: {"condition": "Slight Rain", "icon": "🌦️", "risk": "Moderate", "description": "Light showers; continuous moisture monitoring on coking coal & limestone hatches."},
    63: {"condition": "Moderate Rain", "icon": "🌧️", "risk": "Elevated", "description": "Precipitation exceeds threshold; recommended partial hatch tarping & conveyor cover."},
    65: {"condition": "Heavy Rain", "icon": "🌧️", "risk": "High Alert", "description": "Intense rainfall; halt bulk discharging to prevent cargo liquefaction and coal slurry formation."},
    80: {"condition": "Rain Showers / Wind Swell", "icon": "⛈️", "risk": "High Alert", "description": "Heavy marine squall & gusting wind; lightering suspension advisory and crane safety stop."},
    82: {"condition": "Violent Squall", "icon": "⛈️", "risk": "Critical Alert", "description": "Severe squall lines; suspend all port crane operations and double mooring lines."}
}


class PortWeatherForecaster:
    def __init__(self):
        self.db = db_manager
        self.static_data = self._load_static_data()

    def _load_static_data(self):
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"meta": {}, "by_port": {}, "records": []}

    def _resolve_port_name(self, port_key):
        if not port_key:
            return "Paradip"
        key_norm = str(port_key).lower().strip().replace(" ", "_")
        return PORT_ALIASES.get(key_norm, PORT_ALIASES.get(port_key, "Paradip"))

    def get_ports_catalog(self):
        """Returns summary of all monitored ports with live operational weather from database."""
        ports = ["Paradip", "Visakhapatnam", "Dhamra", "Kolkata", "Chennai", "Kamarajar", "V.O.Chidambaranar"]
        ports_summary = []

        for p_name in ports:
            p_forecast = self.get_port_forecast(p_name)
            if p_forecast and p_forecast.get("forecast_days"):
                first_day = p_forecast["forecast_days"][0]
                ports_summary.append({
                    "port_name": p_name,
                    "latitude": p_forecast.get("latitude"),
                    "longitude": p_forecast.get("longitude"),
                    "current_date": first_day.get("date"),
                    "current_weather": {
                        "condition": first_day.get("condition"),
                        "icon": first_day.get("icon", "☀️"),
                        "temp_max": first_day.get("temperature_max_c"),
                        "temp_min": first_day.get("temperature_min_c"),
                        "wind_kmh": first_day.get("max_wind_kmh"),
                        "precipitation_mm": first_day.get("precipitation_mm"),
                        "operational_risk": first_day.get("operational_risk"),
                        "operational_impact": first_day.get("operational_impact")
                    },
                    "summary_30d": p_forecast.get("summary", {})
                })

        return ports_summary

    def get_port_forecast(self, port_key, horizon_days=None):
        """Returns weather forecast for a specific port from dynamic database or static fallback."""
        port_name = self._resolve_port_name(port_key)

        # 1. Query database records
        try:
            db_records = self.db.get_port_weather(port_name=port_name, horizon_days=30)
            if db_records:
                forecast_days = []
                total_precip = 0.0
                max_wind = 0.0
                high_risk_days = 0

                for r in db_records:
                    w_code = r.get("wmo_code", 1)
                    info = WMO_CODE_INFO.get(w_code, {"condition": r.get("condition", "Mainly Clear"), "icon": "☀️", "risk": "Low", "description": "Safe bulk operations."})
                    
                    p_mm = float(r.get("precipitation_mm", 0.0))
                    w_spd = float(r.get("max_wind_kmh", 12.0))
                    total_precip += p_mm
                    if w_spd > max_wind:
                        max_wind = w_spd

                    op_risk = r.get("operational_risk", info["risk"])
                    if "High" in op_risk or "Critical" in op_risk:
                        high_risk_days += 1

                    forecast_days.append({
                        "date": r.get("date"),
                        "temperature_max_c": r.get("temperature_max_c"),
                        "temperature_min_c": r.get("temperature_min_c"),
                        "max_wind_kmh": w_spd,
                        "precipitation_mm": p_mm,
                        "wmo_code": w_code,
                        "condition": r.get("condition"),
                        "icon": info["icon"],
                        "operational_risk": op_risk,
                        "operational_impact": info["description"]
                    })

                if horizon_days and str(horizon_days).isdigit():
                    forecast_days = forecast_days[:int(horizon_days)]

                summary_risk = "High" if high_risk_days >= 3 or total_precip > 50 else ("Moderate" if high_risk_days >= 1 or total_precip > 15 else "Low")

                return {
                    "port_name": port_name,
                    "latitude": db_records[0].get("latitude", 20.3),
                    "longitude": db_records[0].get("longitude", 86.6),
                    "horizon_days": len(forecast_days),
                    "summary": {
                        "total_precipitation_mm": round(total_precip, 1),
                        "max_gust_kmh": round(max_wind, 1),
                        "high_risk_days_count": high_risk_days,
                        "weather_risk_level": summary_risk
                    },
                    "forecast_days": forecast_days
                }
        except Exception as e:
            logger.warning(f"Failed to query DB for port weather {port_name}: {e}")

        # Fallback to static data
        by_port = self.static_data.get("by_port", {})
        port_data = by_port.get(port_name, {})
        forecast_days = port_data.get("forecast_days", [])
        if horizon_days and str(horizon_days).isdigit():
            forecast_days = forecast_days[:int(horizon_days)]

        return {
            "port_name": port_name,
            "latitude": port_data.get("latitude", 20.316),
            "longitude": port_data.get("longitude", 86.611),
            "horizon_days": len(forecast_days),
            "summary": port_data.get("summary", {}),
            "forecast_days": forecast_days
        }

    def get_daily_snapshot(self, date=None):
        """Returns metocean snapshot across all ports for a given date."""
        catalog = self.get_ports_catalog()
        return {
            "date": date or (catalog[0]["current_date"] if catalog else None),
            "ports_count": len(catalog),
            "ports": catalog
        }

    def compute_weather_risk_score(self):
        """Computes composite East Coast port weather risk score (0-100)."""
        catalog = self.get_ports_catalog()
        if not catalog:
            return 25.0

        risk_scores = []
        for p in catalog:
            cw = p.get("current_weather", {})
            wind = float(cw.get("wind_kmh", 15.0))
            rain = float(cw.get("precipitation_mm", 0.0))
            w_score = min(50.0, max(0.0, (wind - 14.0) / 16.0 * 50.0))
            r_score = min(50.0, rain * 4.0)
            risk_scores.append(w_score + r_score)

        avg_score = sum(risk_scores) / len(risk_scores) if risk_scores else 25.0
        return round(max(10.0, min(95.0, avg_score)), 1)
