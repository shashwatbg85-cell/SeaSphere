/**
 * NAVI-STEEL Main Application Logic
 * Integrates Freight Forecasting, Vessel Optimization, Landed Cost Analysis, and Crisis Simulation.
 */

let forecastChart = null;
let currentForecastData = null;
let currentActiveHorizon = "all";

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
    .then(res => res.json())
    .then(res => {
      if (res.status !== "success") return;
      const d = res.data;

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
    })
    .catch(err => console.error("Error loading snapshot:", err));
}

/**
 * 2. Fetch & Render Multi-Horizon Freight Forecast with Chart.js
 */
function loadForecast(routeKey) {
  fetch(`/api/forecast?route=${routeKey}`)
    .then(res => res.json())
    .then(res => {
      if (res.status !== "success") return;
      currentForecastData = res.data;
      renderForecastView(currentForecastData);
    })
    .catch(err => console.error("Error loading forecast:", err));
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

  // A. Call Vessel Optimizer API
  fetch("/api/optimizer/vessel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      port_id: portId,
      cargo_tonnage: tonnage,
      commodity_id: commodityId
    })
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === "success") renderVesselCards(res.data);
  });

  // B. Call Charter Recommender API
  fetch("/api/optimizer/charter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      route_key: "freight_aus_paradip_cape",
      cargo_tonnage: tonnage,
      max_lead_days: 45
    })
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === "success") renderCharterRecommendation(res.data);
  });

  // C. Call Total Landed Cost API
  fetch("/api/optimizer/landed-cost", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      plant_id: plantId,
      origin_id: "hay_point",
      commodity_id: commodityId,
      cargo_tonnage: tonnage,
      vessel_class: vesselClass
    })
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === "success") renderLandedCostTable(res.data);
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

  const debouncedSim = debounce(() => triggerSimulation(), 200);

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
  .then(res => res.json())
  .then(res => {
    if (res.status === "success") renderSimulationResults(res.data);
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
 * 5. Procurement Tender Report Generator Modal
 */
function generateProcurementReport() {
  const container = document.getElementById("report-modal-body");
  if (!container) return;

  const now = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  const plant = document.getElementById("tender-plant").options[document.getElementById("tender-plant").selectedIndex].text;
  const commodity = document.getElementById("tender-commodity").options[document.getElementById("tender-commodity").selectedIndex].text;
  const tonnage = parseFloat(document.getElementById("tender-tonnage").value) || 150000;
  const action = document.getElementById("rec-action-badge").innerText;
  const laycan = document.getElementById("rec-laycan-window").innerText;
  const savings = document.getElementById("rec-savings-val").innerText;

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
        ${document.getElementById("rec-advice-text").innerText}
      </div>
      <div style="margin-top: 0.6rem; font-size: 0.82rem; color: #00f5a0; font-weight: 600;">
        Estimated Freight Savings: ${savings}
      </div>
    </div>

    <h4 style="color: #ffffff; font-family: 'Outfit'; margin-bottom: 0.6rem;">Multi-Port Landed Cost Benchmark:</h4>
    <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 1rem;">
      ${document.getElementById("landed-best-summary").innerText}
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
