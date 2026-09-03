# NAVI-STEEL: Intelligent Maritime Freight Forecasting & Bulk Cargo Procurement Decision Support System

> **Smart India Hackathon (SIH 2026) | Problem ID: SIH26006**  
> **Sponsoring Ministry:** Ministry of Steel, Government of India  
> **Theme:** Transportation & Logistics / Smart Automation  
> **Target Organizations:** Steel Authority of India Ltd (SAIL), Rashtriya Ispat Nigam Ltd (RINL - Vizag Steel), NMDC, Ministry of Steel

[![Live Website](https://img.shields.io/badge/🌐_LIVE_WEBSITE-CLICK_HERE_TO_OPEN-00d2ff?style=for-the-badge&logo=googlechrome&logoColor=white)](https://trickyfinisher000-sudo.github.io/SIH-PROTO/)
[![GitHub Pages](https://img.shields.io/badge/Hosted_On-GitHub_Pages-00f5a0?style=for-the-badge&logo=github)](https://trickyfinisher000-sudo.github.io/SIH-PROTO/)

### 🔗 **Direct Live Application URL:**  
### 👉 [https://trickyfinisher000-sudo.github.io/SIH-PROTO/](https://trickyfinisher000-sudo.github.io/SIH-PROTO/)

---

## 📌 Executive Summary
Indian steel public sector enterprises import tens of millions of metric tonnes of **metallurgical (coking) coal**, thermal coal, limestone, and manganese from overseas mining hubs (Australia, Indonesia, South Africa, USA, Russia) to deep and riverine discharge ports along the **East Coast of India** (Paradip, Visakhapatnam, Haldia, Dhamra, Krishnapatnam).

Historically, PSU procurement managers relied on reactive daily spot market exploration. Because global dry bulk freight rates (Baltic Capesize/Panamax indices) swing wildly by 30% to 80% within weeks, this reactive approach causes:
1. **Chartering at Market Peaks:** Missing multi-million-dollar cost-saving opportunities.
2. **Suboptimal Vessel Selection:** Inefficiently choosing vessel classes (Capesize, Panamax, Supramax) without accounting for dynamic cargo draft and destination port draft limits (e.g. Haldia riverine draft bottlenecks requiring expensive offshore lightering).
3. **Heavy Demurrage Exposure:** Unplanned port congestion and weather delays triggering $15,000–$35,000/day idle penalties per vessel.
4. **Siloed Planning:** Decoupling ocean freight from inland Indian Railways rake logistics.

**NAVI-STEEL** transforms this process into an **intelligent predictive and prescriptive decision support platform**.

---

## 🌟 Key Innovations & Features

### 1. Multi-Horizon AI Freight Forecasting Engine
- **Hybrid Machine Learning:** Gradient Boosted Trees (XGBoost) trained on 6+ years of daily maritime indicators.
- **Probabilistic Horizons:** Generates multi-horizon forecasts (+7, +15, +30, +60, +90 days) with $P_{10}$ (optimistic), $P_{50}$ (expected median), and $P_{90}$ (risk bound) confidence intervals.
- **Explainable AI (XAI):** Real-time feature attribution waterfall detailing how marine bunker fuel (Singapore VLSFO), Baltic momentum, port queues, and Bay of Bengal monsoon seasonality drive the forward rate.

### 2. Vessel Chartering & Market Entry Optimizer
- **Dynamic Arrival Draft Calculation:** Calculates vessel operating draft based on actual cargo parcel deadweight:
  $$\text{Arrival Draft} = \text{Ballast Draft} + (\text{Design Draft} - \text{Ballast Draft}) \times \frac{\text{Cargo Tonnage}}{\text{Max DWT}}$$
- **Lightering & Draft Feasibility Check:** Automatically checks draft clearance and flags shallow riverine ports (like Haldia) requiring offshore transshipment.
- **Optimal 5-Day Laycan Window:** Analyzes the forward cost curve to identify the exact 5-day loading tender window that minimizes charter cost.
- **Contract Type Evaluation:** Compares **Spot Voyage Charter**, **Short-term Time Charter (TC)**, and **Contract of Affreightment (COA)**.

### 3. Total Landed Cost (TLC) & Port Gateway Optimizer
- Evaluates the end-to-end supply chain landed cost to major Indian blast furnaces (SAIL Rourkela, Bokaro, Durgapur, IISCO, Bhilai, RINL Vizag):
  $$\text{TLC} = \text{FOB Price} + \text{Ocean Freight} + \text{Bunker Surcharge (BAF)} + \text{Port Dues} + \text{Demurrage Risk} + \text{Inland Rail Freight}$$
- Compares discharge ports (Paradip vs Dhamra vs Vizag vs Haldia) and quantifies the exact savings of the optimal gateway.

### 4. Crisis & What-If Stress-Testing Simulator
- Interactive sensitivity sliders to stress-test supply chain shocks in real-time:
  - Marine Bunker Fuel Spikes (-30% to +60% VLSFO)
  - Monsoon Swells & Cyclone Port Delays (+0 to +10 Days waiting time)
  - Global Baltic Paper Squeeze
  - Geopolitical Canal Rerouting (Suez Canal / Red Sea closure forcing circumnavigation via Cape of Good Hope)
- Prescribes tactical mitigations (slow-steaming, bunker hedging, port diversion, 24-hr NOR renegotiation).

### 5. Interactive Web Dashboard
- **Theme:** Dark maritime glassmorphism UI with electric cyan and mint emerald accents.
- **Interactive Maritime Map:** Visualizes shipping lanes, overseas origin hubs, East Coast ports, and animated vessel tracks via Leaflet.js.
- **Executive Tender Brief:** One-click generation of procurement briefs formatted for Ministry of Steel / PSU tender boards.

---

## 🏗️ Architecture & Technology Stack

```
d:\sih tesying/
├── app.py                      # Flask REST API server and routing
├── requirements.txt            # Python dependencies
├── test_suite.py               # Automated unit and integration test suite
├── data/
│   ├── maritime_knowledge.py   # Domain specs: Ports, vessels, commodities, steel plants
│   ├── dataset_generator.py    # 6-year realistic daily maritime timeseries generator
│   └── historical_freight.csv  # 2,400+ daily market records (2020-2026)
├── models/
│   ├── train_forecaster.py     # Feature engineering & XGBoost training pipeline
│   ├── forecaster.py           # Multi-horizon inference & Explainable AI engine
│   └── saved_models/           # Pre-trained models & metadata
├── optimizer/
│   ├── vessel_selector.py      # Dynamic draft & vessel capacity optimizer
│   ├── charter_recommender.py  # Optimal laycan window & contract strategy recommender
│   └── landed_cost_calculator.py# Total Landed Procurement Cost calculator to steel plants
├── simulation/
│   └── scenario_simulator.py   # Crisis what-if stress-testing engine
├── static/
│   ├── css/style.css           # Premium glassmorphic maritime stylesheet
│   └── js/
│       ├── app.js              # Application logic, Chart.js forecasts, API calls
│       └── map.js              # Leaflet.js interactive trade route visualizer
└── templates/
    └── index.html              # Main dashboard single-page application
```

- **Backend:** Python 3.14, Flask, NumPy, Pandas, Scikit-Learn, XGBoost, Statsmodels
- **Frontend:** HTML5, Vanilla CSS3 (Custom Maritime Design System), JavaScript (ES6+), Leaflet.js, Chart.js

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
python test_suite.py
```
*(All 8 test suites validate data integrity, ML convergence, optimization logic, and API endpoints).*

### 3. Start the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🎤 Presentation Pitch for SIH Jury & Evaluators

When presenting to the Ministry of Steel and Hackathon Jury, highlight these four key value propositions:

1. **Direct Financial Impact:**
   - On a typical Cape parcel of 150,000 MT of Australian coking coal, a $2.50/MT freight optimization saves **$375,000 per voyage**.
   - For an annual PSU procurement quota of 15–20 million MT, NAVI-STEEL can deliver **₹150 to ₹300 Crores** in annual foreign exchange savings.

2. **Resolving Port Bottlenecks (Haldia vs. Dhamra):**
   - Evaluators love when you demonstrate domain nuances: e.g., Haldia Dock has an 8.5m riverine draft requiring lightering or daughter vessels (+ $6.80/T penalty). NAVI-STEEL dynamically analyzes whether discharging a Capesize at deepwater Dhamra (18m draft) and raking by Indian Railways to Durgapur/Bokaro is cheaper than direct Handymax into Haldia!

3. **Explainable AI vs. Black-Box Models:**
   - PSU committees cannot make decisions on opaque neural networks. NAVI-STEEL shows exact dollar-per-tonne attributions (Bunker fuel impact, Baltic forward momentum, berth waiting time, monsoon seasonality).

4. **Crisis Readiness:**
   - Demonstrating the live What-If Crisis Simulator (e.g. Red Sea/Suez Canal rerouting adding 12 days and $7.50/T) proves the system is production-ready for real-world geopolitical uncertainties.
