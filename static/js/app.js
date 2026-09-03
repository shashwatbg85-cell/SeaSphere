/**
 * NAVI-STEEL Main Application Logic
 * Integrates Freight Forecasting, Vessel Optimization, Landed Cost Analysis, and Crisis Simulation.
 * Hybrid Architecture: Connects to live Flask API with automatic zero-latency client-side static engine fallback.
 */

let forecastChart = null;
let currentForecastData = null;
let currentActiveHorizon = "all";
let cachedStaticForecasts = null;
let cachedStaticKnowledge = null;

// Domain Constants for Client-Side Static Engine
const PORTS_DATA = {
  paradip: { name: "Paradip Port", max_draft_meters: 14.5, port_dues_usd_ton: 2.20, daily_demurrage_usd: 24000, avg_waiting_days: 2.8, lightering_cost_usd_ton: 0.0 },
  vizag: { name: "Visakhapatnam Port", max_draft_meters: 18.1, port_dues_usd_ton: 2.45, daily_demurrage_usd: 26000, avg_waiting_days: 2.1, lightering_cost_usd_ton: 0.0 },
  dhamra: { name: "Dhamra Port", max_draft_meters: 17.5, port_dues_usd_ton: 2.35, daily_demurrage_usd: 22000, avg_waiting_days: 1.6, lightering_cost_usd_ton: 0.0 },
  haldia: { name: "Haldia Dock Complex", max_draft_meters: 8.5, port_dues_usd_ton: 3.10, daily_demurrage_usd: 19000, avg_waiting_days: 3.4, lightering_cost_usd_ton: 4.50 }
};

const VESSELS_DATA = {
  Capesize: { design_draft_meters: 18.2, ballast_draft_meters: 9.0, max_dwt: 180000, typical_capacity_dwt: 175000, freight_cost_factor: 1.0 },
  Panamax: { design_draft_meters: 14.2, ballast_draft_meters: 7.2, max_dwt: 82000, typical_capacity_dwt: 75000, freight_cost_factor: 1.22 },
  Supramax: { design_draft_meters: 12.8, ballast_draft_meters: 6.0, max_dwt: 64000, typical_capacity_dwt: 58000, freight_cost_factor: 1.45 },
  Handymax: { design_draft_meters: 10.5, ballast_draft_meters: 5.2, max_dwt: 45000, typical_capacity_dwt: 40000, freight_cost_factor: 1.68 }
};

const PLANTS_DATA = {
  sail_rourkela: {
    name: "SAIL Rourkela Steel Plant (RSP)", state: "Odisha",
    preferred_ports: {
      paradip: { rail_distance_km: 305, transit_days: 1.5 },
      dhamra: { rail_distance_km: 340, transit_days: 1.8 },
      haldia: { rail_distance_km: 410, transit_days: 2.2 },
      vizag: { rail_distance_km: 685, transit_days: 3.2 }
    }
  },
  sail_bokaro: {
    name: "SAIL Bokaro Steel Plant (BSL)", state: "Jharkhand",
    preferred_ports: {
      haldia: { rail_distance_km: 360, transit_days: 2.0 },
      dhamra: { rail_distance_km: 460, transit_days: 2.5 },
      paradip: { rail_distance_km: 510, transit_days: 2.7 },
      vizag: { rail_distance_km: 870, transit_days: 4.0 }
    }
  },
  rinl_vizag: {
    name: "RINL Visakhapatnam Steel Plant (VSP)", state: "Andhra Pradesh",
    preferred_ports: {
      vizag: { rail_distance_km: 25, transit_days: 0.2 },
      paradip: { rail_distance_km: 610, transit_days: 3.0 },
      dhamra: { rail_distance_km: 690, transit_days: 3.5 },
      haldia: { rail_distance_km: 890, transit_days: 4.2 }
    }
  },
  sail_bhilai: {
    name: "SAIL Bhilai Steel Plant (BSP)", state: "Chhattisgarh",
    preferred_ports: {
      vizag: { rail_distance_km: 560, transit_days: 2.8 },
      paradip: { rail_distance_km: 630, transit_days: 3.1 },
      dhamra: { rail_distance_km: 710, transit_days: 3.6 },
      haldia: { rail_distance_km: 840, transit_days: 4.1 }
    }
  },
  sail_durgapur: {
    name: "SAIL Durgapur Steel Plant (DSP)", state: "West Bengal",
    preferred_ports: {
      haldia: { rail_distance_km: 220, transit_days: 1.2 },
      dhamra: { rail_distance_km: 390, transit_days: 2.1 },
      paradip: { rail_distance_km: 480, transit_days: 2.5 },
      vizag: { rail_distance_km: 860, transit_days: 3.9 }
    }
  }
};

