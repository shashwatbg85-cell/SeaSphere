"""
NAVI-STEEL: Intelligent Maritime Freight Forecasting & Vessel Chartering System
Ministry of Steel (SIH26006) - Enterprise REST API Server & Web Application
v2.0 - Enhanced with Risk Scoring, Health Checks, and Input Validation
"""

import os
import time
import logging
from flask import Flask, render_template, request, jsonify

from data.maritime_knowledge import EAST_COAST_PORTS, ORIGIN_PORTS, VESSEL_CLASSES, STEEL_PLANTS, COMMODITIES, ALL_MAJOR_PORTS
from models.forecaster import FreightForecaster
from models.port_traffic_forecaster import PortTrafficForecaster
from models.port_weather_forecaster import PortWeatherForecaster
from optimizer.vessel_selector import VesselSelector
from optimizer.charter_recommender import CharterRecommender
from optimizer.landed_cost_calculator import LandedCostCalculator
from optimizer.risk_scorer import RiskScorer
from simulation.scenario_simulator import ScenarioSimulator
from models.inland_waterways_engine import InlandWaterwaysEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("NAVI-STEEL")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

# Initialize core intelligent engines
START_TIME = time.time()
logger.info("Initializing NAVI-STEEL intelligent engines...")

forecaster = FreightForecaster()
port_forecaster = PortTrafficForecaster()
weather_forecaster = PortWeatherForecaster()
vessel_selector = VesselSelector()
charter_recommender = CharterRecommender()
landed_calculator = LandedCostCalculator()
risk_scorer = RiskScorer()
scenario_simulator = ScenarioSimulator(forecaster, landed_calculator, vessel_selector)
iwt_engine = InlandWaterwaysEngine()

logger.info("All engines initialized successfully.")

# Valid parameter sets for input validation
VALID_PORT_IDS = set(EAST_COAST_PORTS.keys())
VALID_ORIGIN_IDS = set(ORIGIN_PORTS.keys())
VALID_VESSEL_CLASSES = set(VESSEL_CLASSES.keys())
VALID_PLANT_IDS = set(STEEL_PLANTS.keys())
VALID_COMMODITY_IDS = set(COMMODITIES.keys())

# ----------------- UTILITY -----------------

def validate_tonnage(tonnage, default=150000):
    """Validates cargo tonnage within safe bounds."""
    try:
        t = float(tonnage)
        return max(5000, min(300000, t))
    except (TypeError, ValueError):
        return default

# ----------------- WEB VIEWS -----------------

@app.route("/")
def index():
    """Main Executive Maritime Dashboard"""
    return render_template("index.html")

# ----------------- HEALTH CHECK -----------------

