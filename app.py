"""
NAVI-STEEL: Intelligent Maritime Freight Forecasting & Vessel Chartering System
Ministry of Steel (SIH26006) - Enterprise REST API Server & Web Application
"""

import os
from flask import Flask, render_template, request, jsonify

from data.maritime_knowledge import EAST_COAST_PORTS, ORIGIN_PORTS, VESSEL_CLASSES, STEEL_PLANTS, COMMODITIES
from models.forecaster import FreightForecaster
from optimizer.vessel_selector import VesselSelector
from optimizer.charter_recommender import CharterRecommender
from optimizer.landed_cost_calculator import LandedCostCalculator
from simulation.scenario_simulator import ScenarioSimulator

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

# Initialize core intelligent engines
forecaster = FreightForecaster()
vessel_selector = VesselSelector()
charter_recommender = CharterRecommender()
landed_calculator = LandedCostCalculator()
scenario_simulator = ScenarioSimulator(forecaster, landed_calculator, vessel_selector)

# ----------------- WEB VIEWS -----------------

@app.route("/")
def index():
    """Main Executive Maritime Dashboard"""
    return render_template("index.html")

# ----------------- API ENDPOINTS -----------------

@app.route("/api/market/snapshot", methods=["GET"])
def get_market_snapshot():
    """Real-time market snapshot of Baltic dry indices, bunker, commodities."""
    try:
        snapshot = forecaster.get_latest_market_snapshot()
        return jsonify({"status": "success", "data": snapshot})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/market/history", methods=["GET"])
def get_market_history():
    """Historical timeseries for dashboard charts."""
    try:
        days = int(request.args.get("days", 180))
        history = forecaster.get_historical_timeseries(days=days)
        return jsonify({"status": "success", "data": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/forecast", methods=["GET"])
def get_forecast():
    """Multi-horizon probabilistic forecast and XAI drivers for a route."""
    try:
        route_key = request.args.get("route", "freight_aus_paradip_cape")
        forecast = forecaster.forecast_route(route_key=route_key)
        return jsonify({"status": "success", "data": forecast})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/optimizer/vessel", methods=["POST"])
def optimize_vessel():
    """Evaluates vessel feasibility, draft clearance, and lightering costs."""
    try:
        payload = request.get_json() or {}
        port_id = payload.get("port_id", "paradip")
        tonnage = float(payload.get("cargo_tonnage", 150000))
        commodity = payload.get("commodity_id", "coking_coal")
        base_freight = float(payload.get("base_freight_rate_cape", 16.50))
        
        result = vessel_selector.evaluate_vessel_options(
            destination_port_id=port_id,
            cargo_tonnage=tonnage,
            commodity_id=commodity,
            base_freight_rate_cape=base_freight
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/optimizer/charter", methods=["POST"])
def optimize_charter():
    """Recommends market entry timing, laycan window, and contract structure."""
    try:
        payload = request.get_json() or {}
        route_key = payload.get("route_key", "freight_aus_paradip_cape")
        tonnage = float(payload.get("cargo_tonnage", 150000))
        lead_days = int(payload.get("max_lead_days", 45))
        
        forecast = forecaster.forecast_route(route_key=route_key)
        charter_strat = charter_recommender.recommend_charter_strategy(
            forecast_result=forecast,
            cargo_tonnage=tonnage,
            max_lead_days=lead_days
        )
        return jsonify({"status": "success", "data": charter_strat})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/optimizer/landed-cost", methods=["POST"])
def calculate_landed_cost():
    """Computes holistic landed procurement cost and multi-port ranking for a steel plant."""
    try:
        payload = request.get_json() or {}
        plant_id = payload.get("plant_id", "sail_rourkela")
        origin_id = payload.get("origin_id", "hay_point")
        commodity_id = payload.get("commodity_id", "coking_coal")
        tonnage = float(payload.get("cargo_tonnage", 150000))
        vessel_class = payload.get("vessel_class", "Capesize")
        custom_freight = payload.get("custom_freight_rate")
        if custom_freight is not None:
            custom_freight = float(custom_freight)
            
        result = landed_calculator.calculate_landed_cost(
            plant_id=plant_id,
            origin_id=origin_id,
            commodity_id=commodity_id,
            cargo_tonnage=tonnage,
            vessel_class=vessel_class,
            custom_freight_rate=custom_freight
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/simulator/run", methods=["POST"])
def run_simulation():
    """Simulates what-if crises (fuel shock, port delays, BDI shocks, canal rerouting)."""
    try:
        payload = request.get_json() or {}
        route_key = payload.get("route_key", "freight_aus_paradip_cape")
        plant_id = payload.get("plant_id", "sail_rourkela")
        commodity_id = payload.get("commodity_id", "coking_coal")
        tonnage = float(payload.get("cargo_tonnage", 150000))
        vessel_class = payload.get("vessel_class", "Capesize")
        fuel_shock_pct = float(payload.get("fuel_shock_pct", 0.0))
        port_delay_days = float(payload.get("port_delay_days", 0.0))
        bdi_shock_pct = float(payload.get("bdi_shock_pct", 0.0))
        canal_rerouting = bool(payload.get("canal_rerouting_active", False))

        sim_result = scenario_simulator.run_simulation(
            route_key=route_key,
            plant_id=plant_id,
            commodity_id=commodity_id,
            cargo_tonnage=tonnage,
            vessel_class=vessel_class,
            fuel_shock_pct=fuel_shock_pct,
            port_delay_days=port_delay_days,
            bdi_shock_pct=bdi_shock_pct,
            canal_rerouting_active=canal_rerouting
        )
        return jsonify({"status": "success", "data": sim_result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/metadata/all", methods=["GET"])
def get_all_metadata():
    """Returns static maritime metadata (ports, origins, vessels, plants, commodities)."""
    return jsonify({
        "status": "success",
        "data": {
            "ports": EAST_COAST_PORTS,
            "origins": ORIGIN_PORTS,
            "vessels": VESSEL_CLASSES,
            "plants": STEEL_PLANTS,
            "commodities": COMMODITIES
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting NAVI-STEEL Server on http://127.0.0.1:{port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