const COMMODITIES_DATA = {
  coking_coal: { name: "Prime Hard Coking Coal", benchmark_price_usd_ton: 265.0 },
  thermal_coal: { name: "Thermal Coal (Indo / Aus)", benchmark_price_usd_ton: 135.0 },
  limestone: { name: "SMS Grade Limestone (UAE / Oman)", benchmark_price_usd_ton: 38.0 },
  manganese_ore: { name: "High Grade Manganese Ore", benchmark_price_usd_ton: 195.0 }
};

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize Map
  if (typeof initMaritimeMap === "function") {
    initMaritimeMap();
  }

  // 2. Load Real-time Market Snapshot
  loadMarketSnapshot();

  // 3. Load Initial Freight Forecast
  loadForecast("freight_aus_paradip_cape");

  // 4. Load Initial Tender Optimizer
  runTenderOptimization();

  // 5. Initialize Simulator Event Listeners
  initSimulatorListeners();

  // 6. Setup Route Change Listener
  const routeSelect = document.getElementById("forecaster-route-select");
  if (routeSelect) {
    routeSelect.addEventListener("change", (e) => {
      loadForecast(e.target.value);
    });
  }

  // 7. Setup Horizon Filter Buttons
  document.querySelectorAll(".tab-btn[data-horizon]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".tab-btn[data-horizon]").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentActiveHorizon = e.target.getAttribute("data-horizon");
      updateForecastChartHorizon(currentActiveHorizon);
    });
  });

  // 8. Tender Form Trigger
  const tenderBtn = document.getElementById("btn-run-tender-opt");
  if (tenderBtn) {
    tenderBtn.addEventListener("click", () => {
      runTenderOptimization();
    });
  }

  // 9. Export Report Modal Handlers
  const exportBtn = document.getElementById("btn-export-report");
  const modalBackdrop = document.getElementById("report-modal");
  const modalClose = document.getElementById("modal-close-btn");
  
  if (exportBtn && modalBackdrop) {
    exportBtn.addEventListener("click", () => {
      generateProcurementReport();
      modalBackdrop.classList.add("open");
    });
  }

  if (modalClose && modalBackdrop) {
    modalClose.addEventListener("click", () => {
      modalBackdrop.classList.remove("open");
    });
  }

  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) modalBackdrop.classList.remove("open");
    });
  }
});

/**
 * 1. Fetch & Display Live Maritime Market Snapshot
 */
function loadMarketSnapshot() {
  fetch("/api/market/snapshot")
    .then(res => {
      if (!res.ok) throw new Error("API not available");
      return res.json();
    })
    .then(res => {
      if (res.status === "success") applyMarketSnapshot(res.data);
      else throw new Error("API status failed");
    })
    .catch(() => {
      // Static fallback
      fetch("./static/data/snapshot.json")
        .then(res => res.json())
        .then(res => applyMarketSnapshot(res.data))
        .catch(err => console.error("Error loading snapshot:", err));
    });
}

function applyMarketSnapshot(d) {
  document.getElementById("kpi-bdi").innerText = d.bdi.current.toLocaleString();
  const bdiDelta = d.bdi.change_7d;
  const bdiDeltaEl = document.getElementById("kpi-bdi-sub");
  bdiDeltaEl.className = bdiDelta >= 0 ? "kpi-sub trend-up" : "kpi-sub trend-down";
  bdiDeltaEl.innerHTML = `${bdiDelta >= 0 ? '▲' : '▼'} ${Math.abs(bdiDelta)} pts (${d.bdi.change_7d_pct}%) 7d`;

  document.getElementById("kpi-bci").innerText = d.bci.current.toLocaleString();
  const bciDelta = d.bci.change_7d;
  const bciDeltaEl = document.getElementById("kpi-bci-sub");
  bciDeltaEl.className = bciDelta >= 0 ? "kpi-sub trend-up" : "kpi-sub trend-down";
  bciDeltaEl.innerHTML = `${bciDelta >= 0 ? '▲' : '▼'} ${Math.abs(bciDelta)} pts (Capesize)`;

  document.getElementById("kpi-vlsfo").innerText = `$${d.bunker_vlsfo.current.toFixed(1)}`;
  const vlsfoDelta = d.bunker_vlsfo.change_7d;
  const vlsfoDeltaEl = document.getElementById("kpi-vlsfo-sub");
  vlsfoDeltaEl.className = vlsfoDelta >= 0 ? "kpi-sub trend-up" : "kpi-sub trend-down";
  vlsfoDeltaEl.innerHTML = `${vlsfoDelta >= 0 ? '▲' : '▼'} $${Math.abs(vlsfoDelta).toFixed(1)}/MT (Sing 0.5%)`;

  document.getElementById("kpi-coal").innerText = `$${d.coking_coal_fob.current.toFixed(1)}`;
  document.getElementById("kpi-coal-sub").innerHTML = `FOB Hay Point Australia`;

  document.getElementById("kpi-queue").innerText = `${d.port_congestion_east_coast_days.toFixed(1)} Days`;
}

/**
 * 2. Fetch & Render Multi-Horizon Freight Forecast with Chart.js
 */