@app.route("/api/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    uptime_seconds = round(time.time() - START_TIME, 1)
    model_count = sum(len(v) for v in forecaster.models.values())
    return jsonify({
        "status": "healthy",
        "system": "NAVI-STEEL v2.0",
        "uptime_seconds": uptime_seconds,
        "models_loaded": model_count,
        "engines": {
            "forecaster": "active",
            "port_traffic_forecaster": "active",
            "weather_forecaster": "active",
            "vessel_selector": "active",
            "charter_recommender": "active",
            "landed_cost_calculator": "active",
            "risk_scorer": "active",
            "scenario_simulator": "active",
            "inland_waterways_engine": "active"
        }
    })

# ----------------- API ENDPOINTS -----------------

@app.route("/api/market/snapshot", methods=["GET"])
def get_market_snapshot():
    """Real-time market snapshot of Baltic dry indices, bunker, commodities."""
    try:
        snapshot = forecaster.get_latest_market_snapshot()
        return jsonify({"status": "success", "data": snapshot})
    except Exception as e:
        logger.error(f"Market snapshot error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/market/history", methods=["GET"])
def get_market_history():
    """Historical timeseries for dashboard charts."""
    try:
        days = int(request.args.get("days", 180))
        days = max(7, min(365, days))
        history = forecaster.get_historical_timeseries(days=days)
        return jsonify({"status": "success", "data": history})
    except Exception as e:
        logger.error(f"Market history error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/forecast", methods=["GET"])
def get_forecast():
    """Multi-horizon probabilistic forecast and XAI drivers for a route."""
    try:
        route_key = request.args.get("route", "freight_aus_paradip_cape")
        forecast = forecaster.forecast_route(route_key=route_key)
        return jsonify({"status": "success", "data": forecast})
    except Exception as e:
        logger.error(f"Forecast error for route={request.args.get('route')}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/optimizer/vessel", methods=["POST"])
def optimize_vessel():
    """Evaluates vessel feasibility, draft clearance, and lightering costs."""
    try:
        payload = request.get_json() or {}
        port_id = payload.get("port_id", "paradip")
        if port_id not in VALID_PORT_IDS:
            port_id = "paradip"
        
        tonnage = validate_tonnage(payload.get("cargo_tonnage", 150000))
        commodity = payload.get("commodity_id", "coking_coal")
        base_freight = float(payload.get("base_freight_rate_cape", 16.50))
        base_freight = max(1.0, min(100.0, base_freight))
        
        result = vessel_selector.evaluate_vessel_options(
            destination_port_id=port_id,
            cargo_tonnage=tonnage,
            commodity_id=commodity,
            base_freight_rate_cape=base_freight
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        logger.error(f"Vessel optimizer error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/optimizer/charter", methods=["POST"])
def optimize_charter():
    """Recommends market entry timing, laycan window, and contract structure."""
    try:
        payload = request.get_json() or {}
        route_key = payload.get("route_key", "freight_aus_paradip_cape")
        tonnage = validate_tonnage(payload.get("cargo_tonnage", 150000))
        lead_days = int(payload.get("max_lead_days", 45))
        lead_days = max(7, min(90, lead_days))
        
        forecast = forecaster.forecast_route(route_key=route_key)
        charter_strat = charter_recommender.recommend_charter_strategy(
            forecast_result=forecast,
            cargo_tonnage=tonnage,
            max_lead_days=lead_days
        )
        return jsonify({"status": "success", "data": charter_strat})
    except Exception as e:
        logger.error(f"Charter optimizer error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/optimizer/landed-cost", methods=["POST"])
def calculate_landed_cost():
    """Computes holistic landed procurement cost and multi-port ranking for a steel plant."""
    try:
        payload = request.get_json() or {}
        plant_id = payload.get("plant_id", "sail_rourkela")
        if plant_id not in VALID_PLANT_IDS:
            plant_id = "sail_rourkela"
            
        origin_id = payload.get("origin_id", "hay_point")
        if origin_id not in VALID_ORIGIN_IDS:
            origin_id = "hay_point"
            
        commodity_id = payload.get("commodity_id", "coking_coal")
        if commodity_id not in VALID_COMMODITY_IDS:
            commodity_id = "coking_coal"
            
        tonnage = validate_tonnage(payload.get("cargo_tonnage", 150000))
        vessel_class = payload.get("vessel_class", "Capesize")
        if vessel_class not in VALID_VESSEL_CLASSES:
            vessel_class = "Capesize"
            
        custom_freight = payload.get("custom_freight_rate")
        if custom_freight is not None:
            custom_freight = max(1.0, min(100.0, float(custom_freight)))
            
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
        logger.error(f"Landed cost error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/simulator/run", methods=["POST"])
def run_simulation():
    """Simulates what-if crises (fuel shock, port delays, BDI shocks, canal rerouting)."""
    try:
        payload = request.get_json() or {}
        route_key = payload.get("route_key", "freight_aus_paradip_cape")
        plant_id = payload.get("plant_id", "sail_rourkela")
        commodity_id = payload.get("commodity_id", "coking_coal")
        tonnage = validate_tonnage(payload.get("cargo_tonnage", 150000))
        vessel_class = payload.get("vessel_class", "Capesize")
        
        fuel_shock_pct = max(-50, min(100, float(payload.get("fuel_shock_pct", 0.0))))
        port_delay_days = max(0, min(15, float(payload.get("port_delay_days", 0.0))))
        bdi_shock_pct = max(-50, min(100, float(payload.get("bdi_shock_pct", 0.0))))
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
        logger.error(f"Simulation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/metadata/all", methods=["GET"])
def get_all_metadata():
    """Returns static maritime metadata (ports, origins, vessels, plants, commodities)."""
    return jsonify({
        "status": "success",
        "data": {
            "ports": EAST_COAST_PORTS,
            "major_ports": ALL_MAJOR_PORTS,
            "origins": ORIGIN_PORTS,
            "vessels": VESSEL_CLASSES,
            "plants": STEEL_PLANTS,
            "commodities": COMMODITIES
        }
    })

# ----------------- RISK SCORING API -----------------

@app.route("/api/risk/score", methods=["GET"])
def get_risk_score():
    """Returns composite maritime procurement risk index (0-100) with traffic-light classification."""
    try:
        snapshot = forecaster.get_latest_market_snapshot()
        latest_row = forecaster.historical_data.iloc[-1]
        
        # Build market snapshot for risk scorer
        market_data = {
            "bdi": snapshot["bdi"]["current"],
            "bci": snapshot["bci"]["current"],
            "bunker_vlsfo": snapshot["bunker_vlsfo"]["current"],
            "port_congestion_days": snapshot["port_congestion_east_coast_days"],
            "monsoon_index": float(latest_row.get("monsoon_index", 1.0)),
            "bdi_vol_14d": float(latest_row.get("bdi", 1800)) * 0.025,  # Approximate 14d vol
            "canal_risk_active": False
        }
        
        risk_result = risk_scorer.compute_risk_score(market_data)
        return jsonify({"status": "success", "data": risk_result})
    except Exception as e:
        logger.error(f"Risk score error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- PORT TRAFFIC & CAPACITY FORECASTING API -----------------

@app.route("/api/ports/traffic/history", methods=["GET"])
def get_port_traffic_history():
    """Returns 33-year historical traffic throughput (1990-91 to 2022-23) in MT."""
    try:
        port_id = request.args.get("port", "all")
        if port_id == "all":
            data = port_forecaster.get_historical_traffic(None)
        else:
            data = port_forecaster.get_historical_traffic(port_id)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        logger.error(f"Port traffic history error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/ports/traffic/forecast", methods=["GET"])
def get_port_traffic_forecast():
    """Returns multi-year ML forward projection through FY 2029-30 with P10/P50/P90 confidence bounds."""
    try:
        port_id = request.args.get("port", "total_mt")
        forecast = port_forecaster.get_traffic_forecast(port_id)
        return jsonify({"status": "success", "data": forecast})
    except Exception as e:
        logger.error(f"Port traffic forecast error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/ports/traffic/breakdown", methods=["GET"])
def get_port_cargo_breakdown():
    """Returns overseas vs coastal, unloaded vs loaded breakdown for FY 2022-23."""
    try:
        port_name = request.args.get("port")
        breakdown = port_forecaster.get_cargo_breakdown(port_name)
        return jsonify({"status": "success", "data": breakdown})
    except Exception as e:
        logger.error(f"Port breakdown error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/ports/ranking", methods=["GET"])
def get_port_rankings():
    """Returns ranked major ports by throughput, projected 2030 volume, and traffic share."""
    try:
        rankings = port_forecaster.get_port_rankings()
        return jsonify({"status": "success", "data": rankings})
    except Exception as e:
        logger.error(f"Port rankings error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/ports/all", methods=["GET"])
def get_all_major_ports():
    """Returns comprehensive metadata for all 12 Major Ports of India."""
    try:
        catalog = port_forecaster.get_all_ports_catalog()
        return jsonify({"status": "success", "data": catalog})
    except Exception as e:
        logger.error(f"Port catalog error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- PORT WEATHER & METOCEAN API -----------------

@app.route("/api/weather/forecast", methods=["GET"])
def get_weather_forecast():
    """Returns 30-day meteorological forecast, operational risk, and hatch guidance for a port."""
    try:
        port_key = request.args.get("port", "paradip")
        horizon = request.args.get("days")
        forecast = weather_forecaster.get_port_forecast(port_key, horizon_days=horizon)
        return jsonify({"status": "success", "data": forecast})
    except Exception as e:
        logger.error(f"Weather forecast error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/weather/ports", methods=["GET"])
def get_weather_ports():
    """Returns metocean summaries and current weather for all 7 East Coast cargo ports."""
    try:
        ports = weather_forecaster.get_ports_catalog()
        return jsonify({"status": "success", "data": ports})
    except Exception as e:
        logger.error(f"Weather ports catalog error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/weather/snapshot", methods=["GET"])
def get_weather_snapshot():
    """Returns cross-port comparative weather conditions for a specific date."""
    try:
        date = request.args.get("date")
        snapshot = weather_forecaster.get_daily_snapshot(date)
        return jsonify({"status": "success", "data": snapshot})
    except Exception as e:
        logger.error(f"Weather snapshot error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- INLAND WATERWAYS TRANSPORT (IWT) API -----------------

@app.route("/api/iwt/overview", methods=["GET"])
def get_iwt_overview():
    """Executive KPIs for Indian Inland Waterways transport."""
    try:
        overview = iwt_engine.get_overview()
        return jsonify({"status": "success", "data": overview})
    except Exception as e:
        logger.error(f"IWT overview error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/timeseries", methods=["GET"])
def get_iwt_timeseries():
    """11-year historical cargo movement (2013-14 to 2023-24) + 2030 projections."""
    try:
        ts = iwt_engine.get_timeseries()
        return jsonify({"status": "success", "data": ts})
    except Exception as e:
        logger.error(f"IWT timeseries error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/waterways", methods=["GET"])
def get_iwt_waterways():
    """Catalog of National Waterways (NW-1, NW-2, NW-3, NW-4, NW-5, NW-86, NW-97, etc.)."""
    try:
        state = request.args.get("state")
        catalog = iwt_engine.get_waterways_catalog(state=state)
        return jsonify({"status": "success", "data": catalog})
    except Exception as e:
        logger.error(f"IWT waterways catalog error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/waterway/<waterway_id>", methods=["GET"])
def get_iwt_waterway_detail(waterway_id):
    """Detailed specifications for a single National Waterway."""
    try:
        nw = iwt_engine.get_waterway_by_id(waterway_id.upper())
        if not nw:
            return jsonify({"status": "error", "message": f"Waterway {waterway_id} not found"}), 404
        return jsonify({"status": "success", "data": nw})
    except Exception as e:
        logger.error(f"IWT waterway detail error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/depth-lad", methods=["GET"])
def get_iwt_depth_lad():
    """Stretch-wise Least Available Depth (LAD), dredging status, shallow alerts, air draft."""
    try:
        stretches = iwt_engine.get_navigation_depth_stretches()
        return jsonify({"status": "success", "data": stretches})
    except Exception as e:
        logger.error(f"IWT depth LAD error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/depth-check", methods=["POST"])
def check_iwt_depth_clearance():
    """Evaluates vessel draft against stretch LAD, computing Under-Keel Clearance (UKC) & safety alert."""
    try:
        payload = request.get_json() or {}
        stretch_id = payload.get("stretch_id", "NW1_HAL_FRK")
        vessel_draft = float(payload.get("vessel_draft_m", 2.2))
        safety_margin = float(payload.get("safety_margin_m", 0.3))
        
        result = iwt_engine.check_vessel_draft_clearance(
            stretch_id=stretch_id,
            vessel_draft_m=vessel_draft,
            safety_margin_m=safety_margin
        )
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        logger.error(f"IWT depth clearance check error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/commodities", methods=["GET"])
def get_iwt_commodities():
    """Breakdown of cargo movement by commodity (Coal, fly ash, steel, cement, iron ore, etc.)."""
    try:
        commodities = iwt_engine.get_commodities()
        return jsonify({"status": "success", "data": commodities})
    except Exception as e:
        logger.error(f"IWT commodities error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/infrastructure", methods=["GET"])
def get_iwt_infrastructure():
    """Terminals, jetties, berths, storage capacities, and heavy handling equipment."""
    try:
        infra = iwt_engine.get_infrastructure()
        return jsonify({"status": "success", "data": infra})
    except Exception as e:
        logger.error(f"IWT infrastructure error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/vessels", methods=["GET"])
def get_iwt_vessels():
    """IWT vessel types, specifications (DWT, draft, speed), and active fleet statistics."""
    try:
        fleet = iwt_engine.get_vessel_fleet()
        return jsonify({"status": "success", "data": fleet})
    except Exception as e:
        logger.error(f"IWT vessels error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/routes", methods=["GET"])
def get_iwt_routes():
    """River route stretches, distances, currents, and multi-modal benchmarks."""
    try:
        routes = iwt_engine.get_routes()
        return jsonify({"status": "success", "data": routes})
    except Exception as e:
        logger.error(f"IWT routes error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/route-calc", methods=["POST"])
def calculate_iwt_route():
    """Calculates transit time with river currents, freight cost, and financial + carbon savings vs rail/road."""
    try:
        payload = request.get_json() or {}
        route_id = payload.get("route_id", "haldia_to_varanasi")
        tonnage = float(payload.get("cargo_tonnage", 5000))
        commodity_id = payload.get("commodity_id", "steel")
        vessel_type_id = payload.get("vessel_type_id", "self_propelled_barge_1000")
        is_upstream = bool(payload.get("is_upstream", True))

        calc_result = iwt_engine.calculate_route_transit_and_savings(
            route_id=route_id,
            cargo_tonnage=tonnage,
            commodity_id=commodity_id,
            vessel_type_id=vessel_type_id,
            is_upstream=is_upstream
        )
        return jsonify({"status": "success", "data": calc_result})
    except Exception as e:
        logger.error(f"IWT route calculation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/operators", methods=["GET"])
def get_iwt_operators():
    """Directory of private operators and public sector undertakings active in IWT."""
    try:
        operators = iwt_engine.get_operators()
        return jsonify({"status": "success", "data": operators})
    except Exception as e:
        logger.error(f"IWT operators error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/passengers", methods=["GET"])
def get_iwt_passengers():
    """Inland vessel passenger movement, Ro-Pax, and river cruise tourism."""
    try:
        passengers = iwt_engine.get_passengers_info()
        return jsonify({"status": "success", "data": passengers})
    except Exception as e:
        logger.error(f"IWT passengers error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/iwt/safety", methods=["GET"])
def get_iwt_safety():
    """Inland water transport safety audit, accident logs, and navigation aid coverage."""
    try:
        safety = iwt_engine.get_safety_metrics()
        return jsonify({"status": "success", "data": safety})
    except Exception as e:
        logger.error(f"IWT safety error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting NAVI-STEEL Server on http://127.0.0.1:{port}...")
    print(f"\n  [NAVI-STEEL v2.0] Maritime Intelligence Platform")
    print(f"  Dashboard:  http://127.0.0.1:{port}")
    print(f"  Health:     http://127.0.0.1:{port}/api/health")
    print(f"  Risk Score: http://127.0.0.1:{port}/api/risk/score\n")
    app.run(host="0.0.0.0", port=port, debug=False)