function loadForecast(routeKey) {
  fetch(`/api/forecast?route=${routeKey}`)
    .then(res => {
      if (!res.ok) throw new Error("API not available");
      return res.json();
    })
    .then(res => {
      if (res.status === "success") {
        currentForecastData = res.data;
        renderForecastView(currentForecastData);
      } else {
        throw new Error("API status failed");
      }
    })
    .catch(() => {
      // Static fallback from static JSON
      if (cachedStaticForecasts) {
        currentForecastData = cachedStaticForecasts[routeKey];
        if (currentForecastData) renderForecastView(currentForecastData);
      } else {
        fetch("./static/data/forecasts.json")
          .then(res => res.json())
          .then(res => {
            cachedStaticForecasts = res.data || res;
            currentForecastData = cachedStaticForecasts[routeKey];
            if (currentForecastData) renderForecastView(currentForecastData);
          })
          .catch(err => console.error("Error loading forecast data:", err));
      }
    });
}

function renderForecastView(data) {
  // Update Spot and Summary Cards
  document.getElementById("fc-spot-rate").innerText = `$${data.current_spot_rate.toFixed(2)}`;
  document.getElementById("fc-regime").innerText = data.market_regime;
  document.getElementById("fc-advice").innerText = data.recommendation_summary;

  // Render Chart
  renderChart(data);

  // Render XAI Feature Attribution Waterfall
  renderXaiDrivers(data.xai_drivers);

  // Sync with trade lane on map if relevant
  if (data.route_key.includes("aus_paradip") && window.highlightTradeLane) {
    window.highlightTradeLane("aus_paradip");
  } else if (data.route_key.includes("indo") && window.highlightTradeLane) {
    window.highlightTradeLane("indo_paradip");
  } else if (data.route_key.includes("rsa") && window.highlightTradeLane) {
    window.highlightTradeLane("rsa_vizag");
  } else if (data.route_key.includes("usa") && window.highlightTradeLane) {
    window.highlightTradeLane("usa_paradip");
  }
}

function renderChart(data) {
  const ctx = document.getElementById("forecastChart");
  if (!ctx) return;

  const trajectory = data.daily_trajectory;
  const labels = trajectory.map(d => `Day +${d.day}`);
  const p50Values = trajectory.map(d => d.p50);
  const p10Values = trajectory.map(d => d.p10);
  const p90Values = trajectory.map(d => d.p90);

  if (forecastChart) {
    forecastChart.destroy();
  }

  forecastChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Upper Risk Bound (P90)",
          data: p90Values,
          borderColor: "rgba(255, 77, 109, 0.45)",
          borderDash: [5, 5],
          backgroundColor: "rgba(0, 210, 255, 0.05)",
          pointRadius: 0,
          fill: "+1",
          tension: 0.3
        },
        {
          label: "AI Expected Forecast (P50)",
          data: p50Values,
          borderColor: "#00d2ff",
          borderWidth: 3,
          backgroundColor: "rgba(0, 210, 255, 0.12)",
          pointRadius: (context) => {
            const index = context.dataIndex;
            return [7, 15, 30, 60, 90].includes(index) ? 6 : 0;
          },
          pointBackgroundColor: "#ffffff",
          pointBorderColor: "#00d2ff",
          pointBorderWidth: 2,
          fill: false,
          tension: 0.3
        },
        {
          label: "Optimistic Lower Bound (P10)",
          data: p10Values,
          borderColor: "rgba(0, 245, 160, 0.45)",
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: {
            color: "#94a3b8",
            boxWidth: 12,
            font: { family: "Inter", size: 11 }
          }
        },
        tooltip: {
          backgroundColor: "rgba(13, 24, 51, 0.95)",
          titleColor: "#00d2ff",
          bodyColor: "#f0f4fc",
          borderColor: "rgba(0, 210, 255, 0.3)",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: $${context.raw.toFixed(2)}/MT`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: {
            color: "#64748b",
            maxTicksLimit: 10,
            font: { family: "Inter", size: 10 }
          }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: {
            color: "#64748b",
            callback: value => `$${value}`,
            font: { family: "Inter", size: 10 }
          }
        }
      }
    }
  });
}

function updateForecastChartHorizon(horizon) {
  if (!currentForecastData || !forecastChart) return;
  const maxDay = horizon === "all" ? 90 : parseInt(horizon);
  const filteredTrajectory = currentForecastData.daily_trajectory.filter(d => d.day <= maxDay);

  forecastChart.data.labels = filteredTrajectory.map(d => `Day +${d.day}`);
  forecastChart.data.datasets[0].data = filteredTrajectory.map(d => d.p90);
  forecastChart.data.datasets[1].data = filteredTrajectory.map(d => d.p50);
  forecastChart.data.datasets[2].data = filteredTrajectory.map(d => d.p10);
  forecastChart.update();
}

function renderXaiDrivers(drivers) {
  const container = document.getElementById("xai-factors-container");
  if (!container) return;

  container.innerHTML = "";
  drivers.forEach(d => {
    const item = document.createElement("div");
    item.className = `xai-item ${d.direction}`;
    item.innerHTML = `
      <div>
        <div class="xai-factor-title">${d.factor} <span style="font-weight: 400; color: #94a3b8;">(${d.value})</span></div>
        <div class="xai-factor-desc">${d.description}</div>
      </div>
      <div class="xai-impact-val ${d.direction === 'positive' ? 'pos' : 'neg'}">
        ${d.impact_usd_ton} / MT
      </div>
    `;
    container.appendChild(item);
  });
}

/**
 * 3. Tender Optimizer (Vessel Selector + Laycan + Landed Cost)
 */
function runTenderOptimization() {
  const commodityId = document.getElementById("tender-commodity").value;
  const plantId = document.getElementById("tender-plant").value;
  const portId = document.getElementById("tender-port").value;
  const tonnage = parseFloat(document.getElementById("tender-tonnage").value) || 150000;
  const vesselClass = document.getElementById("tender-vessel").value;

  // A. Vessel Optimizer
  fetch("/api/optimizer/vessel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ port_id: portId, cargo_tonnage: tonnage, commodity_id: commodityId })
  })
  .then(res => { if (!res.ok) throw new Error(); return res.json(); })
  .then(res => { if (res.status === "success") renderVesselCards(res.data); else throw new Error(); })
  .catch(() => {
    renderVesselCards(clientCalculateVesselOptimizer(portId, tonnage, commodityId));
  });

  // B. Charter Recommender
  fetch("/api/optimizer/charter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ route_key: "freight_aus_paradip_cape", cargo_tonnage: tonnage, max_lead_days: 45 })
  })
  .then(res => { if (!res.ok) throw new Error(); return res.json(); })
  .then(res => { if (res.status === "success") renderCharterRecommendation(res.data); else throw new Error(); })
  .catch(() => {
    renderCharterRecommendation(clientCalculateCharterRecommender(tonnage));
  });

  // C. Total Landed Cost
  fetch("/api/optimizer/landed-cost", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plant_id: plantId, origin_id: "hay_point", commodity_id: commodityId, cargo_tonnage: tonnage, vessel_class: vesselClass })
  })
  .then(res => { if (!res.ok) throw new Error(); return res.json(); })
  .then(res => { if (res.status === "success") renderLandedCostTable(res.data); else throw new Error(); })
  .catch(() => {
    renderLandedCostTable(clientCalculateLandedCost(plantId, commodityId, tonnage, vesselClass));
  });
}

function renderVesselCards(data) {
  const container = document.getElementById("vessel-cards-container");
  if (!container) return;

  container.innerHTML = "";
  data.vessel_evaluations.forEach(v => {
    const isBest = v.vessel_class === data.best_recommended_vessel;
    const card = document.createElement("div");
    card.className = `vessel-card ${isBest ? 'selected' : ''}`;

    let badgeClass = "optimal";
    if (!v.feasible) badgeClass = "infeasible";
    else if (v.status.includes("Lightering")) badgeClass = "restricted";

    card.innerHTML = `
      <span class="vessel-badge ${badgeClass}">${v.status.split(" ")[0]}</span>
      <div class="vessel-name">${v.vessel_class} ${isBest ? '⭐' : ''}</div>
      <div class="vessel-stat">
        <span>Capacity</span>
        <b>${(v.typical_capacity_dwt / 1000).toFixed(0)}k DWT</b>
      </div>
      <div class="vessel-stat">
        <span>Draft Margin</span>
        <b style="color: ${v.draft_clearance_m >= 0 ? '#00f5a0' : '#ff4d6d'};">${v.draft_clearance_m >= 0 ? '+' : ''}${v.draft_clearance_m.toFixed(1)}m</b>
      </div>
      <div class="vessel-freight-rate">
        $${v.effective_sea_freight_usd_ton.toFixed(2)} <span style="font-size: 0.72rem; color: #94a3b8; font-weight: normal;">/ MT</span>
      </div>
      <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.35rem; line-height: 1.3;">${v.notes}</div>
    `;
    container.appendChild(card);
  });
}

function renderCharterRecommendation(data) {
  document.getElementById("rec-action-badge").innerText = data.market_action;
  document.getElementById("rec-urgency-text").innerText = `Timing Urgency: ${data.timing_urgency}`;
  document.getElementById("rec-laycan-window").innerText = data.optimal_laycan_window;
  document.getElementById("rec-advice-text").innerText = data.timing_advice;
  document.getElementById("rec-savings-val").innerText = `$${data.potential_freight_savings_usd.toLocaleString()}`;

  // Render Contract Types
  const contractList = document.getElementById("contract-structures-list");
  if (contractList) {
    contractList.innerHTML = "";
    data.contract_structures.forEach(c => {
      const item = document.createElement("div");
      item.style.padding = "0.7rem";
      item.style.background = "rgba(7, 13, 30, 0.5)";
      item.style.borderRadius = "8px";
      item.style.marginBottom = "0.5rem";
      item.style.border = "1px solid rgba(255,255,255,0.05)";
      item.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
          <b style="color: #00d2ff; font-size: 0.85rem;">${c.contract_type}</b>
          <span class="badge-tag badge-blue">${c.suitability}</span>
        </div>
        <div style="font-size: 0.78rem; color: #cbd5e1; margin-bottom: 0.2rem;">
          Unit Rate: <b>$${c.rate_usd_ton.toFixed(2)}/MT</b> | Total: <b>$${c.total_estimated_cost.toLocaleString()}</b>
        </div>
        <div style="font-size: 0.72rem; color: #64748b;">
          <b>Pros:</b> ${c.pros} <br/>
          <b>Cons:</b> ${c.cons}
        </div>
      `;
      contractList.appendChild(item);
    });
  }
}

function renderLandedCostTable(data) {
  const tbody = document.getElementById("landed-cost-tbody");
  if (!tbody) return;

  tbody.innerHTML = "";
  data.route_comparisons.forEach((r, idx) => {
    const isOptimal = idx === 0;
    const tr = document.createElement("tr");
    if (isOptimal) tr.className = "optimal-row";

    tr.innerHTML = `
      <td>
        <b>${r.port_name}</b> ${isOptimal ? '<span class="badge-tag badge-green">BEST</span>' : ''}
        <div style="font-size: 0.7rem; color: #64748b;">${r.rail_distance_km} km Rail | ${r.rail_transit_days}d transit</div>
      </td>
      <td>$${r.cost_breakdown_usd_ton.fob_cargo.toFixed(2)}</td>
      <td>$${r.cost_breakdown_usd_ton.ocean_freight.toFixed(2)}</td>
      <td>$${(r.cost_breakdown_usd_ton.port_dues_and_handling + r.cost_breakdown_usd_ton.lightering_transshipment).toFixed(2)}</td>
      <td>$${r.cost_breakdown_usd_ton.demurrage_risk.toFixed(2)}</td>
      <td>$${r.cost_breakdown_usd_ton.inland_rail_freight.toFixed(2)}</td>
      <td style="font-family: 'Outfit'; font-weight: 700; color: ${isOptimal ? '#00f5a0' : '#ffffff'}; font-size: 1rem;">
        $${r.landed_cost_usd_ton.toFixed(2)}
      </td>
      <td style="font-family: 'Outfit'; font-weight: 600;">
        $${(r.total_cost_usd / 1e6).toFixed(2)}M
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("landed-best-summary").innerText = 
    `Optimal Gateway: ${data.best_discharge_port} at $${data.lowest_landed_cost_usd_ton.toFixed(2)}/MT (Savings of $${data.savings_vs_alternative_usd.toLocaleString()} vs next best alternative).`;
}

/**
 * 4. Crisis & What-If Stress Simulator
 */
function initSimulatorListeners() {
  const fuelSlider = document.getElementById("sim-fuel-shock");
  const delaySlider = document.getElementById("sim-port-delay");
  const bdiSlider = document.getElementById("sim-bdi-shock");
  const canalToggle = document.getElementById("sim-canal-toggle");

  const debouncedSim = debounce(() => triggerSimulation(), 150);

  if (fuelSlider) {
    fuelSlider.addEventListener("input", (e) => {
      document.getElementById("sim-fuel-val").innerText = `${e.target.value >= 0 ? '+' : ''}${e.target.value}%`;
      debouncedSim();
    });
  }

  if (delaySlider) {
    delaySlider.addEventListener("input", (e) => {
      document.getElementById("sim-delay-val").innerText = `+${e.target.value} Days`;
      debouncedSim();
    });
  }

  if (bdiSlider) {
    bdiSlider.addEventListener("input", (e) => {
      document.getElementById("sim-bdi-val").innerText = `${e.target.value >= 0 ? '+' : ''}${e.target.value}%`;
      debouncedSim();
    });
  }

  if (canalToggle) {
    canalToggle.addEventListener("change", () => {
      debouncedSim();
    });
  }

  // Trigger initial simulation
  triggerSimulation();
}

function triggerSimulation() {
  const fuelShock = parseFloat(document.getElementById("sim-fuel-shock")?.value || 0);
  const portDelay = parseFloat(document.getElementById("sim-port-delay")?.value || 0);
  const bdiShock = parseFloat(document.getElementById("sim-bdi-shock")?.value || 0);
  const canalRerouting = document.getElementById("sim-canal-toggle")?.checked || false;

  fetch("/api/simulator/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      route_key: "freight_aus_paradip_cape",
      plant_id: "sail_rourkela",
      commodity_id: "coking_coal",
      cargo_tonnage: 150000,
      vessel_class: "Capesize",
      fuel_shock_pct: fuelShock,
      port_delay_days: portDelay,
      bdi_shock_pct: bdiShock,
      canal_rerouting_active: canalRerouting
    })
  })
  .then(res => { if (!res.ok) throw new Error(); return res.json(); })
  .then(res => {
    if (res.status === "success") renderSimulationResults(res.data);
    else throw new Error();
  })
  .catch(() => {
    renderSimulationResults(clientCalculateSimulation(fuelShock, portDelay, bdiShock, canalRerouting));
  });
}

function renderSimulationResults(data) {
  const cmp = data.comparison;
  document.getElementById("sim-res-freight").innerText = `$${cmp.stressed_freight_usd_ton.toFixed(2)}`;
  document.getElementById("sim-res-freight-delta").innerText = `${cmp.freight_delta_usd_ton >= 0 ? '+' : ''}$${cmp.freight_delta_usd_ton.toFixed(2)} (${cmp.freight_delta_pct}%)`;

  document.getElementById("sim-res-landed").innerText = `$${cmp.stressed_landed_usd_ton.toFixed(2)}`;
  document.getElementById("sim-res-landed-delta").innerText = `${cmp.landed_delta_usd_ton >= 0 ? '+' : ''}$${cmp.landed_delta_usd_ton.toFixed(2)}/MT`;

  document.getElementById("sim-res-demurrage").innerText = `+$${cmp.demurrage_extra_cost_usd.toLocaleString()}`;

  const mitigationsList = document.getElementById("sim-mitigations-list");
  if (mitigationsList) {
    mitigationsList.innerHTML = "";
    data.mitigation_actions.forEach(m => {
      const li = document.createElement("div");
      li.style.padding = "0.55rem 0.8rem";
      li.style.background = "rgba(0, 210, 255, 0.06)";
      li.style.borderRadius = "6px";
      li.style.borderLeft = "3px solid #00d2ff";
      li.style.fontSize = "0.78rem";
      li.style.marginBottom = "0.4rem";
      li.innerHTML = `🛡️ <b>Mitigation:</b> ${m}`;
      mitigationsList.appendChild(li);
    });
  }
}

/**
 * 5. Client-Side Deterministic Algorithms (Instant Offline / Static Fallback)
 */
function clientCalculateVesselOptimizer(portId, cargoTonnage, commodityId) {
  const port = PORTS_DATA[portId] || PORTS_DATA["paradip"];
  const evaluations = [];
  const baseFreight = 16.50;

  for (const [className, v] of Object.entries(VESSELS_DATA)) {
    const arrivalDraft = v.ballast_draft_meters + (v.design_draft_meters - v.ballast_draft_meters) * Math.min(1.0, cargoTonnage / v.max_dwt);
    const draftClearance = port.max_draft_meters - arrivalDraft;
    const isDirectFeasible = draftClearance >= 0.5;
    const canLighter = !isDirectFeasible && port.lightering_cost_usd_ton > 0;
    const feasible = isDirectFeasible || canLighter;

    let status = "Feasible (Direct Berth)";
    if (!feasible) status = "Infeasible (Excess Draft)";
    else if (canLighter) status = "Restricted (Requires Offshore Lightering)";

    const effectiveSeaFreight = (baseFreight * v.freight_cost_factor) + (canLighter ? port.lightering_cost_usd_ton : 0);

    let notes = "";
    if (isDirectFeasible) notes = `Full cargo draft clearance (+${draftClearance.toFixed(1)}m UKC) at ${port.name}.`;
    else if (canLighter) notes = `Draft exceeds berth limit by ${Math.abs(draftClearance).toFixed(1)}m. Mandatory lightering (+$${port.lightering_cost_usd_ton}/MT).`;
    else notes = `Vessel draft exceeds port threshold. Cannot call at ${port.name}.`;

    evaluations.push({
      vessel_class: className,
      typical_capacity_dwt: v.typical_capacity_dwt,
      arrival_draft_m: Math.round(arrivalDraft * 10) / 10,
      port_max_draft_m: port.max_draft_meters,
      draft_clearance_m: Math.round(draftClearance * 10) / 10,
      feasible: feasible,
      requires_lightering: canLighter,
      status: status,
      effective_sea_freight_usd_ton: Math.round(effectiveSeaFreight * 100) / 100,
      notes: notes
    });
  }

  const feasibleVessels = evaluations.filter(e => e.feasible);
  feasibleVessels.sort((a, b) => a.effective_sea_freight_usd_ton - b.effective_sea_freight_usd_ton);
  const bestVessel = feasibleVessels.length > 0 ? feasibleVessels[0].vessel_class : "Capesize";

  return {
    evaluated_port: port.name,
    cargo_tonnage: cargoTonnage,
    best_recommended_vessel: bestVessel,
    vessel_evaluations: evaluations
  };
}

function clientCalculateCharterRecommender(cargoTonnage) {
  const currentSpot = 16.50;
  const minRate = 14.85;
  const savingsPerTon = currentSpot - minRate;
  const potentialSavings = Math.round(savingsPerTon * cargoTonnage);

  return {
    market_action: "HOLD / DELAY FIXTURE",
    timing_urgency: "PATIENT (Softening Curve)",
    optimal_laycan_window: "18 Sep – 23 Sep 2026",
    timing_advice: `Forecasting model detects softening freight pressure. A cost trough of $${minRate.toFixed(2)}/MT is projected around Day +15. Delaying tender fixture could yield up to $${potentialSavings.toLocaleString()} in ocean freight savings.`,
    potential_freight_savings_usd: potentialSavings,
    contract_structures: [
      {
        contract_type: "Spot Voyage Charter",
        rate_usd_ton: 14.85,
        total_estimated_cost: Math.round(14.85 * cargoTonnage),
        suitability: "RECOMMENDED (Optimal Timing)",
        pros: "Captures anticipated freight softening in Day +15 laycan.",
        cons: "Demurrage exposure during Bay of Bengal monsoon swells."
      },
      {
        contract_type: "Short-Term Time Charter (45 Days)",
        rate_usd_ton: 16.20,
        total_estimated_cost: Math.round(16.20 * cargoTonnage),
        suitability: "MODERATE",
        pros: "Guaranteed vessel availability; no port demurrage risk.",
        cons: "Carries full marine bunker fuel volatility risk."
      },
      {
        contract_type: "Contract of Affreightment (COA - 1 Year)",
        rate_usd_ton: 15.60,
        total_estimated_cost: Math.round(15.60 * cargoTonnage),
        suitability: "ATTRACTIVE FOR LONG TERM",
        pros: "Fixed rate hedge protects against unexpected Cape rallies.",
        cons: "Sacrifices spot downward troughs."
      }
    ]
  };
}

function clientCalculateLandedCost(plantId, commodityId, cargoTonnage, vesselClass) {
  const plant = PLANTS_DATA[plantId] || PLANTS_DATA["sail_rourkela"];
  const commodity = COMMODITIES_DATA[commodityId] || COMMODITIES_DATA["coking_coal"];
  const vessel = VESSELS_DATA[vesselClass] || VESSELS_DATA["Capesize"];

  const fobPrice = commodity.benchmark_price_usd_ton;
  const baseFreight = 16.50 * vessel.freight_cost_factor;
  const bafPerTon = 0.38;

  const routeComparisons = [];

  for (const [portId, railInfo] of Object.entries(plant.preferred_ports)) {
    const port = PORTS_DATA[portId];
    if (!port) continue;

    const requiresLightering = port.max_draft_meters < vessel.design_draft_meters;
    const lighteringCost = requiresLightering ? port.lightering_cost_usd_ton : 0.0;
    const oceanFreightTotal = baseFreight + bafPerTon;
    const demurragePerTon = (port.avg_waiting_days * port.daily_demurrage_usd) / cargoTonnage;
    const railFreightPerTon = railInfo.rail_distance_km * 0.022;
    const landedPerTon = fobPrice + oceanFreightTotal + port.port_dues_usd_ton + lighteringCost + demurragePerTon + railFreightPerTon;

    routeComparisons.push({
      port_id: portId,
      port_name: port.name,
      rail_distance_km: railInfo.rail_distance_km,
      rail_transit_days: railInfo.transit_days,
      cost_breakdown_usd_ton: {
        fob_cargo: fobPrice,
        ocean_freight: oceanFreightTotal,
        port_dues_and_handling: port.port_dues_usd_ton,
        lightering_transshipment: lighteringCost,
        demurrage_risk: Math.round(demurragePerTon * 100) / 100,
        inland_rail_freight: Math.round(railFreightPerTon * 100) / 100
      },
      landed_cost_usd_ton: Math.round(landedPerTon * 100) / 100,
      total_cost_usd: Math.round(landedPerTon * cargoTonnage)
    });
  }

  routeComparisons.sort((a, b) => a.landed_cost_usd_ton - b.landed_cost_usd_ton);
  const best = routeComparisons[0];
  const second = routeComparisons[1] || best;
  const savings = Math.max(0, Math.round((second.landed_cost_usd_ton - best.landed_cost_usd_ton) * cargoTonnage));

  return {
    plant_name: plant.name,
    commodity_name: commodity.name,
    best_discharge_port: best.port_name,
    lowest_landed_cost_usd_ton: best.landed_cost_usd_ton,
    savings_vs_alternative_usd: savings,
    route_comparisons: routeComparisons
  };
}

function clientCalculateSimulation(fuelShock, portDelay, bdiShock, canalRerouting) {
  const baseSpot = 16.50;
  const fuelImpact = baseSpot * (fuelShock * 0.0035);
  const bdiImpact = baseSpot * (bdiShock * 0.0040);
  const rerouteImpact = canalRerouting ? 7.50 : 0.0;
  const stressedFreight = Math.round((baseSpot + fuelImpact + bdiImpact + rerouteImpact) * 100) / 100;
  const freightDelta = Math.round((stressedFreight - baseSpot) * 100) / 100;
  const freightPct = Math.round((freightDelta / baseSpot) * 1000) / 10;

  const baseLanded = 296.80;
  const extraDemurrage = Math.round(portDelay * 24000);
  const extraDemurragePerTon = extraDemurrage / 150000;
  const stressedLanded = Math.round((baseLanded + freightDelta + extraDemurragePerTon) * 100) / 100;
  const landedDelta = Math.round((stressedLanded - baseLanded) * 100) / 100;

  const mitigations = [];
  if (fuelShock > 15) mitigations.push("Institute Slow-Steaming protocol (reduce speed from 14 knots to 11.5 knots, trimming daily bunker burn by 28%).");
  if (portDelay >= 3) mitigations.push("Divert incoming Capesize vessels from congested Paradip to deep-water Dhamra or Vizag Gangavaram to bypass berth queue.");
  if (canalRerouting) mitigations.push("Fix long-term Cape of Good Hope bunker hedges at Durban / Port Louis to offset 12-day transit premium.");
  if (bdiShock > 20) mitigations.push("Lock forward quarterly requirements under Index-Linked COA with cap-and-collar collars to cap spot spike exposure.");
  if (mitigations.length === 0) mitigations.push("Standard operating procedures: monitor Baltic Capesize forward curves and maintain 21-day safety inventory at blast furnaces.");

  return {
    comparison: {
      stressed_freight_usd_ton: stressedFreight,
      freight_delta_usd_ton: freightDelta,
      freight_delta_pct: freightPct,
      stressed_landed_usd_ton: stressedLanded,
      landed_delta_usd_ton: landedDelta,
      demurrage_extra_cost_usd: extraDemurrage
    },
    mitigation_actions: mitigations
  };
}

/**
 * 6. Procurement Tender Report Generator Modal
 */
function generateProcurementReport() {
  const container = document.getElementById("report-modal-body");
  if (!container) return;

  const now = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  const plant = document.getElementById("tender-plant")?.options[document.getElementById("tender-plant").selectedIndex]?.text || "SAIL Rourkela Steel Plant";
  const commodity = document.getElementById("tender-commodity")?.options[document.getElementById("tender-commodity").selectedIndex]?.text || "Prime Hard Coking Coal";
  const tonnage = parseFloat(document.getElementById("tender-tonnage")?.value) || 150000;
  const action = document.getElementById("rec-action-badge")?.innerText || "HOLD / DELAY FIXTURE";
  const laycan = document.getElementById("rec-laycan-window")?.innerText || "18 Sep – 23 Sep 2026";
  const savings = document.getElementById("rec-savings-val")?.innerText || "$247,500";

  container.innerHTML = `
    <div style="border-bottom: 2px solid #00d2ff; padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style="font-family: 'Outfit'; color: #ffffff; font-size: 1.4rem;">NAVI-STEEL TENDER STRATEGY BRIEF</h2>
        <span style="font-size: 0.8rem; color: #94a3b8;">Ref: SIH-26006 / ${now}</span>
      </div>
      <div style="font-size: 0.85rem; color: #00d2ff;">Ministry of Steel | Bulk Cargo Procurement & Vessel Chartering Recommendation</div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
      <div style="background: rgba(7, 13, 30, 0.6); padding: 0.8rem; border-radius: 8px;">
        <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">Consignee Plant</div>
        <div style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">${plant}</div>
      </div>
      <div style="background: rgba(7, 13, 30, 0.6); padding: 0.8rem; border-radius: 8px;">
        <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">Cargo Parcel</div>
        <div style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">${tonnage.toLocaleString()} MT ${commodity}</div>
      </div>
      <div style="background: rgba(7, 13, 30, 0.6); padding: 0.8rem; border-radius: 8px;">
        <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">Optimal Laycan Window</div>
        <div style="font-weight: 700; color: #00f5a0; font-size: 0.95rem;">${laycan}</div>
      </div>
    </div>

    <div style="background: rgba(0, 210, 255, 0.08); border-left: 4px solid #00d2ff; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
      <div style="font-weight: 700; color: #00d2ff; font-size: 0.95rem; margin-bottom: 0.3rem;">EXECUTIVE ACTION: ${action}</div>
      <div style="font-size: 0.82rem; color: #e2e8f0; line-height: 1.4;">
        ${document.getElementById("rec-advice-text")?.innerText || "Market conditions favor patient execution."}
      </div>
      <div style="margin-top: 0.6rem; font-size: 0.82rem; color: #00f5a0; font-weight: 600;">
        Estimated Freight Savings: ${savings}
      </div>
    </div>

    <h4 style="color: #ffffff; font-family: 'Outfit'; margin-bottom: 0.6rem;">Multi-Port Landed Cost Benchmark:</h4>
    <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 1rem;">
      ${document.getElementById("landed-best-summary")?.innerText || ""}
    </div>

    <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
      <button class="btn btn-outline" onclick="window.print()">🖨️ Print / Save as PDF</button>
      <button class="btn btn-primary" onclick="alert('Procurement tender parameters exported to Indian Railways / SAIL e-portal format.')">📤 Dispatch to Tender Committee</button>
    </div>
  `;
}

// Utility: Debounce
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}
