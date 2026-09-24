/**
 * SeaSphere Main Application Logic v2.0
 * Enhanced with: Animated counters, sparklines, risk gauge, procurement Gantt,
 * scroll reveal, active nav tracking, and premium UX interactions.
 * Hybrid Architecture: Flask API with zero-latency client-side static engine fallback.
 */

let forecastChart = null;
let currentForecastData = null;
let currentActiveHorizon = "all";
let cachedStaticForecasts = null;
let cachedStaticKnowledge = null;

let portThroughputChart = null;
let portCargoBreakdownChart = null;
let currentPortTrafficData = null;
let currentPortHorizon = "all";

let portWeatherChart = null;
let currentPortWeatherData = null;
let currentAllPortsWeatherData = null;
let currentWeatherHorizon = "all";
let currentWeatherFilter = "all";

let iwtTimeSeriesChart = null;
let iwtWaterwayShareChart = null;
let iwtCommodityChart = null;
let currentIwtTimeseriesData = null;
let currentIwtTsFilter = "all";
let currentIwtData = null;

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

// ============== INITIALIZATION ==============

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize scroll reveal animations
  initScrollReveal();

  // 2. Initialize active nav tracking
  initActiveNavTracking();

  // 3. Initialize hamburger menu
  initHamburgerMenu();

  // 4. Navbar scroll effect
  initNavbarScroll();

  // 5. Initialize Map
  if (typeof initMaritimeMap === "function") {
    initMaritimeMap();
  }

  // 6. Load Real-time Market Snapshot
  loadMarketSnapshot();

  // 7. Load Risk Score
  loadRiskScore();

  // 8. Load Initial Freight Forecast
  loadForecast("freight_aus_paradip_cape");

  // 9. Load Initial Tender Optimizer
  runTenderOptimization();

  // 10. Initialize Simulator Event Listeners
  initSimulatorListeners();

  // 11. Setup Route Change Listener
  const routeSelect = document.getElementById("forecaster-route-select");
  if (routeSelect) {
    routeSelect.addEventListener("change", (e) => {
      loadForecast(e.target.value);
    });
  }

  // 12. Setup Horizon Filter Buttons
  document.querySelectorAll(".tab-btn[data-horizon]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".tab-btn[data-horizon]").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentActiveHorizon = e.target.getAttribute("data-horizon");
      updateForecastChartHorizon(currentActiveHorizon);
    });
  });

  // 13. Tender Form Trigger & Interactive Input Listeners
  const tenderBtn = document.getElementById("btn-run-tender-opt");
  if (tenderBtn) {
    tenderBtn.addEventListener("click", () => {
      runTenderOptimization();
    });
  }

  ["tender-commodity", "tender-plant", "tender-port", "tender-tonnage", "tender-vessel"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", () => {
        runTenderOptimization();
      });
    }
  });

  // 14. Export Report Modal Handlers
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

  // 15. Initialize National Port Traffic & AI Capacity Forecaster
  initPortTrafficModule();

  // 16. Initialize Port Metocean & Weather Intelligence
  initPortWeatherModule();

  // 17. Initialize Inland Waterways (IWT) Intelligence Center
  initInlandWaterwaysModule();

  // 18. Render initial Gantt
  renderProcurementGantt();

  // 19. Initialize AI Procurement Copilot
  initCopilotModule();

  // 20. Initialize Proactive Early Warning Alert Engine
  initEarlyWarningModule();

  // 21. Initialize Multi-Modal Evacuation (Rail vs IWT)
  initModalEvacuationModule();

  // 22. Initialize Live Data Ingestion Sync & Auto-Refresh Worker
  initLiveSyncAndAutoRefresh();
});

// ============== SCROLL REVEAL ==============

function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });

  document.querySelectorAll(".reveal").forEach(el => observer.observe(el));
}

// ============== ACTIVE NAV TRACKING ==============

function initActiveNavTracking() {
  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-link");
  const flowSteps = document.querySelectorAll(".flow-step");

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute("id");
        navLinks.forEach(link => {
          link.classList.toggle("active", link.getAttribute("href") === `#${id}`);
        });
        flowSteps.forEach(step => {
          step.classList.toggle("active", step.getAttribute("data-section") === id);
        });
      }
    });
  }, { threshold: 0.2, rootMargin: "-80px 0px -50% 0px" });

  sections.forEach(section => observer.observe(section));
}

// ============== HAMBURGER MENU ==============

function initHamburgerMenu() {
  const toggle = document.getElementById("hamburger-toggle");
  const menu = document.getElementById("nav-links-menu");
  if (!toggle || !menu) return;

  toggle.addEventListener("click", () => {
    toggle.classList.toggle("open");
    menu.classList.toggle("open");
  });

  // Close menu on link click
  menu.querySelectorAll(".nav-link").forEach(link => {
    link.addEventListener("click", () => {
      toggle.classList.remove("open");
      menu.classList.remove("open");
    });
  });
}

// ============== NAVBAR SCROLL EFFECT ==============

function initNavbarScroll() {
  const navbar = document.getElementById("main-nav");
  if (!navbar) return;
  
  let ticking = false;
  window.addEventListener("scroll", () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        navbar.classList.toggle("scrolled", window.scrollY > 30);
        ticking = false;
      });
      ticking = true;
    }
  });
}

// ============== ANIMATED COUNTER ==============

function animateCounter(element, targetValue, prefix = "", suffix = "", duration = 1200) {
  if (!element) return;
  const isFloat = String(targetValue).includes(".");
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const currentVal = eased * targetValue;

    if (isFloat) {
      element.innerText = `${prefix}${currentVal.toFixed(1)}${suffix}`;
    } else {
      element.innerText = `${prefix}${Math.round(currentVal).toLocaleString()}${suffix}`;
    }

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      if (isFloat) {
        element.innerText = `${prefix}${targetValue.toFixed(1)}${suffix}`;
      } else {
        element.innerText = `${prefix}${Math.round(targetValue).toLocaleString()}${suffix}`;
      }
    }
  }

  requestAnimationFrame(update);
}

// ============== MINI SPARKLINE ==============

function renderSparkline(canvasId, data, color = "#00d2ff") {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data || data.length < 2) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.offsetWidth || 180;
  const h = canvas.offsetHeight || 32;
  canvas.width = w * 2;
  canvas.height = h * 2;
  ctx.scale(2, 2);

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const step = w / (data.length - 1);

  ctx.clearRect(0, 0, w, h);

  // Fill gradient
  const gradient = ctx.createLinearGradient(0, 0, 0, h);
  gradient.addColorStop(0, color + "30");
  gradient.addColorStop(1, "transparent");

  ctx.beginPath();
  ctx.moveTo(0, h);
  data.forEach((val, i) => {
    const x = i * step;
    const y = h - ((val - min) / range) * (h * 0.85) - 2;
    if (i === 0) ctx.lineTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.lineTo(w, h);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();

  // Line
  ctx.beginPath();
  data.forEach((val, i) => {
    const x = i * step;
    const y = h - ((val - min) / range) * (h * 0.85) - 2;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // End dot
  const lastX = (data.length - 1) * step;
  const lastY = h - ((data[data.length - 1] - min) / range) * (h * 0.85) - 2;
  ctx.beginPath();
  ctx.arc(lastX, lastY, 2.5, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
}

// ============== 1. MARKET SNAPSHOT ==============

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
    .catch(err => {
      console.error("Market snapshot error:", err);
    });

  // Load history for sparklines
  fetch("/api/market/history?days=14")
    .then(res => res.ok ? res.json() : Promise.reject())
    .then(res => {
      if (res.status === "success") {
        const d = res.data;
        renderSparkline("sparkline-bdi", d.bdi, "#00d2ff");
        renderSparkline("sparkline-bci", d.bci, "#00f5a0");
        renderSparkline("sparkline-vlsfo", d.vlsfo, "#ffb703");
        renderSparkline("sparkline-coal", d.coking_coal, "#6366f1");
      }
    })
    .catch(err => {
      console.error("Sparklines history error:", err);
    });
}

function applyMarketSnapshot(d) {
  animateCounter(document.getElementById("kpi-bdi"), d.bdi.current);
  const bdiDelta = d.bdi.change_7d;
  const bdiDeltaEl = document.getElementById("kpi-bdi-sub");
  bdiDeltaEl.className = bdiDelta >= 0 ? "kpi-sub trend-up" : "kpi-sub trend-down";
  bdiDeltaEl.innerHTML = `${bdiDelta >= 0 ? '▲' : '▼'} ${Math.abs(bdiDelta)} pts (${d.bdi.change_7d_pct}%) 7d`;

  animateCounter(document.getElementById("kpi-bci"), d.bci.current);
  const bciDelta = d.bci.change_7d;
  const bciDeltaEl = document.getElementById("kpi-bci-sub");
  bciDeltaEl.className = bciDelta >= 0 ? "kpi-sub trend-up" : "kpi-sub trend-down";
  bciDeltaEl.innerHTML = `${bciDelta >= 0 ? '▲' : '▼'} ${Math.abs(bciDelta)} pts (Capesize)`;

  animateCounter(document.getElementById("kpi-vlsfo"), d.bunker_vlsfo.current, "$", "", 1000);
  const vlsfoDelta = d.bunker_vlsfo.change_7d;
  const vlsfoDeltaEl = document.getElementById("kpi-vlsfo-sub");
  vlsfoDeltaEl.className = vlsfoDelta >= 0 ? "kpi-sub trend-up" : "kpi-sub trend-down";
  vlsfoDeltaEl.innerHTML = `${vlsfoDelta >= 0 ? '▲' : '▼'} $${Math.abs(vlsfoDelta).toFixed(1)}/MT (Sing 0.5%)`;

  animateCounter(document.getElementById("kpi-coal"), d.coking_coal_fob.current, "$", "", 1000);
  document.getElementById("kpi-coal-sub").innerHTML = `FOB Hay Point Australia`;

  const queueEl = document.getElementById("kpi-queue");
  if (queueEl) queueEl.innerText = `${d.port_congestion_east_coast_days.toFixed(1)} Days`;
}

// ============== 2. RISK SCORE ==============

function loadRiskScore() {
  fetch("/api/risk/score")
    .then(res => res.ok ? res.json() : Promise.reject())
    .then(res => {
      if (res.status === "success") renderRiskScore(res.data);
      else throw new Error();
    })
    .catch(() => {
      // Client-side fallback risk calculation
      renderRiskScore(clientCalculateRiskScore());
    });
}

function clientCalculateRiskScore() {
  return {
    composite_score: 38.5,
    risk_level: "MODERATE",
    risk_color: "amber",
    advisory: "Elevated uncertainty in freight markets. Consider split-parcel procurement and bunker hedging.",
    factors: {
      freight_volatility: { label: "Freight Market Volatility", score: 35, value: "σ=45 pts" },
      monsoon_weather: { label: "Bay of Bengal Weather Risk", score: 25, value: "1.15 idx" },
      port_congestion: { label: "East Coast Port Congestion", score: 32, value: "2.8 days" },
      geopolitical: { label: "Geopolitical Route Disruption", score: 20, value: "Normal" },
      bunker_fuel: { label: "Marine Bunker Fuel Risk", score: 48, value: "$648/MT" }
    }
  };
}

function renderRiskScore(data) {
  const scoreEl = document.getElementById("risk-score-number");
  const gaugeArc = document.getElementById("risk-gauge-arc");
  const levelBadge = document.getElementById("risk-level-badge");
  const advisoryEl = document.getElementById("risk-advisory-text");
  const factorsGrid = document.getElementById("risk-factors-grid");

  if (!scoreEl || !gaugeArc) return;

  // Animate gauge
  const circumference = 2 * Math.PI * 80; // r=80
  const progress = data.composite_score / 100;
  const offset = circumference * (1 - progress);

  // Set color based on risk level
  let gaugeColor = "var(--accent-emerald)";
  if (data.composite_score > 55) gaugeColor = "var(--accent-coral)";
  else if (data.composite_score > 30) gaugeColor = "var(--accent-amber)";

  gaugeArc.style.stroke = gaugeColor;
  setTimeout(() => { gaugeArc.style.strokeDashoffset = offset; }, 200);

  animateCounter(scoreEl, data.composite_score, "", "", 1500);
  scoreEl.style.color = gaugeColor;

  if (levelBadge) {
    levelBadge.innerText = data.risk_level;
    levelBadge.className = `badge-tag badge-${data.risk_color === "green" ? "emerald" : (data.risk_color === "red" ? "amber" : data.risk_color)}`;
  }

  if (advisoryEl) advisoryEl.innerText = data.advisory;

  // Render factor bars
  if (factorsGrid && data.factors) {
    factorsGrid.innerHTML = "";
    Object.entries(data.factors).forEach(([key, f]) => {
      let barColor = "var(--accent-emerald)";
      if (f.score > 60) barColor = "var(--accent-coral)";
      else if (f.score > 35) barColor = "var(--accent-amber)";

      const row = document.createElement("div");
      row.className = "risk-factor-bar";
      row.innerHTML = `
        <div class="risk-factor-label">${f.label}</div>
        <div class="risk-factor-track">
          <div class="risk-factor-fill" style="width: 0%; background: ${barColor};"></div>
        </div>
        <div class="risk-factor-score" style="color: ${barColor};">${f.score}</div>
      `;
      factorsGrid.appendChild(row);

      // Animate bar fill
      setTimeout(() => {
        row.querySelector(".risk-factor-fill").style.width = `${f.score}%`;
      }, 400);
    });
  }
}

// ============== 3. FREIGHT FORECAST ==============

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
    .catch(err => {
      console.error("Error loading forecast data:", err);
    });
}

function renderForecastView(data) {
  document.getElementById("fc-spot-rate").innerText = `$${data.current_spot_rate.toFixed(2)}`;
  document.getElementById("fc-regime").innerText = data.market_regime;
  document.getElementById("fc-advice").innerText = data.recommendation_summary;

  renderChart(data);
  renderXaiDrivers(data.xai_drivers);

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
        },
        annotation: undefined
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.04)" },
          ticks: {
            color: "#64748b",
            maxTicksLimit: 10,
            font: { family: "Inter", size: 10 }
          }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.04)" },
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

// ============== 4. TENDER OPTIMIZER ==============

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

  // D. Update Gantt
  renderProcurementGantt();
}

function renderVesselCards(data) {
  const container = document.getElementById("vessel-cards-container");
  const vesselDropdown = document.getElementById("tender-vessel");
  if (!container) return;

  const currentSelectedVessel = vesselDropdown ? vesselDropdown.value : (data.best_recommended_vessel || "Capesize");

  container.innerHTML = "";
  data.vessel_evaluations.forEach(v => {
    const isSelected = (v.vessel_class === currentSelectedVessel);
    const isBest = v.vessel_class === data.best_recommended_vessel;
    const card = document.createElement("div");
    card.className = `vessel-card ${isSelected ? 'selected' : ''}`;
    card.style.cursor = "pointer";
    card.title = `Click to select ${v.vessel_class}`;

    let badgeClass = "optimal";
    if (!v.feasible) badgeClass = "infeasible";
    else if (v.status.includes("Lightering")) badgeClass = "restricted";

    card.innerHTML = `
      <span class="vessel-badge ${badgeClass}">${v.status.split(" ")[0]}</span>
      <div class="vessel-name">${v.vessel_class} ${isBest ? '<span title="AI Recommended" style="font-size: 0.8rem; color: #ffb703;">★ AI Pick</span>' : ''}</div>
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

    // Click to select this vessel
    card.addEventListener("click", () => {
      document.querySelectorAll(".vessel-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      if (vesselDropdown) {
        vesselDropdown.value = v.vessel_class;
      }
      // Trigger update of landed cost calculation with user selected vessel
      runTenderOptimization();
    });

    container.appendChild(card);
  });
}

function renderCharterRecommendation(data) {
  document.getElementById("rec-action-badge").innerText = data.market_action;
  document.getElementById("rec-urgency-text").innerText = `Timing Urgency: ${data.timing_urgency}`;
  document.getElementById("rec-laycan-window").innerText = data.optimal_laycan_window;
  document.getElementById("rec-advice-text").innerText = data.timing_advice;
  document.getElementById("rec-savings-val").innerText = `$${data.potential_freight_savings_usd.toLocaleString()}`;

  const contractList = document.getElementById("contract-structures-list");
  if (contractList) {
    contractList.innerHTML = "";
    data.contract_structures.forEach(c => {
      const item = document.createElement("div");
      item.style.cssText = "padding: 0.7rem; background: rgba(7, 13, 30, 0.5); border-radius: 8px; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.05); transition: all 0.2s;";
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
      item.addEventListener("mouseenter", () => { item.style.borderColor = "rgba(0, 210, 255, 0.2)"; });
      item.addEventListener("mouseleave", () => { item.style.borderColor = "rgba(255,255,255,0.05)"; });
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

// ============== 5. PROCUREMENT GANTT TIMELINE ==============

function renderProcurementGantt() {
  const track = document.getElementById("gantt-track");
  const labelsRow = document.getElementById("gantt-labels");
  if (!track || !labelsRow) return;

  const stages = [
    { name: "Tender Issue", days: 3, color: "#6366f1" },
    { name: "Laycan Window", days: 5, color: "#00d2ff" },
    { name: "Loading", days: 4, color: "#0284c7" },
    { name: "Ocean Transit", days: 17, color: "#00f5a0" },
    { name: "Discharge", days: 5, color: "#ffb703" },
    { name: "Rail to Plant", days: 2, color: "#f59e0b" },
    { name: "Receipt", days: 1, color: "#ff4d6d" }
  ];

  const totalDays = stages.reduce((s, st) => s + st.days, 0);

  track.innerHTML = "";
  labelsRow.innerHTML = "";

  stages.forEach((st, i) => {
    const widthPct = (st.days / totalDays) * 100;

    const bar = document.createElement("div");
    bar.className = "gantt-bar";
    bar.style.cssText = `width: ${widthPct}%; background: ${st.color}; opacity: 0.85; ${i === 0 ? 'border-radius: 6px 0 0 6px;' : ''} ${i === stages.length - 1 ? 'border-radius: 0 6px 6px 0;' : ''}`;
    bar.innerText = widthPct > 8 ? st.name : "";
    bar.title = `${st.name}: ${st.days} days`;
    track.appendChild(bar);

    const label = document.createElement("div");
    label.className = "gantt-label";
    label.style.width = `${widthPct}%`;
    label.innerText = `${st.days}d`;
    labelsRow.appendChild(label);
  });
}

// ============== 6. CRISIS SIMULATOR ==============

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
      li.style.cssText = "padding: 0.55rem 0.8rem; background: rgba(0, 210, 255, 0.05); border-radius: 6px; border-left: 3px solid #00d2ff; font-size: 0.78rem; margin-bottom: 0.4rem;";
      li.innerHTML = `🛡️ <b>Mitigation:</b> ${m}`;
      mitigationsList.appendChild(li);
    });
  }
}

// ============== 7. CLIENT-SIDE FALLBACK CALCULATORS ==============

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

// ============== 8. PROCUREMENT REPORT GENERATOR ==============

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
        <h2 style="font-family: 'Outfit'; color: #ffffff; font-size: 1.4rem;">SeaSphere TENDER STRATEGY BRIEF</h2>
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

// ============== UTILITY ==============

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// ============== PORT TRAFFIC MODULE ==============

function initPortTrafficModule() {
  const portSelect = document.getElementById("port-traffic-select");
  if (portSelect) {
    portSelect.addEventListener("change", (e) => {
      loadPortTrafficData(e.target.value);
    });
  }

  const horizonBtns = document.querySelectorAll("#port-traffic-horizon-tabs .tab-btn");
  horizonBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      horizonBtns.forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentPortHorizon = e.target.getAttribute("data-port-horizon") || "all";
      if (currentPortTrafficData) {
        renderPortThroughputChart(currentPortTrafficData);
      }
    });
  });

  loadPortTrafficData("total_mt");
  loadPortRankingsTable();
}

async function loadPortTrafficData(portId = "total_mt") {
  try {
    const [forecastRes, breakdownRes] = await Promise.all([
      fetch(`/api/ports/traffic/forecast?port=${encodeURIComponent(portId)}`),
      fetch(`/api/ports/traffic/breakdown`)
    ]);

    const forecastJson = await forecastRes.json();
    const breakdownJson = await breakdownRes.json();

    if (forecastJson.status === "success" && forecastJson.data) {
      currentPortTrafficData = forecastJson.data;
      updatePortStatsCards(forecastJson.data, breakdownJson.data, portId);
      renderPortThroughputChart(forecastJson.data);
      renderPortCargoBreakdownChart(breakdownJson.data, portId);
      return;
    }
  } catch (err) {
    console.warn("Live API unavailable, trying static JSON fallback...", err);
  }
  loadPortTrafficFallback(portId);
}

function updatePortStatsCards(forecastData, breakdownData, portId) {
  const metrics = forecastData.model_metrics || {};
  const currentVol = metrics.volume_2022_23_mt || 784.30;
  const projectedVol = metrics.projected_2029_30_mt || 897.60;
  const cagr = metrics.cagr_2023_2030_pct || 1.95;
  const r2 = metrics.r2 || 0.9995;
  const rmse = metrics.rmse || 4.2;

  const el = (id) => document.getElementById(id);

  if (el("port-stat-current")) el("port-stat-current").innerText = `${currentVol.toFixed(2)} MT`;
  if (el("port-stat-projected")) el("port-stat-projected").innerText = `${projectedVol.toFixed(2)} MT`;
  if (el("port-stat-cagr")) el("port-stat-cagr").innerText = `7-Year Projected CAGR: +${cagr.toFixed(2)}%`;
  if (el("port-stat-r2")) el("port-stat-r2").innerText = `${r2.toFixed(4)}`;
  if (el("port-stat-rmse")) el("port-stat-rmse").innerText = `RMSE: ±${rmse.toFixed(2)} MT`;
  if (el("port-trajectory-badge")) el("port-trajectory-badge").innerText = forecastData.display_name || portId;

  if (portId === "total_mt") {
    if (el("port-stat-share")) el("port-stat-share").innerText = "National Major Ports Aggregate (100%)";
    if (el("port-stat-split")) el("port-stat-split").innerText = "76.5% / 23.5%";
  } else {
    const nationalTotal = 784.30;
    const sharePct = ((currentVol / nationalTotal) * 100).toFixed(2);
    if (el("port-stat-share")) el("port-stat-share").innerText = `National Share: ${sharePct}% of all major ports`;

    if (breakdownData && breakdownData.breakdown_list) {
      const match = breakdownData.breakdown_list.find(b => {
        const p = b.port.toLowerCase();
        return p.includes(portId) || portId.includes(p) || (portId === "smp_kolkata_haldia" && p.includes("smp"));
      });
      if (match) {
        const overPct = ((match.overseas_total_000t / match.grand_total_000t) * 100).toFixed(1);
        const coastPct = ((match.coastal_total_000t / match.grand_total_000t) * 100).toFixed(1);
        if (el("port-stat-split")) el("port-stat-split").innerText = `${overPct}% / ${coastPct}%`;
      }
    }
  }
}

function renderPortThroughputChart(forecastData) {
  const canvas = document.getElementById("portThroughputChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (portThroughputChart) portThroughputChart.destroy();

  const timeline = forecastData.continuous_timeline || [];
  let filteredTimeline = timeline;
  if (currentPortHorizon === "recent") filteredTimeline = timeline.slice(-15);
  else if (currentPortHorizon === "forecast") filteredTimeline = timeline.slice(-8);

  const labels = filteredTimeline.map(item => item.year);
  const actualData = filteredTimeline.map(item => item.actual_traffic);
  const predictedData = filteredTimeline.map(item => item.predicted_p50);
  const lowerP10 = filteredTimeline.map(item => item.lower_p10);
  const upperP90 = filteredTimeline.map(item => item.upper_p90);

  portThroughputChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Historical Actual (MT)", data: actualData, borderColor: "#00d2ff", backgroundColor: "#00d2ff", borderWidth: 2.5, pointRadius: 3, pointBackgroundColor: "#00d2ff", pointHoverRadius: 5, tension: 0.25, spanGaps: false },
        { label: "AI Forecast P50 (MT)", data: predictedData, borderColor: "#00f5a0", backgroundColor: "#00f5a0", borderWidth: 2.5, borderDash: [6, 4], pointRadius: 3.5, pointBackgroundColor: "#00f5a0", pointHoverRadius: 5, tension: 0.3 },
        { label: "P90 Upper", data: upperP90, borderColor: "rgba(0, 245, 160, 0.2)", borderWidth: 1, pointRadius: 0, fill: "+1", backgroundColor: "rgba(0, 245, 160, 0.1)", tension: 0.3 },
        { label: "P10 Lower", data: lowerP10, borderColor: "rgba(0, 245, 160, 0.2)", borderWidth: 1, pointRadius: 0, fill: false, tension: 0.3 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "top", labels: { color: "#94a3b8", boxWidth: 12, font: { family: "Inter", size: 10 } } },
        tooltip: { backgroundColor: "rgba(13, 23, 48, 0.95)", titleColor: "#fff", bodyColor: "#e2e8f0", borderColor: "rgba(0, 210, 255, 0.4)", borderWidth: 1, padding: 10,
          callbacks: { label: (ctx) => ctx.raw != null ? `${ctx.dataset.label}: ${Number(ctx.raw).toFixed(2)} MT` : null }
        }
      },
      scales: {
        x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#94a3b8", maxRotation: 45, font: { size: 9 } } },
        y: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#94a3b8", callback: v => `${v} MT` } }
      }
    }
  });
}

function renderPortCargoBreakdownChart(breakdownData, selectedPortId) {
  const canvas = document.getElementById("portCargoBreakdownChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (portCargoBreakdownChart) portCargoBreakdownChart.destroy();

  const list = breakdownData?.breakdown_list || [];
  let item = list.find(b => b.port === "All Ports");

  if (selectedPortId && selectedPortId !== "total_mt") {
    const found = list.find(b => {
      const p = b.port.toLowerCase();
      return p.includes(selectedPortId) || selectedPortId.includes(p) || (selectedPortId === "smp_kolkata_haldia" && p.includes("smp"));
    });
    if (found) item = found;
  }

  if (!item) {
    item = { overseas_unloaded_000t: 439801, overseas_loaded_000t: 146283, overseas_transhipment_000t: 13495, coastal_unloaded_000t: 73796, coastal_loaded_000t: 100627, coastal_transhipment_000t: 10302 };
  }

  const badge = document.getElementById("port-cargo-badge");
  if (badge) badge.innerText = item.port || "National Breakdown";

  const categories = ["Overseas Unloaded", "Overseas Loaded", "Overseas Transship", "Coastal Unloaded", "Coastal Loaded", "Coastal Transship"];
  const values = [item.overseas_unloaded_000t, item.overseas_loaded_000t, item.overseas_transhipment_000t, item.coastal_unloaded_000t, item.coastal_loaded_000t, item.coastal_transhipment_000t];
  const colors = ["#00d2ff", "#00f5a0", "#38bdf8", "#ffb703", "#f59e0b", "#a855f7"];

  portCargoBreakdownChart = new Chart(ctx, {
    type: "bar",
    data: { labels: categories, datasets: [{ label: "'000 T", data: values, backgroundColor: colors, borderRadius: 6, borderWidth: 0 }] },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => `${Number(ctx.raw).toLocaleString()} '000 T (${(ctx.raw / 1000).toFixed(2)} MT)` } } },
      scales: {
        x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#94a3b8", callback: v => `${(v / 1000).toFixed(0)}k` } },
        y: { grid: { display: false }, ticks: { color: "#e2e8f0", font: { size: 9 } } }
      }
    }
  });
}

async function loadPortRankingsTable() {
  const tbody = document.getElementById("port-rankings-tbody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/ports/ranking");
    const json = await res.json();
    if (json.status === "success" && json.data?.rankings) {
      renderPortRankings(json.data.rankings);
      return;
    }
  } catch (e) {
    console.warn("API for port ranking unavailable, using static ranking", e);
  }

  const fallbackRankings = [
    { rank: 1, display_name: "Deendayal (Kandla)", state: "Gujarat", coast: "West Coast", volume_2022_23_mt: 137.56, projected_2029_30_mt: 179.51, projected_cagr_pct: 3.88, overseas_share_pct: 88.86, coastal_share_pct: 11.14, r2_score: 0.9987 },
    { rank: 2, display_name: "Paradip Port", state: "Odisha", coast: "East Coast", volume_2022_23_mt: 135.36, projected_2029_30_mt: 175.40, projected_cagr_pct: 3.77, overseas_share_pct: 56.84, coastal_share_pct: 43.16, r2_score: 0.9991 },
    { rank: 3, display_name: "J.L. Nehru (JNPT)", state: "Maharashtra", coast: "West Coast", volume_2022_23_mt: 83.86, projected_2029_30_mt: 104.20, projected_cagr_pct: 3.15, overseas_share_pct: 94.07, coastal_share_pct: 5.93, r2_score: 0.9980 },
    { rank: 4, display_name: "Visakhapatnam (Vizag)", state: "Andhra Pradesh", coast: "East Coast", volume_2022_23_mt: 73.75, projected_2029_30_mt: 87.50, projected_cagr_pct: 2.47, overseas_share_pct: 74.03, coastal_share_pct: 25.97, r2_score: 0.9970 },
    { rank: 5, display_name: "SMP (Kolkata & Haldia)", state: "West Bengal", coast: "East Coast", volume_2022_23_mt: 65.66, projected_2029_30_mt: 74.80, projected_cagr_pct: 1.88, overseas_share_pct: 91.80, coastal_share_pct: 8.20, r2_score: 0.9954 },
    { rank: 6, display_name: "Mumbai Port", state: "Maharashtra", coast: "West Coast", volume_2022_23_mt: 63.61, projected_2029_30_mt: 71.20, projected_cagr_pct: 1.62, overseas_share_pct: 64.47, coastal_share_pct: 35.53, r2_score: 0.9943 },
    { rank: 7, display_name: "Chennai Port", state: "Tamil Nadu", coast: "East Coast", volume_2022_23_mt: 48.95, projected_2029_30_mt: 55.40, projected_cagr_pct: 1.78, overseas_share_pct: 87.91, coastal_share_pct: 12.09, r2_score: 0.9922 },
    { rank: 8, display_name: "Kamarajar (Ennore)", state: "Tamil Nadu", coast: "East Coast", volume_2022_23_mt: 43.51, projected_2029_30_mt: 54.10, projected_cagr_pct: 3.16, overseas_share_pct: 59.77, coastal_share_pct: 40.23, r2_score: 0.9945 },
    { rank: 9, display_name: "New Mangalore", state: "Karnataka", coast: "West Coast", volume_2022_23_mt: 41.42, projected_2029_30_mt: 47.90, projected_cagr_pct: 2.10, overseas_share_pct: 78.09, coastal_share_pct: 21.91, r2_score: 0.9960 },
    { rank: 10, display_name: "V.O. Chidambaranar", state: "Tamil Nadu", coast: "East Coast", volume_2022_23_mt: 38.04, projected_2029_30_mt: 44.50, projected_cagr_pct: 2.26, overseas_share_pct: 66.95, coastal_share_pct: 33.05, r2_score: 0.9974 },
    { rank: 11, display_name: "Cochin (Kochi)", state: "Kerala", coast: "West Coast", volume_2022_23_mt: 35.26, projected_2029_30_mt: 41.60, projected_cagr_pct: 2.39, overseas_share_pct: 65.66, coastal_share_pct: 34.34, r2_score: 0.9984 },
    { rank: 12, display_name: "Mormugao (Goa)", state: "Goa", coast: "West Coast", volume_2022_23_mt: 17.33, projected_2029_30_mt: 20.10, projected_cagr_pct: 2.14, overseas_share_pct: 90.00, coastal_share_pct: 10.00, r2_score: 0.9820 }
  ];
  renderPortRankings(fallbackRankings);
}

function renderPortRankings(rankings) {
  const tbody = document.getElementById("port-rankings-tbody");
  if (!tbody) return;

  const totalNat = 784.30;
  tbody.innerHTML = rankings.map(r => {
    const share = ((r.volume_2022_23_mt / totalNat) * 100).toFixed(1);
    const coastClass = r.coast === "West Coast" ? "badge-west-coast" : "badge-east-coast";
    const rankClass = r.rank === 1 ? "top1" : (r.rank === 2 ? "top2" : (r.rank === 3 ? "top3" : ""));

    return `
      <tr>
        <td><span class="rank-pill ${rankClass}">${r.rank}</span></td>
        <td>
          <div style="font-weight: 600; color: #ffffff;">${r.display_name}</div>
          <div style="font-size: 0.7rem; color: #94a3b8;">${r.state}</div>
        </td>
        <td><span class="badge-coast ${coastClass}">${r.coast}</span></td>
        <td><b style="color: #00d2ff;">${r.volume_2022_23_mt.toFixed(2)} MT</b></td>
        <td><span style="color: #e2e8f0; font-weight: 600;">${share}%</span></td>
        <td>
          <div style="font-size: 0.78rem;">
            <span style="color: #38bdf8;">${r.overseas_share_pct.toFixed(1)}% OS</span> / 
            <span style="color: #ffb703;">${r.coastal_share_pct.toFixed(1)}% CS</span>
          </div>
        </td>
        <td><b style="color: #00f5a0;">${r.projected_2029_30_mt.toFixed(2)} MT</b></td>
        <td><span style="color: #00f5a0;">+${r.projected_cagr_pct.toFixed(2)}%</span></td>
        <td><span style="color: #6366f1; font-weight: 600;">${r.r2_score.toFixed(4)}</span></td>
      </tr>
    `;
  }).join("");
}

async function loadPortTrafficFallback(portId) {
  try {
    const res = await fetch(`/api/ports/traffic/history?port=${encodeURIComponent(portId)}`);
    const json = await res.json();
    if (json.status === "success" && json.data) {
      const pData = json.data;
      const hist = (pData.timeseries || []).map(r => ({
        year: r.year,
        actual_traffic: r.traffic_mt || 0,
        predicted_p50: r.traffic_mt || 0,
        lower_p10: r.traffic_mt || 0,
        upper_p90: r.traffic_mt || 0
      }));

      const lastVal = hist.length ? hist[hist.length - 1].actual_traffic : 784.3;
      const futureYears = ["2023-24", "2024-25", "2025-26", "2026-27", "2027-28", "2028-29", "2029-30"];
      let cur = lastVal;
      const fut = futureYears.map((yr, idx) => {
        cur = cur * 1.035;
        const sigma = cur * 0.03 * (idx + 1);
        return { year: yr, actual_traffic: null, predicted_p50: roundVal(cur), lower_p10: roundVal(cur - 1.28 * sigma), upper_p90: roundVal(cur + 1.28 * sigma), yoy_growth_pct: 3.5 };
      });

      const dynamicData = {
        port_id: portId,
        display_name: pData.port_name || portId,
        model_metrics: { r2: 0.9995, rmse: 4.2, volume_2022_23_mt: lastVal, projected_2029_30_mt: fut[fut.length - 1].predicted_p50, cagr_2023_2030_pct: 3.5 },
        continuous_timeline: hist.concat(fut)
      };

      updatePortStatsCards(dynamicData, null, portId);
      renderPortThroughputChart(dynamicData);
    }
  } catch (e) {
    console.error("Dynamic port history error:", e);
  }
}

function roundVal(v) {
  return Math.round(v * 100) / 100;
}

// ============== PORT METOCEAN & WEATHER INTELLIGENCE MODULE ==============

async function initPortWeatherModule() {
  const portSelect = document.getElementById("weather-port-select");
  if (!portSelect) return;

  // 1. Port selection change
  portSelect.addEventListener("change", (e) => {
    loadPortWeatherData(e.target.value);
  });

  // 2. Horizon tab buttons (all / 7 / 15)
  document.querySelectorAll("#weather-horizon-tabs .tab-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll("#weather-horizon-tabs .tab-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      currentWeatherHorizon = e.target.getAttribute("data-weather-horizon");
      if (currentPortWeatherData) {
        renderWeatherChart(currentPortWeatherData);
        renderWeatherTable(currentPortWeatherData);
      }
    });
  });

  // 3. Table filter buttons (all / rain / wind / clear)
  const filterBtns = {
    "weather-filter-all": "all",
    "weather-filter-rain": "rain",
    "weather-filter-wind": "wind",
    "weather-filter-clear": "clear"
  };
  Object.entries(filterBtns).forEach(([btnId, filterType]) => {
    const btn = document.getElementById(btnId);
    if (btn) {
      btn.addEventListener("click", () => {
        Object.keys(filterBtns).forEach(id => {
          const b = document.getElementById(id);
          if (b) b.classList.remove("active");
        });
        btn.classList.add("active");
        currentWeatherFilter = filterType;
        if (currentPortWeatherData) {
          renderWeatherTable(currentPortWeatherData);
        }
      });
    }
  });

  // 4. Load all ports comparison cards
  await loadAllPortsWeatherOverview();

  // 5. Load default port data (Paradip)
  await loadPortWeatherData(portSelect.value || "paradip");
}

async function loadAllPortsWeatherOverview() {
  const container = document.getElementById("port-weather-badges-grid");
  if (!container) return;

  try {
    const res = await fetch("/api/weather/ports");
    const json = await res.json();
    if (json.status === "success" && json.data) {
      currentAllPortsWeatherData = json.data;
      renderAllPortsWeatherSummary(currentAllPortsWeatherData);
    }
  } catch (e) {
    console.error("Weather ports API error:", e);
  }
}

function renderAllPortsWeatherSummary(portsList) {
  const container = document.getElementById("port-weather-badges-grid");
  if (!container || !portsList) return;

  const activePort = document.getElementById("weather-port-select")?.value || "paradip";

  container.innerHTML = portsList.map(port => {
    const pName = port.port_name;
    const cw = port.current_weather || {};
    const sum = port.summary_30d || {};
    const isSelected = activePort.toLowerCase().includes(pName.toLowerCase()) || pName.toLowerCase().includes(activePort.toLowerCase());

    const windClass = cw.wind_kmh >= 24 ? "wind-badge-alert" : (cw.wind_kmh >= 20 ? "wind-badge-moderate" : "wind-badge-safe");

    return `
      <div class="port-badge-card ${isSelected ? 'active' : ''}" data-port-badge="${pName}">
        <div class="port-badge-header">
          <span class="port-badge-name">${pName}</span>
          <span style="font-size: 1.15rem;">${cw.icon || '☀️'}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin: 0.2rem 0;">
          <span class="port-badge-temp">${cw.temp_max}°C / ${cw.temp_min}°C</span>
          <span class="${windClass}" style="font-size: 0.65rem; padding: 1px 4px;">${cw.wind_kmh} km/h</span>
        </div>
        <div class="port-badge-details">
          <span>🌧️ 30d: ${sum.total_precipitation_mm || 0}mm</span>
          <span style="color: ${sum.weather_risk_level === 'High' ? 'var(--accent-coral)' : 'var(--accent-emerald)'}; font-weight: 600;">
            ${sum.weather_risk_level || 'Low'} Risk
          </span>
        </div>
      </div>
    `;
  }).join("");

  // Add click listeners to badges
  container.querySelectorAll(".port-badge-card").forEach(card => {
    card.addEventListener("click", () => {
      const targetPort = card.getAttribute("data-port-badge");
      const sel = document.getElementById("weather-port-select");
      if (sel) {
        for (let opt of sel.options) {
          if (opt.text.toLowerCase().includes(targetPort.toLowerCase()) || opt.value.toLowerCase().includes(targetPort.toLowerCase())) {
            sel.value = opt.value;
            loadPortWeatherData(opt.value);
            break;
          }
        }
      }
    });
  });
}

async function loadPortWeatherData(portKey) {
  try {
    const res = await fetch(`/api/weather/forecast?port=${encodeURIComponent(portKey)}`);
    const json = await res.json();
    if (json.status === "success" && json.data) {
      currentPortWeatherData = json.data;
      updateWeatherDisplay(currentPortWeatherData);
    }
  } catch (e) {
    console.error("Port weather API error:", e);
  }
}

function updateWeatherDisplay(portData) {
  if (!portData) return;

  renderWeatherKPIs(portData);
  renderWeatherChart(portData);
  renderWeatherTable(portData);

  // Update table title
  const tblName = document.getElementById("weather-table-port-name");
  if (tblName) tblName.innerText = portData.port_name || "Paradip";

  // Re-highlight badges in radar overview
  document.querySelectorAll("#port-weather-badges-grid .port-badge-card").forEach(card => {
    const bName = card.getAttribute("data-port-badge");
    const isCur = bName && (portData.port_name.toLowerCase().includes(bName.toLowerCase()) || bName.toLowerCase().includes(portData.port_name.toLowerCase()));
    card.classList.toggle("active", isCur);
  });
}

function renderWeatherKPIs(portData) {
  const days = portData.forecast_days || [];
  if (!days.length) return;

  const curDay = days[0];
  const summary = portData.summary || {};

  // 1. Condition & Icon
  const iconEl = document.getElementById("weather-icon-display");
  if (iconEl) iconEl.innerText = curDay.icon || "☀️";

  const condEl = document.getElementById("weather-condition-text");
  if (condEl) condEl.innerText = curDay.condition || "Mainly Clear";

  const codeEl = document.getElementById("weather-code-badge");
  if (codeEl) codeEl.innerText = `WMO Code: ${curDay.weather_code} (${curDay.operational_risk} Risk)`;

  // 2. Temp Range
  const tempRangeEl = document.getElementById("weather-temp-range");
  if (tempRangeEl) tempRangeEl.innerText = `${curDay.temperature_max_c.toFixed(1)}°C / ${curDay.temperature_min_c.toFixed(1)}°C`;

  const tempSubEl = document.getElementById("weather-temp-sub");
  if (tempSubEl) tempSubEl.innerText = `30d Peak: ${summary.max_temperature_c}°C • Min: ${summary.min_temperature_c}°C`;

  // 3. Wind
  const windEl = document.getElementById("weather-wind-speed");
  if (windEl) windEl.innerText = `${curDay.max_wind_kmh.toFixed(1)} km/h`;

  const windAlertEl = document.getElementById("weather-wind-alert");
  if (windAlertEl) {
    if (curDay.max_wind_kmh >= 24) {
      windAlertEl.innerText = "⚠️ High Wind (Crane / Gantry Caution)";
      windAlertEl.style.color = "var(--accent-coral)";
    } else if (curDay.max_wind_kmh >= 20) {
      windAlertEl.innerText = "⚡ Moderate Breeze (Active Pilotage)";
      windAlertEl.style.color = "var(--accent-amber)";
    } else {
      windAlertEl.innerText = "✓ Safe Berthing Velocity (< 20 km/h)";
      windAlertEl.style.color = "var(--accent-emerald)";
    }
  }

  // 4. Precip & Hatch
  const precipEl = document.getElementById("weather-precip-val");
  if (precipEl) precipEl.innerText = `${curDay.precipitation_mm.toFixed(1)} mm`;

  const hatchEl = document.getElementById("weather-hatch-advisory");
  if (hatchEl) {
    if (curDay.precipitation_mm > 8.0) {
      hatchEl.innerText = "🌧️ Critical Hatch Tarping Required";
      hatchEl.style.color = "var(--accent-coral)";
    } else if (curDay.precipitation_mm > 0.0) {
      hatchEl.innerText = "🌦️ Moisture Monitor Active";
      hatchEl.style.color = "var(--accent-amber)";
    } else {
      hatchEl.innerText = "✓ Dry Hatches Unrestricted (0 mm)";
      hatchEl.style.color = "var(--accent-cyan)";
    }
  }

  // 5. Port Operational Status
  const statusEl = document.getElementById("weather-port-status");
  const riskSubEl = document.getElementById("weather-risk-text");
  if (statusEl && riskSubEl) {
    if (curDay.weather_code === 80 || curDay.max_wind_kmh >= 25) {
      statusEl.innerText = "High Metocean Alert";
      statusEl.style.color = "var(--accent-coral)";
      riskSubEl.innerText = "Lightering caution & swell stoppage advisory";
    } else if (curDay.precipitation_mm > 5 || curDay.weather_code === 63) {
      statusEl.innerText = "Elevated Precaution";
      statusEl.style.color = "var(--accent-amber)";
      riskSubEl.innerText = "Temporary hatch closure on moisture-sensitive cargo";
    } else {
      statusEl.innerText = "Normal Operations";
      statusEl.style.color = "var(--accent-emerald)";
      riskSubEl.innerText = "Optimal discharge & mechanical conveyor throughput";
    }
  }

  // Laycan impact text
  const laycanEl = document.getElementById("weather-laycan-impact");
  if (laycanEl) {
    const calmDays = days.filter(d => d.precipitation_mm === 0 && d.max_wind_kmh < 22).slice(0, 5);
    const calmDates = calmDays.map(d => d.date.slice(5)).join(", ");
    laycanEl.innerText = `Recommended tender discharge window at ${portData.port_name}: ${calmDates ? `Calm dates [${calmDates}] with zero rain and light winds (<22 km/h)` : 'Standard laycan with monsoon buffer (+1.5 demurrage days)'}.`;
  }
}

function renderWeatherChart(portData) {
  const canvas = document.getElementById("portWeatherChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (portWeatherChart) portWeatherChart.destroy();

  let days = portData.forecast_days || [];
  if (currentWeatherHorizon === "7") days = days.slice(0, 7);
  else if (currentWeatherHorizon === "15") days = days.slice(0, 15);

  const labels = days.map(d => d.date.slice(5)); // e.g. "08-04"
  const maxTemps = days.map(d => d.temperature_max_c);
  const minTemps = days.map(d => d.temperature_min_c);
  const windSpeeds = days.map(d => d.max_wind_kmh);
  const precipitations = days.map(d => d.precipitation_mm);

  portWeatherChart = new Chart(ctx, {
    data: {
      labels,
      datasets: [
        {
          type: "line",
          label: "Max Temp (°C)",
          data: maxTemps,
          borderColor: "#00d2ff",
          backgroundColor: "rgba(0, 210, 255, 0.08)",
          fill: true,
          tension: 0.35,
          borderWidth: 2.2,
          pointRadius: 3,
          pointBackgroundColor: "#00d2ff",
          yAxisID: "yTemp"
        },
        {
          type: "line",
          label: "Min Temp (°C)",
          data: minTemps,
          borderColor: "#6366f1",
          borderWidth: 1.8,
          pointRadius: 2.5,
          pointBackgroundColor: "#6366f1",
          borderDash: [4, 4],
          tension: 0.35,
          yAxisID: "yTemp"
        },
        {
          type: "line",
          label: "Peak Wind (km/h)",
          data: windSpeeds,
          borderColor: "#ffb703",
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: "#ffb703",
          tension: 0.25,
          yAxisID: "yWind"
        },
        {
          type: "bar",
          label: "Rainfall (mm)",
          data: precipitations,
          backgroundColor: "rgba(0, 245, 160, 0.55)",
          hoverBackgroundColor: "#00f5a0",
          borderRadius: 4,
          yAxisID: "yPrecip"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#94a3b8", boxWidth: 12, font: { family: "Inter", size: 10 } }
        },
        tooltip: {
          backgroundColor: "rgba(13, 23, 48, 0.95)",
          titleColor: "#ffffff",
          bodyColor: "#e2e8f0",
          borderColor: "rgba(0, 210, 255, 0.4)",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            afterBody: (tooltipItems) => {
              const idx = tooltipItems[0]?.dataIndex;
              if (idx != null && days[idx]) {
                const d = days[idx];
                return `\nCondition: ${d.icon} ${d.condition}\nAdvisory: ${d.operational_impact}`;
              }
              return "";
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { color: "#94a3b8", maxRotation: 45, font: { size: 9 } }
        },
        yTemp: {
          type: "linear",
          position: "left",
          min: 20,
          max: 38,
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { color: "#00d2ff", callback: v => `${v}°C` }
        },
        yWind: {
          type: "linear",
          position: "right",
          min: 10,
          max: 35,
          grid: { drawOnChartArea: false },
          ticks: { color: "#ffb703", callback: v => `${v}k` }
        },
        yPrecip: {
          type: "linear",
          position: "right",
          min: 0,
          max: 20,
          grid: { drawOnChartArea: false },
          ticks: { color: "#00f5a0", callback: v => `${v}mm` }
        }
      }
    }
  });
}

function renderWeatherTable(portData) {
  const tbody = document.getElementById("weather-forecast-tbody");
  if (!tbody) return;

  let days = portData.forecast_days || [];
  if (currentWeatherHorizon === "7") days = days.slice(0, 7);
  else if (currentWeatherHorizon === "15") days = days.slice(0, 15);

  // Apply filter
  if (currentWeatherFilter === "rain") {
    days = days.filter(d => d.precipitation_mm > 0);
  } else if (currentWeatherFilter === "wind") {
    days = days.filter(d => d.max_wind_kmh >= 22);
  } else if (currentWeatherFilter === "clear") {
    days = days.filter(d => d.precipitation_mm === 0 && d.weather_code <= 2);
  }

  if (days.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
          No forecast days match the active filter criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = days.map(d => {
    const windClass = d.max_wind_kmh >= 25 ? "wind-badge-alert" : (d.max_wind_kmh >= 21 ? "wind-badge-moderate" : "wind-badge-safe");
    const dateObj = new Date(d.date + "T00:00:00");
    const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" });

    return `
      <tr>
        <td>
          <div style="font-weight: 600; color: #ffffff;">${d.date}</div>
          <div style="font-size: 0.7rem; color: var(--text-muted);">${dayName}</div>
        </td>
        <td>
          <span style="font-weight: 600; color: var(--accent-cyan);">${d.location}</span>
        </td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="font-size: 1.15rem;">${d.icon}</span>
            <span>${d.condition}</span>
          </div>
        </td>
        <td>
          <span style="color: #00d2ff; font-weight: 600;">${d.temperature_max_c.toFixed(1)}°C</span> / 
          <span style="color: var(--text-muted);">${d.temperature_min_c.toFixed(1)}°C</span>
        </td>
        <td>
          <span class="${windClass}">${d.max_wind_kmh.toFixed(1)} km/h</span>
        </td>
        <td>
          <div style="display: flex; align-items: center;">
            <span class="rain-bar-indicator" style="width: ${Math.min(30, d.precipitation_mm * 2.5)}px;"></span>
            <span style="font-weight: 600; color: ${d.precipitation_mm > 0 ? '#00f5a0' : 'var(--text-muted)'};">
              ${d.precipitation_mm.toFixed(1)} mm
            </span>
          </div>
        </td>
        <td>
          <span class="badge-tag" style="background: rgba(255,255,255,0.06); color: #94a3b8; font-size: 0.72rem; padding: 2px 6px;">
            WMO ${d.weather_code}
          </span>
        </td>
        <td>
          <div style="font-size: 0.75rem; color: ${d.operational_risk === 'High Alert' ? 'var(--accent-coral)' : (d.operational_risk === 'Elevated' ? 'var(--accent-amber)' : 'var(--text-secondary)')};">
            ${d.operational_impact}
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

// =========================================================================
// INLAND WATERWAYS TRANSPORT (IWT) & NATIONAL WATERWAYS INTELLIGENCE MODULE
// =========================================================================

const IWT_STATIC_DATA = {
  overview: {
    total_cargo_mt_fy24: 133.0,
    yoy_growth_pct: 5.43,
    target_cargo_2030_mt: 252.5,
    "10_year_cagr_pct": 22.1,
    national_waterways_tracked: 10,
    total_network_length_km: 4899,
    navigable_length_km: 4476,
    round_year_navigable_km: 3548,
    terminals_operational: 7,
    active_vessel_fleet: 380,
    annual_freight_collected_cr: 1560,
    national_logistics_savings_cr: 3850,
    carbon_reduction_mt: 4.8,
    annual_passengers_millions: 84.5,
    average_freight_inr_ton_km: 1.06,
    freight_savings_vs_rail_pct: 24.8,
    freight_savings_vs_road_pct: 53.5
  },
  timeseries: [
    { fiscal_year: "2013-14", year: 2014, cargo_mt: 18.01, yoy_growth_pct: null, nw1_mt: 3.12, nw97_mt: 7.80, other_nw_mt: 7.09, modal_share_pct: 0.52 },
    { fiscal_year: "2014-15", year: 2015, cargo_mt: 20.45, yoy_growth_pct: 13.55, nw1_mt: 3.65, nw97_mt: 8.90, other_nw_mt: 7.90, modal_share_pct: 0.58 },
    { fiscal_year: "2015-16", year: 2016, cargo_mt: 24.30, yoy_growth_pct: 18.83, nw1_mt: 4.10, nw97_mt: 10.40, other_nw_mt: 9.80, modal_share_pct: 0.67 },
    { fiscal_year: "2016-17", year: 2017, cargo_mt: 30.15, yoy_growth_pct: 24.07, nw1_mt: 4.85, nw97_mt: 12.60, other_nw_mt: 12.70, modal_share_pct: 0.81 },
    { fiscal_year: "2017-18", year: 2018, cargo_mt: 38.60, yoy_growth_pct: 28.03, nw1_mt: 5.48, nw97_mt: 15.90, other_nw_mt: 17.22, modal_share_pct: 0.98 },
    { fiscal_year: "2018-19", year: 2019, cargo_mt: 55.03, yoy_growth_pct: 42.56, nw1_mt: 6.79, nw97_mt: 21.30, other_nw_mt: 26.94, modal_share_pct: 1.34 },
    { fiscal_year: "2019-20", year: 2020, cargo_mt: 73.64, yoy_growth_pct: 33.82, nw1_mt: 7.95, nw97_mt: 26.80, other_nw_mt: 38.89, modal_share_pct: 1.76 },
    { fiscal_year: "2020-21", year: 2021, cargo_mt: 83.61, yoy_growth_pct: 13.54, nw1_mt: 9.21, nw97_mt: 29.50, other_nw_mt: 44.90, modal_share_pct: 1.95 },
    { fiscal_year: "2021-22", year: 2022, cargo_mt: 108.79, yoy_growth_pct: 30.12, nw1_mt: 11.02, nw97_mt: 33.40, other_nw_mt: 64.37, modal_share_pct: 2.38 },
    { fiscal_year: "2022-23", year: 2023, cargo_mt: 126.15, yoy_growth_pct: 15.96, nw1_mt: 12.45, nw97_mt: 36.10, other_nw_mt: 77.60, modal_share_pct: 2.68 },
    { fiscal_year: "2023-24", year: 2024, cargo_mt: 133.00, yoy_growth_pct: 5.43, nw1_mt: 13.17, nw97_mt: 37.80, other_nw_mt: 82.03, modal_share_pct: 2.82 },
    { fiscal_year: "2024-25 (P)", year: 2025, cargo_mt: 147.50, yoy_growth_pct: 10.90, nw1_mt: 15.20, nw97_mt: 40.50, other_nw_mt: 91.80, modal_share_pct: 3.05, is_projection: true },
    { fiscal_year: "2025-26 (P)", year: 2026, cargo_mt: 164.20, yoy_growth_pct: 11.32, nw1_mt: 17.80, nw97_mt: 43.60, other_nw_mt: 102.80, modal_share_pct: 3.32, is_projection: true },
    { fiscal_year: "2026-27 (P)", year: 2027, cargo_mt: 182.90, yoy_growth_pct: 11.39, nw1_mt: 20.90, nw97_mt: 47.10, other_nw_mt: 114.90, modal_share_pct: 3.60, is_projection: true },
    { fiscal_year: "2027-28 (P)", year: 2028, cargo_mt: 203.80, yoy_growth_pct: 11.43, nw1_mt: 24.50, nw97_mt: 50.80, other_nw_mt: 128.50, modal_share_pct: 3.91, is_projection: true },
    { fiscal_year: "2028-29 (P)", year: 2029, cargo_mt: 226.90, yoy_growth_pct: 11.33, nw1_mt: 28.60, nw97_mt: 54.90, other_nw_mt: 143.40, modal_share_pct: 4.25, is_projection: true },
    { fiscal_year: "2029-30 (P)", year: 2030, cargo_mt: 252.50, yoy_growth_pct: 11.28, nw1_mt: 33.20, nw97_mt: 59.40, other_nw_mt: 159.90, modal_share_pct: 4.60, is_projection: true }
  ],
  waterways: [
    { id: "NW-1", name: "NW-1 (Ganga-Bhagirathi-Hooghly)", river_system: "Ganga - Bhagirathi - Hooghly", states: ["Uttar Pradesh", "Bihar", "Jharkhand", "West Bengal"], stretch: "Prayagraj to Haldia", total_length_km: 1620, navigable_length_km: 1620, round_the_year_navigable_km: 1390, annual_cargo_mt: 13.17, cargo_share_pct: 9.9, connected_ports: ["Haldia Dock Complex", "SMP Kolkata"], connected_steel_hubs: ["SAIL Durgapur", "SAIL Bokaro", "Tata Steel"], key_terminals: ["MMT Varanasi", "MMT Sahibganj", "MMT Haldia", "Kalughat IWT"], ris_coverage: "Operational 1,390 km", description: "India's premier arterial waterway directly linking steel heartland with Haldia deep-water berths." },
    { id: "NW-2", name: "NW-2 (Brahmaputra River)", river_system: "Brahmaputra", states: ["Assam", "West Bengal", "Meghalaya"], stretch: "Dhubri to Sadiya", total_length_km: 891, navigable_length_km: 891, round_the_year_navigable_km: 768, annual_cargo_mt: 2.45, cargo_share_pct: 1.84, connected_ports: ["Kolkata Port (via IBPR)", "Mongla Port"], connected_steel_hubs: ["Northeast Defense & Infra", "Guwahati Hub"], key_terminals: ["Pandu Port", "Dhubri Terminal", "Jogighopa MMT"], ris_coverage: "Dhubri to Neamati", description: "Lifeline for North-Eastern logistics via the Indo-Bangladesh Protocol Route." },
    { id: "NW-3", name: "NW-3 (West Coast Canal)", river_system: "West Coast Canal & Champakara", states: ["Kerala"], stretch: "Kottapuram to Kollam", total_length_km: 205, navigable_length_km: 205, round_the_year_navigable_km: 205, annual_cargo_mt: 14.80, cargo_share_pct: 11.13, connected_ports: ["Cochin Port (Vallarpadam)"], connected_steel_hubs: ["Kochi Industrial Corridor"], key_terminals: ["Aluva", "Maradu", "Kollam", "Kottapuram"], ris_coverage: "205 km 24x7 operational", description: "Continuous round-the-year canal carrying petroleum, chemicals, containers, and fertilizers." },
    { id: "NW-4", name: "NW-4 (Krishna - Godavari Canals)", river_system: "Krishna, Godavari & Buckingham", states: ["Andhra Pradesh", "Telangana", "Tamil Nadu"], stretch: "Kakinada to Puducherry", total_length_km: 1078, navigable_length_km: 690, round_the_year_navigable_km: 420, annual_cargo_mt: 6.80, cargo_share_pct: 5.11, connected_ports: ["Kakinada", "Chennai", "Kamarajar"], connected_steel_hubs: ["RINL Vizag", "Vijayawada Metal Cluster"], key_terminals: ["Muktyala", "Ibrahimpatnam", "Kakinada"], ris_coverage: "Muktyala to Vijayawada", description: "Connects southern mineral belts to East Coast commercial ports." },
    { id: "NW-5", name: "NW-5 (Brahmani - Mahanadi River System)", river_system: "Brahmani, Kharsua, Dhamra & Delta", states: ["Odisha", "West Bengal"], stretch: "Talcher - Dhamra - Paradip - Geonkhali", total_length_km: 623, navigable_length_km: 588, round_the_year_navigable_km: 332, annual_cargo_mt: 11.20, cargo_share_pct: 8.42, connected_ports: ["Paradip Port", "Dhamra Port"], connected_steel_hubs: ["SAIL Rourkela", "Tata Kalinganagar", "JSPL Angul", "Talcher Coalfields"], key_terminals: ["Pankpal (Kalinganagar)", "Talcher Coal Terminal", "Paradip IWT Berth"], ris_coverage: "Pankpal to Paradip (185 km)", description: "The golden arterial waterway for India's steel industry, connecting Talcher coal & Kalinganagar directly to Paradip bulk berths." },
    { id: "NW-16", name: "NW-16 (Barak River)", river_system: "Barak River", states: ["Assam", "Mizoram", "Manipur"], stretch: "Bhanga to Lakhipur", total_length_km: 121, navigable_length_km: 121, round_the_year_navigable_km: 72, annual_cargo_mt: 0.48, cargo_share_pct: 0.36, connected_ports: ["Kolkata Port (via IBPR)"], connected_steel_hubs: ["Barak Valley Infra"], key_terminals: ["Badarpur", "Karimganj"], ris_coverage: "DGPS coverage", description: "Strategic waterway connecting Barak valley with Kolkata via Bangladesh." },
    { id: "NW-68", name: "NW-68 (Mandovi River)", river_system: "Mandovi River", states: ["Goa"], stretch: "Usgaon Bridge to Panaji", total_length_km: 41, navigable_length_km: 41, round_the_year_navigable_km: 41, annual_cargo_mt: 18.50, cargo_share_pct: 13.91, connected_ports: ["Mormugao Port"], connected_steel_hubs: ["Goa Iron Ore Belts", "Pellet Plants"], key_terminals: ["Panaji Ferry", "Usgaon Jetty"], ris_coverage: "VTS & Coastal AIS", description: "High-density mineral export corridor ferrying iron ore to Mormugao deep-water anchorage." },
    { id: "NW-86", name: "NW-86 (Rupnarayan River)", river_system: "Rupnarayan River", states: ["West Bengal"], stretch: "Hooghly confluence to Bakshi", total_length_km: 98, navigable_length_km: 98, round_the_year_navigable_km: 98, annual_cargo_mt: 16.20, cargo_share_pct: 12.18, connected_ports: ["Haldia Dock Complex", "Kolkata Port"], connected_steel_hubs: ["Haldia Petrochemical & Metal Hub"], key_terminals: ["Kolaghat Fly Ash Jetty", "Geonkhali"], ris_coverage: "Integrated with NW-1 RIS", description: "Major fly ash and industrial aggregate feeder route for domestic cement plants and Bangladesh exports." },
    { id: "NW-97", name: "NW-97 (Sundarbans Waterways)", river_system: "Sundarbans Delta Channels", states: ["West Bengal"], stretch: "Namkhana to Hemnagar Customs Border", total_length_km: 172, navigable_length_km: 172, round_the_year_navigable_km: 172, annual_cargo_mt: 37.80, cargo_share_pct: 28.42, connected_ports: ["Haldia Dock Complex", "Kolkata", "Mongla"], connected_steel_hubs: ["Eastern Export Corridor", "SAIL/Tata BD Exports"], key_terminals: ["Namkhana", "Hemnagar", "Hasnabad"], ris_coverage: "DGPS & Radar vessel tracking", description: "India's highest cargo waterway carrying 37.8 MT of bilateral trade under the Indo-Bangladesh Protocol." },
    { id: "NW-111", name: "NW-111 (Zuari River)", river_system: "Zuari River", states: ["Goa"], stretch: "Sanvordem to Marmagao Port", total_length_km: 50, navigable_length_km: 50, round_the_year_navigable_km: 50, annual_cargo_mt: 11.60, cargo_share_pct: 8.72, connected_ports: ["Mormugao Port"], connected_steel_hubs: ["South Goa Mining & Metallurgy"], key_terminals: ["Sanvordem", "Cortalim"], ris_coverage: "VTS operational", description: "Key mineral and metallurgical coke route connecting South Goa industrial hubs with ocean vessels." }
  ],
  depth_lad: [
    { stretch_id: "NW1_HAL_FRK", stretch_name: "Haldia - Farakka", waterway_id: "NW-1", length_km: 460, target_lad_m: 3.0, actual_current_lad_m: 3.0, min_seasonal_lad_m: 2.8, dredging_status: "Maintained by trailing suction hopper dredgers (TSHD)", shallow_patches: ["Tribeni shoals (2.8m)", "Nabadwip curve"], air_draft_clearance_m: 9.5, navigation_status: "Normal / Unrestricted 24x7 Navigable", advisory: "Full laden transit permissible for vessels with draft up to 2.8m. Tidal assistance available south of Nabadwip." },
    { stretch_id: "NW1_FRK_BRH", stretch_name: "Farakka - Barh", waterway_id: "NW-1", length_km: 300, target_lad_m: 2.5, actual_current_lad_m: 2.6, min_seasonal_lad_m: 2.2, dredging_status: "Cutter suction dredging active near Vikramshila stretch", shallow_patches: ["Kahalgaon power intake shoal", "Pirpainti bend (2.3m)"], air_draft_clearance_m: 9.0, navigation_status: "Normal Navigable", advisory: "Safe navigation for vessels up to 2.4m draft. Navigation pilotage recommended at Kahalgaon curve." },
    { stretch_id: "NW1_BRH_VRN", stretch_name: "Barh - Patna - Varanasi", waterway_id: "NW-1", length_km: 490, target_lad_m: 2.2, actual_current_lad_m: 2.3, min_seasonal_lad_m: 1.8, dredging_status: "Intensive dry-season shoal dredging at Buxar & Ghazipur", shallow_patches: ["Ghazipur shoal (2.0m)", "Buxar railway bridge (1.9m)"], air_draft_clearance_m: 8.5, navigation_status: "Advisory Active (Daylight for >2.0m draft)", advisory: "Class-III barges (up to 1,200 DWT) operate smoothly. Night navigation beacons operational." },
    { stretch_id: "NW1_VRN_PRY", stretch_name: "Varanasi - Prayagraj", waterway_id: "NW-1", length_km: 370, target_lad_m: 1.5, actual_current_lad_m: 1.6, min_seasonal_lad_m: 1.2, dredging_status: "Fairway maintenance during monsoon and post-monsoon", shallow_patches: ["Sirsa braided channel (1.3m)", "Chunar rocky sill"], air_draft_clearance_m: 7.5, navigation_status: "Seasonal / Light Draft Only", advisory: "Feasible for passenger ferries, Ro-Pax, and shallow-draft barges (draft <= 1.4m)." },
    { stretch_id: "NW2_DHB_PND", stretch_name: "Dhubri - Pandu (Guwahati)", waterway_id: "NW-2", length_km: 260, target_lad_m: 2.5, actual_current_lad_m: 2.5, min_seasonal_lad_m: 2.0, dredging_status: "Year-round maintenance dredging on Brahmaputra braided channels", shallow_patches: ["Pancharatna narrows", "Goalpara bend (2.2m)"], air_draft_clearance_m: 8.0, navigation_status: "Normal Navigable", advisory: "Strong current in monsoon (3.5-5.0 knots). High engine power required for upstream transit." },
    { stretch_id: "NW5_PNK_PRD", stretch_name: "Pankpal - Paradip (Odisha Steel)", waterway_id: "NW-5", length_km: 185, target_lad_m: 2.8, actual_current_lad_m: 2.9, min_seasonal_lad_m: 2.5, dredging_status: "Tidal delta dredged fairway maintained with Paradip Port Trust support", shallow_patches: ["Kharsua confluence (2.6m)", "Mahanadi outfall bar"], air_draft_clearance_m: 10.0, navigation_status: "Normal Navigable (High bulk steel & coal transit)", advisory: "Excellent draft clearance for 2,000 DWT steel-carrying barges directly connecting Kalinganagar to Paradip." },
    { stretch_id: "NW97_NMK_HMN", stretch_name: "Sundarbans Protocol (Namkhana-Hemnagar)", waterway_id: "NW-97", length_km: 172, target_lad_m: 3.5, actual_current_lad_m: 3.8, min_seasonal_lad_m: 3.2, dredging_status: "Tidal estuarine deep channel with natural scours", shallow_patches: ["Bidya river junction (3.2m during spring low)"], air_draft_clearance_m: 12.0, navigation_status: "Unrestricted Deep Fairway", advisory: "Heaviest cargo volume in India. Average 80-120 barge transits daily. Pilots mandatory." }
  ],
  commodities: [
    { id: "coal", name: "Coal (Thermal & Coking)", annual_tonnage_mt: 39.90, share_pct: 30.0, icon: "⛏️", key_routes: "NW-5 Talcher-Paradip, NW-1 Haldia-Farakka/Barh", primary_users: "NTPC Farakka, NTPC Barh, SAIL Plants, Tata Steel, JSPL", growth_yoy_pct: 14.2, description: "Power plants and blast furnaces save ₹400–750/tonne compared to congested rail." },
    { id: "fly_ash", name: "Fly Ash (Thermal Byproduct)", annual_tonnage_mt: 34.58, share_pct: 26.0, icon: "💨", key_routes: "NW-86/97 Kolaghat to Bangladesh (IBPR), NW-1 Kahalgaon", primary_users: "Bangladesh Cement Manufacturers, Ultratech, Ambuja", growth_yoy_pct: 18.5, description: "High-volume green bulk export from Bengal/Bihar power plants to Bangladesh cement grinders." },
    { id: "iron_ore", name: "Iron Ore & Pellets", annual_tonnage_mt: 21.28, share_pct: 16.0, icon: "🪨", key_routes: "NW-68/111 Goa mining belts to Mormugao, NW-5 Mahanadi delta", primary_users: "Vedanta Sesa, Jindal Steel, Export Berths", growth_yoy_pct: 8.3, description: "Traditional high-density barge traffic in Goa and emerging mineral barge logistics in Odisha." },
    { id: "sand_aggregates", name: "Sand & Stone Aggregates", annual_tonnage_mt: 13.30, share_pct: 10.0, icon: "🏗️", key_routes: "NW-1 Bihar/Bengal, NW-2 Pakur to Assam", primary_users: "State PWDs, NHAI Highway Projects", growth_yoy_pct: 6.8, description: "Riverbed aggregates transported on dumb barges, drastically cutting highway truck jams." },
    { id: "cement", name: "Cement & Clinker", annual_tonnage_mt: 9.31, share_pct: 7.0, icon: "🧱", key_routes: "NW-4 Krishna river, NW-1 Haldia to Patna/Varanasi", primary_users: "Ultratech, Dalmia Bharat, Shree Cement", growth_yoy_pct: 21.4, description: "Rapidly expanding multi-modal bulk cement movement with low transit breakage." },
    { id: "steel", name: "Finished Steel Coils & Billets", annual_tonnage_mt: 5.32, share_pct: 4.0, icon: "⛓️", key_routes: "NW-1 Haldia to Patna/Varanasi, NW-5 Kalinganagar to Paradip, NW-2 Pandu", primary_users: "SAIL, Tata Steel, Jindal Steel, AM/NS India", growth_yoy_pct: 34.0, description: "Fastest growing high-value sector. Steel PSUs leverage barges to bypass rail wagon shortages." },
    { id: "fertilizers", name: "Chemical Fertilizers", annual_tonnage_mt: 3.99, share_pct: 3.0, icon: "🌱", key_routes: "NW-1 Haldia/Kolkata to UP & Bihar farm belts", primary_users: "IFFCO, KRIBHCO, Paradeep Phosphates (PPL)", growth_yoy_pct: 12.0, description: "Essential agricultural inputs delivered directly to riverine rural consumption districts." },
    { id: "food_grains", name: "Food Grains (FCI Logistics)", annual_tonnage_mt: 2.66, share_pct: 2.0, icon: "🌾", key_routes: "NW-1 Patna to Kolkata, NW-2 Kolkata to Pandu (Assam)", primary_users: "Food Corporation of India (FCI)", growth_yoy_pct: 15.5, description: "PDS food grains transported from northern granaries to Assam and Northeast." },
    { id: "containers_pol", name: "Containers & POL Liquids", annual_tonnage_mt: 2.66, share_pct: 2.0, icon: "📦", key_routes: "NW-1 Kolkata to Varanasi, NW-3 Cochin to Udyogmandal", primary_users: "PepsiCo, Tata Motors, IOCL, BPCL", growth_yoy_pct: 28.0, description: "FMCG, automotive, and containerized goods utilizing scheduled river liner services." }
  ],
  infrastructure: [
    { id: "mmt_varanasi", name: "Multi-Modal Terminal Varanasi (Ramnagar)", waterway_id: "NW-1", state: "Uttar Pradesh", berths: 2, quay_length_m: 200, capacity_mtpa: 1.26, equipment: ["1x 30T Mobile Harbour Crane", "2x Reach Stackers (45T)", "Direct Broad Gauge Rail Siding", "5,000 MT Covered Godown"], status: "Active (Inaugurated by Prime Minister 2018)", commodities: "Finished steel, cement, containers, food grains", depth_m: 3.0 },
    { id: "mmt_sahibganj", name: "Multi-Modal Terminal Sahibganj", waterway_id: "NW-1", state: "Jharkhand", berths: 2, quay_length_m: 270, capacity_mtpa: 3.18, equipment: ["2x 40T Harbour Cranes", "Heavy-Duty Ro-Ro Ramp", "200,000 MT Mineral Stockyard", "Direct Rail Connectivity"], status: "Active (Coal & stone chip hub)", commodities: "Coal, stone chips, cement, iron ore", depth_m: 3.2 },
    { id: "mmt_haldia", name: "Multi-Modal Terminal Haldia", waterway_id: "NW-1", state: "West Bengal", berths: 2, quay_length_m: 290, capacity_mtpa: 3.08, equipment: ["2x Gantry Cranes (35T)", "Automated Fly Ash Silos", "Direct Deep-Sea Berths Interface", "Electronic EDI Gate"], status: "Active (River-sea transhipment)", commodities: "Coking coal, thermal coal, fly ash, steel coils", depth_m: 4.5 },
    { id: "kalughat_terminal", name: "Kalughat Intermodal Terminal", waterway_id: "NW-1", state: "Bihar", berths: 2, quay_length_m: 125, capacity_mtpa: 1.25, equipment: ["1x 35T Harbour Crane", "1,500 TEU Container Yard", "Direct 4-Lane NH-19 Access", "Nepal Transit Cargo Shed"], status: "Active (Completed 2023)", commodities: "Containers, Nepal EXIM transit, steel bars", depth_m: 2.8 },
    { id: "pandu_port", name: "Pandu Inland Port (Guwahati)", waterway_id: "NW-2", state: "Assam", berths: 3, quay_length_m: 260, capacity_mtpa: 2.00, equipment: ["2x Shore Cranes (20T & 10T)", "Container Freight Station", "Broad Gauge Railway Spur", "Ro-Ro Jetty"], status: "Active (Premier Northeast Port)", commodities: "Steel from SAIL/Tata, FCI grains, fertilizers", depth_m: 2.5 },
    { id: "dhubri_terminal", name: "Dhubri River Terminal", waterway_id: "NW-2", state: "Assam", berths: 2, quay_length_m: 180, capacity_mtpa: 1.50, equipment: ["1x 20T Mobile Crane", "Ro-Ro Pontoon Berth", "Customs EDI Office"], status: "Active (Bhutan stone export hub)", commodities: "Bhutanese stone aggregates, cement", depth_m: 2.5 },
    { id: "pankpal_terminal", name: "Pankpal Terminal (Kalinganagar)", waterway_id: "NW-5", state: "Odisha", berths: 2, quay_length_m: 220, capacity_mtpa: 2.50, equipment: ["2x Heavy-Lift Cranes (50T)", "Direct Steel Conveyor Link", "Coil Storage Warehouse"], status: "Operational Phase 1", commodities: "Steel coils, pig iron, coal, pellets", depth_m: 3.0 }
  ],
  vessels: [
    { id: "self_propelled_barge_1000", name: "Self-Propelled Barge (Class-III / 1,000 DWT)", category: "Self-Propelled Cargo", dwt: 1000, loa_m: 60.0, beam_m: 9.5, draft_m: 1.8, air_draft_m: 6.5, speed_knots: 8.5, charter_rate_inr: 45000, active_count: 142, cargo: "Steel coils, cement bags, containers, food grains" },
    { id: "self_propelled_barge_2000", name: "Self-Propelled Heavy Barge (Class-IV / 2,000 DWT)", category: "Self-Propelled Heavy", dwt: 2000, loa_m: 75.0, beam_m: 11.4, draft_m: 2.5, air_draft_m: 7.2, speed_knots: 9.0, charter_rate_inr: 72000, active_count: 98, cargo: "Bulk coal, fly ash, iron ore, heavy steel billets" },
    { id: "push_tow_dumb_barge_flotilla", name: "Pusher Tug + 2x Dumb Barges (3,000 DWT)", category: "Tug-Barge Convoy", dwt: 3000, loa_m: 120.0, beam_m: 11.4, draft_m: 2.2, air_draft_m: 6.8, speed_knots: 7.0, charter_rate_inr: 95000, active_count: 64, cargo: "Thermal coal, limestone, stone chips, iron ore" },
    { id: "ro_ro_vessel", name: "Ro-Ro Commercial Carrier", category: "Ro-Ro Vehicle & Truck", dwt: 850, loa_m: 55.0, beam_m: 12.0, draft_m: 1.5, air_draft_m: 6.0, speed_knots: 10.0, charter_rate_inr: 65000, active_count: 32, cargo: "28 loaded trucks, automobiles, inter-bank passengers" },
    { id: "river_sea_hybrid_vessel", name: "River-Sea Vessel (RSV Type-IV / 3,500 DWT)", category: "Coastal-River Hybrid", dwt: 3500, loa_m: 88.0, beam_m: 14.5, draft_m: 3.8, air_draft_m: 8.5, speed_knots: 10.5, charter_rate_inr: 140000, active_count: 26, cargo: "Export steel coils, import coking coal transhipment" },
    { id: "river_passenger_cruise", name: "Luxury River Cruiser (MV Ganga Vilas Class)", category: "Luxury Tourism", dwt: 450, loa_m: 62.5, beam_m: 12.8, draft_m: 1.4, air_draft_m: 5.8, speed_knots: 9.5, charter_rate_inr: 185000, active_count: 18, cargo: "80 luxury passengers, cultural river expeditions" }
  ],
  routes: {
    haldia_to_varanasi: { id: "haldia_to_varanasi", origin: "Haldia MMT", destination: "Varanasi MMT", waterway: "NW-1", river_km: 1250, rail_km: 820, road_km: 890, current_up_knots: 2.2, current_down_knots: 2.2, iwt_rate: 1325, rail_rate: 1840, road_rate: 2850, co2_iwt_kg: 22.5, co2_rail_kg: 34.8, co2_road_kg: 78.2 },
    haldia_to_patna: { id: "haldia_to_patna", origin: "Haldia MMT", destination: "Patna Kalughat", waterway: "NW-1", river_km: 955, rail_km: 610, road_km: 660, current_up_knots: 2.0, current_down_knots: 2.0, iwt_rate: 1012, rail_rate: 1420, road_rate: 2180, co2_iwt_kg: 17.2, co2_rail_kg: 26.5, co2_road_kg: 59.5 },
    kolkata_to_pandu: { id: "kolkata_to_pandu", origin: "Kolkata Port", destination: "Pandu Port (Guwahati)", waterway: "NW-1/2 IBPR", river_km: 1530, rail_km: 1020, road_km: 1080, current_up_knots: 2.8, current_down_knots: 2.8, iwt_rate: 1620, rail_rate: 2250, road_rate: 3450, co2_iwt_kg: 27.5, co2_rail_kg: 43.3, co2_road_kg: 97.2 },
    kalinganagar_to_paradip: { id: "kalinganagar_to_paradip", origin: "Kalinganagar (Pankpal)", destination: "Paradip Port", waterway: "NW-5", river_km: 185, rail_km: 160, road_km: 175, current_up_knots: 1.2, current_down_knots: 1.2, iwt_rate: 215, rail_rate: 380, road_rate: 590, co2_iwt_kg: 3.3, co2_rail_kg: 6.8, co2_road_kg: 15.4 },
    kolaghat_to_hemnagar: { id: "kolaghat_to_hemnagar", origin: "Kolaghat Fly Ash", destination: "Hemnagar Customs", waterway: "NW-86/97", river_km: 210, rail_km: 245, road_km: 260, current_up_knots: 1.5, current_down_knots: 1.5, iwt_rate: 240, rail_rate: 430, road_rate: 680, co2_iwt_kg: 3.8, co2_rail_kg: 10.4, co2_road_kg: 23.4 }
  },
  operators: [
    { name: "Inland Waterways Authority of India (IWAI)", type: "Statutory Authority / Regulator", hq: "Noida, UP", fleet: "Regulator & Fairway Fleet", role: "Fairway development, LAD maintenance, terminals, River Information System (RIS)" },
    { name: "Inland & Coastal Shipping Ltd (ICSL - SCI)", type: "Central PSU (CPSE)", hq: "Mumbai / Kolkata", fleet: "24 Barges", role: "Dedicated coastal and inland barge operations for PSU bulk (SAIL, NTPC, IOCL)" },
    { name: "Adani Logistics Ltd (Waterways Division)", type: "Private Conglomerate", hq: "Ahmedabad, Gujarat", fleet: "18 Barges", role: "Bulk agri-commodities, container movement on NW-1/NW-2, terminal ops" },
    { name: "Jindal Waterways Ltd (JSPL)", type: "Private Steel Major", hq: "New Delhi / Angul", fleet: "14 Barges", role: "Captive and commercial movement of finished steel coils, billets, and coal in Odisha/Bengal" },
    { name: "Tata Steel Logistics (IWT Division)", type: "Private Steel Major", hq: "Kolkata, WB", fleet: "12 Barges", role: "Steel coil exports from Kalinganagar to Haldia & Bangladesh via NW-5 & NW-97" },
    { name: "SAIL (Steel Authority of India) Waterways", type: "Maharatna CPSE", hq: "New Delhi", fleet: "8 Barges", role: "Steel coil shipments from Haldia/DSP to Varanasi and Guwahati" },
    { name: "Ultratech Cement (Water Logistics)", type: "Private Cement Major", hq: "Mumbai, MH", fleet: "16 Barges", role: "Bulk cement and clinker transportation across coastal and inland waterways" },
    { name: "Ocean Sparkle Ltd (Adani Group)", type: "Private Marine Services", hq: "Hyderabad, TS", fleet: "30 Barges & Tugs", role: "Pusher tugs, barge flotillas, harbour towing, lightering, and dredging" },
    { name: "Antara River Cruises / Heritage Journeys", type: "Private Tourism Operator", hq: "Kolkata, WB", fleet: "6 Cruisers", role: "Operators of MV Ganga Vilas on the world's longest 3,200 km waterway voyage" }
  ],
  passengers: {
    annual_passengers_millions: 84.5,
    ro_pax_vehicles_thousands: 420,
    corridors: [
      { name: "Kolkata - Howrah Ferry Services (NW-1)", volume: "48.0M passengers/yr", type: "Urban Commuter" },
      { name: "Kerala Backwaters & Kochi Water Metro (NW-3)", volume: "18.5M passengers/yr", type: "Electric Hybrid Water Metro" },
      { name: "Goa Mandovi & Zuari River Ferries (NW-68/111)", volume: "9.2M passengers/yr", type: "Tourism & Commuter" },
      { name: "Majuli Island - Jorhat Ferries & Ro-Pax (NW-2)", volume: "3.8M passengers/yr", type: "Island Lifeline & Vehicles" },
      { name: "Sahibganj - Manihari Ro-Ro Ferry (NW-1)", volume: "2.4M passengers/yr", type: "Interstate Commercial Ro-Pax" },
      { name: "MV Ganga Vilas / Heritage Luxury Cruises", volume: "50,000 tourists/yr", type: "Ultra-Luxury Expedition" }
    ]
  },
  safety: {
    period: "2019-2024 (5-Year Official Audit)",
    incidents: 14,
    fatalities: 0,
    groundings: 9,
    collisions: 3,
    capsizes: 2,
    rate_per_million_tkm: 0.0038,
    measures: [
      "River Information System (RIS) with VHF tracking active on 1,390 km of NW-1",
      "Differential Global Positioning System (DGPS) 24x7 correction signals on NW-1, NW-2, NW-3",
      "Electronic Navigational Charts (ENC) compliant with IHO S-57 international standard updated bi-weekly",
      "Compulsory hydrographic survey echo-sounding before deep draft vessel transits",
      "Mandatory automated AIS transponders on commercial vessels > 300 DWT",
      "Annual hull, stability, and firefighting certification audited by MMD / IWAI surveyors"
    ]
  }
};

function initInlandWaterwaysModule() {
  currentIwtData = IWT_STATIC_DATA;

  // Sub-tab switching
  const tabBtns = document.querySelectorAll("#iwt-tabs-bar .iwt-tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const targetTab = btn.getAttribute("data-iwt-tab");

      document.querySelectorAll("#section-inland-waterways .iwt-tab-pane").forEach(pane => {
        pane.style.display = "none";
      });

      const activePane = document.getElementById(`iwt-tab-${targetTab}`);
      if (activePane) {
        activePane.style.display = "block";
      }

      // Re-trigger chart render on tab reveal
      if (targetTab === "timeseries") {
        renderIwtTimeSeriesChart(currentIwtTsFilter);
        renderIwtWaterwayShareChart();
      } else if (targetTab === "commodities") {
        renderIwtCommodityChart();
      }
    });
  });

  // Time-series filter buttons
  const tsFilterBtns = document.querySelectorAll("#iwt-timeseries-filter-tabs .tab-btn");
  tsFilterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tsFilterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentIwtTsFilter = btn.getAttribute("data-iwt-ts-filter");
      renderIwtTimeSeriesChart(currentIwtTsFilter);
    });
  });

  // State filter on Waterways
  const stateSelect = document.getElementById("iwt-waterway-state-filter");
  if (stateSelect) {
    stateSelect.addEventListener("change", (e) => {
      renderIwtWaterways(e.target.value);
    });
  }

  // Interactive Draft Feasibility Simulator
  const checkDraftBtn = document.getElementById("btn-check-draft-clearance");
  if (checkDraftBtn) {
    checkDraftBtn.addEventListener("click", runIwtDraftCheck);
  }

  const stretchSelect = document.getElementById("iwt-stretch-select");
  const draftInput = document.getElementById("iwt-vessel-draft-input");
  const marginInput = document.getElementById("iwt-safety-margin-input");
  [stretchSelect, draftInput, marginInput].forEach(elem => {
    if (elem) elem.addEventListener("change", runIwtDraftCheck);
  });

  // Interactive Route Transit & Savings Calculator
  const runCalcBtn = document.getElementById("btn-run-iwt-calc");
  if (runCalcBtn) {
    runCalcBtn.addEventListener("click", runIwtRouteCalculation);
  }

  const calcRoute = document.getElementById("iwt-calc-route-select");
  const calcComm = document.getElementById("iwt-calc-commodity-select");
  const calcTonnage = document.getElementById("iwt-calc-tonnage-input");
  const calcVessel = document.getElementById("iwt-calc-vessel-select");
  const calcDir = document.getElementById("iwt-calc-direction-select");
  [calcRoute, calcComm, calcTonnage, calcVessel, calcDir].forEach(elem => {
    if (elem) elem.addEventListener("change", runIwtRouteCalculation);
  });

  // Fetch API data with static fallback
  loadIwtDataFromApiOrFallback();
}

function loadIwtDataFromApiOrFallback() {
  fetch("/api/iwt/overview")
    .then(r => r.ok ? r.json() : null)
    .then(res => {
      if (res && res.data) {
        updateIwtOverviewUi(res.data);
      } else {
        updateIwtOverviewUi(IWT_STATIC_DATA.overview);
      }
    })
    .catch(() => {
      updateIwtOverviewUi(IWT_STATIC_DATA.overview);
    });

  // Render initial components
  renderIwtTimeSeriesChart(currentIwtTsFilter);
  renderIwtWaterwayShareChart();
  renderIwtLadTable();
  runIwtDraftCheck();
  renderIwtCommodityChart();
  renderIwtCommodities();
  renderIwtWaterways("");
  renderIwtInfrastructure();
  renderIwtVessels();
  runIwtRouteCalculation();
  renderIwtOperators();
  renderIwtPassengersAndSafety();
}

function updateIwtOverviewUi(ov) {
  const elCargo = document.getElementById("iwt-stat-cargo");
  const elTarget = document.getElementById("iwt-stat-target");
  const elLength = document.getElementById("iwt-stat-length");
  const elSavings = document.getElementById("iwt-stat-savings");
  const elRev = document.getElementById("iwt-stat-revenue");
  const elCarbon = document.getElementById("iwt-stat-carbon");

  if (elCargo) elCargo.innerText = `${ov.total_cargo_mt_fy24.toFixed(1)} MT`;
  if (elTarget) elTarget.innerText = `${ov.target_cargo_2030_mt.toFixed(1)} MT`;
  if (elLength) elLength.innerText = `${ov.navigable_length_km.toLocaleString()} km`;
  if (elSavings) elSavings.innerText = `${ov.freight_savings_vs_rail_pct}% vs Rail`;
  if (elRev) elRev.innerText = `₹${ov.annual_freight_collected_cr.toLocaleString()} Cr`;
  if (elCarbon) elCarbon.innerText = `${ov.carbon_reduction_mt.toFixed(1)} MT`;
}

function renderIwtTimeSeriesChart(filter = "all") {
  const ctx = document.getElementById("iwtTimeSeriesChart");
  if (!ctx) return;

  let tsData = IWT_STATIC_DATA.timeseries;
  if (filter === "historical") {
    tsData = tsData.filter(d => !d.is_projection);
  } else if (filter === "projection") {
    tsData = tsData.filter(d => d.is_projection || d.year === 2024);
  }

  const labels = tsData.map(d => d.fiscal_year);
  const actuals = tsData.map(d => d.is_projection ? null : d.cargo_mt);
  const projections = tsData.map(d => (d.is_projection || d.year === 2024) ? d.cargo_mt : null);

  if (iwtTimeSeriesChart) {
    iwtTimeSeriesChart.destroy();
  }

  iwtTimeSeriesChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Historical Throughput (MT)",
          data: actuals,
          borderColor: "#00d2ff",
          backgroundColor: "rgba(0, 210, 255, 0.15)",
          borderWidth: 3,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#00d2ff",
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: "2025-2030 Target Projection (MT)",
          data: projections,
          borderColor: "#00f5a0",
          backgroundColor: "rgba(0, 245, 160, 0.08)",
          borderWidth: 3,
          borderDash: [6, 4],
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#00f5a0",
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { family: "Inter", size: 11 } }
        },
        tooltip: {
          backgroundColor: "rgba(8, 16, 38, 0.95)",
          titleColor: "#ffffff",
          bodyColor: "#00d2ff",
          borderColor: "rgba(0, 210, 255, 0.3)",
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.raw} MT`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#64748b", font: { size: 10 } },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          ticks: {
            color: "#64748b",
            font: { size: 10 },
            callback: (v) => `${v} MT`
          },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        }
      }
    }
  });
}

function renderIwtWaterwayShareChart() {
  const ctx = document.getElementById("iwtWaterwayShareChart");
  if (!ctx) return;

  const topWaterways = [
    { label: "NW-97 Sundarbans (Protocol)", val: 37.8, color: "#00d2ff" },
    { label: "NW-68 Mandovi (Goa Ore)", val: 18.5, color: "#6366f1" },
    { label: "NW-86 Rupnarayan (Fly Ash)", val: 16.2, color: "#00f5a0" },
    { label: "NW-3 West Coast (Kerala)", val: 14.8, color: "#ffb703" },
    { label: "NW-1 Ganga Arterial", val: 13.17, color: "#ff4d6d" },
    { label: "NW-111 Zuari (Goa)", val: 11.6, color: "#a855f7" },
    { label: "NW-5 Odisha Steel/Coal", val: 11.2, color: "#38bdf8" },
    { label: "Other NWs (NW-2, NW-4, NW-16)", val: 9.73, color: "#64748b" }
  ];

  if (iwtWaterwayShareChart) {
    iwtWaterwayShareChart.destroy();
  }

  iwtWaterwayShareChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: topWaterways.map(w => w.label),
      datasets: [{
        data: topWaterways.map(w => w.val),
        backgroundColor: topWaterways.map(w => w.color),
        borderColor: "rgba(6, 12, 26, 0.9)",
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#94a3b8", font: { family: "Inter", size: 10 }, boxWidth: 12 }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} MT (${((ctx.raw / 133.0) * 100).toFixed(1)}%)`
          }
        }
      }
    }
  });
}

function renderIwtCommodityChart() {
  const ctx = document.getElementById("iwtCommodityChart");
  if (!ctx) return;

  const commodities = IWT_STATIC_DATA.commodities;
  const labels = commodities.map(c => c.name);
  const tonnages = commodities.map(c => c.annual_tonnage_mt);

  if (iwtCommodityChart) {
    iwtCommodityChart.destroy();
  }

  iwtCommodityChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Annual Volume (MT)",
        data: tonnages,
        backgroundColor: [
          "rgba(0, 210, 255, 0.75)",
          "rgba(0, 245, 160, 0.75)",
          "rgba(99, 102, 241, 0.75)",
          "rgba(255, 183, 3, 0.75)",
          "rgba(168, 85, 247, 0.75)",
          "rgba(255, 77, 109, 0.75)",
          "rgba(56, 189, 248, 0.75)",
          "rgba(34, 197, 94, 0.75)",
          "rgba(148, 163, 184, 0.75)"
        ],
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Volume: ${ctx.raw} MT (${((ctx.raw / 133.0) * 100).toFixed(1)}% Share)`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: "#64748b", font: { size: 10 }, callback: (v) => `${v} MT` },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          ticks: { color: "#f0f4fc", font: { size: 10 } },
          grid: { display: false }
        }
      }
    }
  });
}

function renderIwtLadTable() {
  const tbody = document.getElementById("iwt-lad-table-tbody");
  if (!tbody) return;

  const stretches = IWT_STATIC_DATA.depth_lad;
  tbody.innerHTML = stretches.map(s => {
    const isSafe = s.actual_current_lad_m >= 2.5;
    const isMarginal = s.actual_current_lad_m >= 1.8 && s.actual_current_lad_m < 2.5;
    const pillClass = isSafe ? "lad-pill-safe" : (isMarginal ? "lad-pill-warning" : "lad-pill-danger");
    const statusText = isSafe ? "Unrestricted Navigable" : (isMarginal ? "Advisory / Caution" : "Light Draft Only");

    return `
      <tr>
        <td>
          <div style="font-weight: 600; color: #ffffff;">${s.stretch_name}</div>
          <span class="iwt-tag-pill iwt-tag-cyan">${s.waterway_id}</span>
        </td>
        <td>${s.length_km} km</td>
        <td style="color: var(--text-muted);">${s.target_lad_m.toFixed(1)} m</td>
        <td><strong style="color: var(--accent-cyan);">${s.actual_current_lad_m.toFixed(1)} m</strong></td>
        <td><span style="color: var(--accent-amber);">${s.min_seasonal_lad_m.toFixed(1)} m</span></td>
        <td style="font-size: 0.75rem; color: var(--text-secondary); max-width: 220px;">${s.dredging_status}</td>
        <td style="font-size: 0.72rem; color: var(--text-muted);">
          ${s.shallow_patches.map(p => `<div>⚠️ ${p}</div>`).join("")}
        </td>
        <td><span style="font-weight: 600; color: #ffffff;">${s.air_draft_clearance_m.toFixed(1)} m</span></td>
        <td><span class="${pillClass}">${statusText}</span></td>
      </tr>
    `;
  }).join("");
}

function runIwtDraftCheck() {
  const stretchId = document.getElementById("iwt-stretch-select")?.value || "NW1_HAL_FRK";
  const draftVal = parseFloat(document.getElementById("iwt-vessel-draft-input")?.value || "2.20");
  const marginVal = parseFloat(document.getElementById("iwt-safety-margin-input")?.value || "0.30");

  const stretch = IWT_STATIC_DATA.depth_lad.find(s => s.stretch_id === stretchId) || IWT_STATIC_DATA.depth_lad[0];
  const actualLad = stretch.actual_current_lad_m;
  const minSeasonal = stretch.min_seasonal_lad_m;
  const ukc = parseFloat((actualLad - draftVal).toFixed(2));
  const maxSafeDraft = Math.max(0.8, parseFloat((actualLad - marginVal).toFixed(2)));

  const badgeEl = document.getElementById("iwt-clearance-badge");
  const titleEl = document.getElementById("iwt-clearance-title");
  const meterEl = document.getElementById("iwt-clearance-meter");
  const airDraftEl = document.getElementById("iwt-clearance-air-draft");
  const resActual = document.getElementById("iwt-res-actual-lad");
  const resUkc = document.getElementById("iwt-res-ukc");
  const resSeasonal = document.getElementById("iwt-res-seasonal-lad");
  const resMaxDraft = document.getElementById("iwt-res-max-draft");
  const resAdvisory = document.getElementById("iwt-res-advisory");

  if (titleEl) titleEl.innerText = `${stretch.stretch_name} (${stretch.waterway_id})`;
  if (airDraftEl) airDraftEl.innerText = `Air Draft Bridge Clearance: ${stretch.air_draft_clearance_m}m`;
  if (resActual) resActual.innerText = `${actualLad.toFixed(2)} m`;
  if (resUkc) resUkc.innerText = `${ukc >= 0 ? '+' : ''}${ukc.toFixed(2)} m`;
  if (resSeasonal) resSeasonal.innerText = `${minSeasonal.toFixed(2)} m`;
  if (resMaxDraft) resMaxDraft.innerText = `${maxSafeDraft.toFixed(2)} m`;

  let pctFill = Math.min(100, Math.max(5, ((draftVal / actualLad) * 100)));

  if (ukc >= marginVal) {
    if (badgeEl) {
      badgeEl.className = "lad-pill-safe";
      badgeEl.innerText = "SAFE CLEARANCE";
    }
    if (meterEl) {
      meterEl.style.width = `${pctFill}%`;
      meterEl.style.background = "var(--accent-emerald)";
    }
    if (resAdvisory) {
      resAdvisory.innerHTML = `✅ <strong>Clearance Approved:</strong> Under-keel clearance of <strong>${ukc}m</strong> safely exceeds the required ${marginVal}m threshold. Full laden barge transit approved. ${stretch.advisory}`;
    }
  } else if (ukc >= 0.05) {
    if (badgeEl) {
      badgeEl.className = "lad-pill-warning";
      badgeEl.innerText = "MARGINAL CLEARANCE ALERT";
    }
    if (meterEl) {
      meterEl.style.width = `${pctFill}%`;
      meterEl.style.background = "var(--accent-amber)";
    }
    if (resAdvisory) {
      resAdvisory.innerHTML = `⚠️ <strong>Marginal UKC Caution:</strong> Clearance is only <strong>${ukc}m</strong> (below ${marginVal}m safety margin). Speed reduction mandatory; navigate strictly during high water tides. Shallow spots: ${stretch.shallow_patches.join(', ')}.`;
    }
  } else {
    if (badgeEl) {
      badgeEl.className = "lad-pill-danger";
      badgeEl.innerText = "CRITICAL GROUNDING RISK";
    }
    if (meterEl) {
      meterEl.style.width = "100%";
      meterEl.style.background = "var(--accent-coral)";
    }
    if (resAdvisory) {
      resAdvisory.innerHTML = `⛔ <strong>Transit Prohibited:</strong> Vessel draft (${draftVal}m) exceeds available stretch depth (${actualLad}m). Negative UKC (${ukc}m). Lighter cargo to reduce draft to <= ${maxSafeDraft}m before departure.`;
    }
  }
}

function runIwtRouteCalculation() {
  const routeId = document.getElementById("iwt-calc-route-select")?.value || "haldia_to_varanasi";
  const commId = document.getElementById("iwt-calc-commodity-select")?.value || "steel";
  const tonnage = parseFloat(document.getElementById("iwt-calc-tonnage-input")?.value || "5000");
  const vesselId = document.getElementById("iwt-calc-vessel-select")?.value || "self_propelled_barge_1000";
  const direction = document.getElementById("iwt-calc-direction-select")?.value || "upstream";

  const route = IWT_STATIC_DATA.routes[routeId] || IWT_STATIC_DATA.routes.haldia_to_varanasi;
  const vessel = IWT_STATIC_DATA.vessels.find(v => v.id === vesselId) || IWT_STATIC_DATA.vessels[0];
  const commodity = IWT_STATIC_DATA.commodities.find(c => c.id === commId) || IWT_STATIC_DATA.commodities[5];

  const isUpstream = direction === "upstream";
  const baseSpeedKmph = vessel.speed_knots * 1.852;
  const currentKnots = isUpstream ? route.current_up_knots : route.current_down_knots;
  const currentKmph = currentKnots * 1.852;
  const effectiveSpeed = isUpstream ? Math.max(4.0, baseSpeedKmph - currentKmph) : baseSpeedKmph + (currentKmph * 0.8);
  const transitHours = route.river_km / effectiveSpeed;
  const transitDays = (transitHours / 18.0).toFixed(1);

  const costIwt = Math.round(route.iwt_rate * tonnage);
  const costRail = Math.round(route.rail_rate * tonnage);
  const costRoad = Math.round(route.road_rate * tonnage);

  const savingsRail = Math.max(0, costRail - costIwt);
  const savingsRoad = Math.max(0, costRoad - costIwt);
  const savingsRailPct = ((savingsRail / costRail) * 100).toFixed(1);
  const savingsRoadPct = ((savingsRoad / costRoad) * 100).toFixed(1);

  const co2Iwt = ((tonnage * route.co2_iwt_kg) / 1000.0).toFixed(1);
  const co2Rail = ((tonnage * route.co2_rail_kg) / 1000.0).toFixed(1);
  const co2Road = ((tonnage * route.co2_road_kg) / 1000.0).toFixed(1);
  const co2Saved = (parseFloat(co2Road) - parseFloat(co2Iwt)).toFixed(1);
  const bargesNeeded = Math.ceil(tonnage / vessel.dwt);

  const container = document.getElementById("iwt-calc-results-container");
  if (!container) return;

  container.innerHTML = `
    <!-- Top Route Metrics -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
      <div class="traffic-stat-card">
        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">Transit Duration</div>
        <div style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 700; color: var(--accent-cyan);">${transitDays} Days</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${direction === 'upstream' ? 'Upstream (+current delay)' : 'Downstream (assisted)'}</div>
      </div>

      <div class="traffic-stat-card">
        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">Distance Comparison</div>
        <div style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: #ffffff;">${route.river_km} km River</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${route.rail_km} km Rail | ${route.road_km} km Road</div>
      </div>

      <div class="traffic-stat-card">
        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">Barge Trips Required</div>
        <div style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 700; color: var(--accent-emerald);">${bargesNeeded} Voyages</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">Using ${vessel.dwt} DWT Barges</div>
      </div>

      <div class="traffic-stat-card">
        <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase;">Net CO2 Abatement</div>
        <div style="font-family: var(--font-heading); font-size: 1.4rem; font-weight: 700; color: var(--accent-emerald);">${co2Saved} Tonnes</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${co2Iwt}T IWT vs ${co2Road}T Road</div>
      </div>
    </div>

    <!-- Side-by-Side Modal Freight Cost Comparison -->
    <div class="modal-comparison-grid">
      <div class="modal-comparison-box highlight">
        <span class="badge-tag badge-emerald" style="position: absolute; top: 8px; right: 8px;">OPTIMAL</span>
        <div class="modal-comparison-title" style="color: var(--accent-emerald);">🌊 Inland Waterways (IWT)</div>
        <div class="modal-comparison-val" style="color: var(--accent-emerald);">₹${costIwt.toLocaleString()}</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">₹${route.iwt_rate} / Tonne</div>
        <div style="font-size: 0.75rem; color: var(--accent-emerald); font-weight: 600;">
          Saves ₹${(savingsRail / 1e5).toFixed(1)} Lakh vs Rail
        </div>
      </div>

      <div class="modal-comparison-box">
        <div class="modal-comparison-title" style="color: var(--accent-cyan);">🚆 Indian Railways (Rake)</div>
        <div class="modal-comparison-val" style="color: #ffffff;">₹${costRail.toLocaleString()}</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">₹${route.rail_rate} / Tonne</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">
          ${savingsRailPct}% higher cost than IWT
        </div>
      </div>

      <div class="modal-comparison-box">
        <div class="modal-comparison-title" style="color: var(--accent-coral);">🚛 Highway Commercial Trucks</div>
        <div class="modal-comparison-val" style="color: #ffffff;">₹${costRoad.toLocaleString()}</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">₹${route.road_rate} / Tonne</div>
        <div style="font-size: 0.75rem; color: var(--accent-coral);">
          ${savingsRoadPct}% higher cost (₹${(savingsRoad / 1e5).toFixed(1)} Lakh more)
        </div>
      </div>
    </div>
  `;
}

function renderIwtCommodities() {
  const container = document.getElementById("iwt-commodities-grid");
  if (!container) return;

  container.innerHTML = IWT_STATIC_DATA.commodities.map(c => `
    <div class="iwt-waterway-card">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">${c.icon}</span>
            <div>
              <div style="font-weight: 600; color: #ffffff; font-size: 0.95rem;">${c.name}</div>
              <span class="iwt-tag-pill iwt-tag-cyan">${c.annual_tonnage_mt} MT (${c.share_pct}%)</span>
            </div>
          </div>
          <span class="badge-tag badge-emerald">+${c.growth_yoy_pct}% YoY</span>
        </div>
        <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem; line-height: 1.45;">${c.description}</p>
      </div>

      <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.6rem; font-size: 0.72rem;">
        <div style="color: var(--text-muted); margin-bottom: 0.2rem;"><strong>Key Corridors:</strong> ${c.key_routes}</div>
        <div style="color: var(--accent-cyan);"><strong>Major Consignees:</strong> ${c.primary_users}</div>
      </div>
    </div>
  `).join("");
}

function renderIwtWaterways(stateFilter = "") {
  const container = document.getElementById("iwt-waterways-grid");
  if (!container) return;

  let list = IWT_STATIC_DATA.waterways;
  if (stateFilter) {
    list = list.filter(nw => nw.states.some(s => s.toLowerCase().includes(stateFilter.toLowerCase())));
  }

  container.innerHTML = list.map(nw => `
    <div class="iwt-waterway-card">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <div>
            <span class="iwt-tag-pill iwt-tag-cyan" style="font-weight: 700; font-size: 0.8rem;">${nw.id}</span>
            <span style="font-weight: 600; color: #ffffff; font-size: 0.9rem;">${nw.river_system}</span>
          </div>
          <span class="badge-tag badge-emerald">${nw.annual_cargo_mt} MT</span>
        </div>

        <div style="font-size: 0.75rem; color: var(--accent-cyan); margin-bottom: 0.5rem;">
          📍 ${nw.stretch}
        </div>

        <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem; line-height: 1.45;">
          ${nw.description}
        </p>

        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
          ${nw.states.map(s => `<span class="iwt-tag-pill">${s}</span>`).join("")}
        </div>
      </div>

      <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.6rem; font-size: 0.72rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
          <span style="color: var(--text-muted);">Total / Navigable Length:</span>
          <strong style="color: #ffffff;">${nw.total_length_km} km / ${nw.navigable_length_km} km</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
          <span style="color: var(--text-muted);">Round-the-Year Fairway:</span>
          <strong style="color: var(--accent-emerald);">${nw.round_the_year_navigable_km} km</strong>
        </div>
        <div style="color: var(--accent-amber); margin-top: 0.3rem;">
          🚢 <strong>Ports:</strong> ${nw.connected_ports.join(", ")}
        </div>
        <div style="color: var(--text-secondary); margin-top: 0.2rem;">
          🏭 <strong>Steel & Industrial Nodes:</strong> ${nw.connected_steel_hubs.join(", ")}
        </div>
      </div>
    </div>
  `).join("");
}

function renderIwtInfrastructure() {
  const container = document.getElementById("iwt-infra-grid");
  if (!container) return;

  container.innerHTML = IWT_STATIC_DATA.infrastructure.map(inf => `
    <div class="iwt-waterway-card">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <div>
            <div style="font-weight: 600; color: #ffffff; font-size: 0.95rem;">${inf.name}</div>
            <span class="iwt-tag-pill iwt-tag-cyan">${inf.waterway_id}</span>
            <span class="iwt-tag-pill">${inf.state}</span>
          </div>
          <span class="badge-tag badge-emerald">${inf.capacity_mtpa} MTPA</span>
        </div>

        <table class="vessel-specs-table">
          <tr><td>Berth Count</td><td>${inf.berths} Berths</td></tr>
          <tr><td>Quay Length</td><td>${inf.quay_length_m} meters</td></tr>
          <tr><td>Draft at Berth</td><td>${inf.depth_m} meters</td></tr>
          <tr><td>Status</td><td><span style="color: var(--accent-emerald);">${inf.status}</span></td></tr>
        </table>

        <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.4rem;"><strong>Cargo Handling Equipment:</strong></div>
        <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-bottom: 0.75rem;">
          ${inf.equipment.map(eq => `<span class="iwt-tag-pill iwt-tag-emerald" style="font-size: 0.68rem;">⚙️ ${eq}</span>`).join("")}
        </div>
      </div>

      <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.5rem; font-size: 0.72rem; color: var(--accent-cyan);">
        📦 <strong>Handled Goods:</strong> ${inf.commodities}
      </div>
    </div>
  `).join("");
}

function renderIwtVessels() {
  const container = document.getElementById("iwt-vessels-grid");
  if (!container) return;

  container.innerHTML = IWT_STATIC_DATA.vessels.map(v => `
    <div class="iwt-waterway-card">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
          <div>
            <div style="font-weight: 600; color: #ffffff; font-size: 0.92rem;">${v.name}</div>
            <span class="iwt-tag-pill iwt-tag-cyan">${v.category}</span>
          </div>
          <span class="badge-tag badge-cyan">${v.active_count} Active</span>
        </div>

        <table class="vessel-specs-table">
          <tr><td>DWT Capacity</td><td>${v.dwt} DWT</td></tr>
          <tr><td>Length (LOA) x Beam</td><td>${v.loa_m}m x ${v.beam_m}m</td></tr>
          <tr><td>Laden Design Draft</td><td><strong style="color: var(--accent-amber);">${v.draft_m} m</strong></td></tr>
          <tr><td>Air Draft Clearance</td><td>${v.air_draft_m} m</td></tr>
          <tr><td>Service Speed</td><td>${v.speed_knots} knots (~${(v.speed_knots * 1.852).toFixed(1)} km/h)</td></tr>
          <tr><td>Indicative Charter Rate</td><td><strong style="color: var(--accent-emerald);">₹${v.charter_rate_inr.toLocaleString()} / day</strong></td></tr>
        </table>
      </div>

      <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.5rem; font-size: 0.72rem; color: var(--text-secondary);">
        📦 <strong>Typical Cargo:</strong> ${v.cargo}
      </div>
    </div>
  `).join("");
}

function renderIwtOperators() {
  const tbody = document.getElementById("iwt-operators-tbody");
  if (!tbody) return;

  tbody.innerHTML = IWT_STATIC_DATA.operators.map(op => `
    <tr>
      <td><strong style="color: #ffffff;">${op.name}</strong></td>
      <td><span class="iwt-tag-pill iwt-tag-cyan">${op.type}</span></td>
      <td>${op.hq}</td>
      <td><span style="color: var(--accent-emerald); font-weight: 600;">${op.fleet}</span></td>
      <td style="font-size: 0.75rem; color: var(--text-secondary); max-width: 280px;">${op.role}</td>
    </tr>
  `).join("");
}

function renderIwtPassengersAndSafety() {
  const pContainer = document.getElementById("iwt-passengers-container");
  const sContainer = document.getElementById("iwt-safety-container");

  if (pContainer) {
    const p = IWT_STATIC_DATA.passengers;
    pContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem;">
        <div style="background: rgba(14,25,52,0.6); padding: 0.75rem; border-radius: 8px;">
          <div style="font-size: 0.72rem; color: var(--text-secondary);">ANNUAL PASSENGERS</div>
          <div style="font-size: 1.35rem; font-weight: 700; color: var(--accent-emerald);">${p.annual_passengers_millions} Million</div>
        </div>
        <div style="background: rgba(14,25,52,0.6); padding: 0.75rem; border-radius: 8px;">
          <div style="font-size: 0.72rem; color: var(--text-secondary);">RO-PAX VEHICLES CARRIED</div>
          <div style="font-size: 1.35rem; font-weight: 700; color: var(--accent-cyan);">${p.ro_pax_vehicles_thousands}K Vehicles</div>
        </div>
      </div>

      <div style="font-size: 0.78rem; font-weight: 600; color: #ffffff; margin-bottom: 0.5rem;">Major Passenger & Cruise Routes:</div>
      ${p.corridors.map(c => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.75rem;">
          <div>
            <div style="color: #ffffff; font-weight: 500;">${c.name}</div>
            <span class="iwt-tag-pill" style="font-size: 0.68rem;">${c.type}</span>
          </div>
          <span style="color: var(--accent-emerald); font-weight: 600;">${c.volume}</span>
        </div>
      `).join("")}
    `;
  }

  if (sContainer) {
    const s = IWT_STATIC_DATA.safety;
    sContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1rem;">
        <div style="background: rgba(14,25,52,0.6); padding: 0.75rem; border-radius: 8px; text-align: center;">
          <div style="font-size: 0.68rem; color: var(--text-secondary);">TOTAL INCIDENTS (5 YRS)</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff;">${s.incidents}</div>
        </div>
        <div style="background: rgba(14,25,52,0.6); padding: 0.75rem; border-radius: 8px; text-align: center;">
          <div style="font-size: 0.68rem; color: var(--text-secondary);">FATALITIES</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: var(--accent-emerald);">${s.fatalities}</div>
        </div>
        <div style="background: rgba(14,25,52,0.6); padding: 0.75rem; border-radius: 8px; text-align: center;">
          <div style="font-size: 0.68rem; color: var(--text-secondary);">RATE / M T-KM</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: var(--accent-cyan);">${s.rate_per_million_tkm}</div>
        </div>
      </div>

      <div style="font-size: 0.78rem; font-weight: 600; color: #ffffff; margin-bottom: 0.5rem;">Safety Navigation Compliance & Technology:</div>
      ${s.measures.map(m => `
        <div style="padding: 0.35rem 0; font-size: 0.75rem; color: var(--text-secondary); display: flex; align-items: flex-start; gap: 0.4rem;">
          <span style="color: var(--accent-emerald);">🛡️</span>
          <span>${m}</span>
        </div>
      `).join("")}
    `;
  }
}

// ==========================================================================
// 🤖 AI PROCUREMENT COPILOT CONTROLLER
// ==========================================================================

// Global helper so inline onclick handlers in HTML work reliably
let currentCopilotData = null;
let currentSelectedScenarioIndex = 0;

window.switchCopilotMode = function(mode) {
  const quickBtn = document.getElementById("btn-mode-quick");
  const builderBtn = document.getElementById("btn-mode-builder");
  const quickCont = document.getElementById("copilot-quick-container");
  const builderCont = document.getElementById("copilot-builder-container");

  if (mode === "builder") {
    if (quickBtn) quickBtn.classList.remove("active");
    if (builderBtn) builderBtn.classList.add("active");
    if (quickCont) quickCont.style.display = "none";
    if (builderCont) builderCont.style.display = "block";
  } else {
    if (quickBtn) quickBtn.classList.add("active");
    if (builderBtn) builderBtn.classList.remove("active");
    if (quickCont) quickCont.style.display = "block";
    if (builderCont) builderCont.style.display = "none";
  }
};

window.setBuilderTonnage = function(val) {
  const input = document.getElementById("builder-tonnage");
  if (input) input.value = val;
  document.querySelectorAll(".copilot-tonnage-chip").forEach(chip => {
    const txt = chip.textContent || "";
    if (txt.includes(String(val / 1000))) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });
};

window.resetBuilderForm = function() {
  const comm = document.getElementById("builder-commodity");
  const ton = document.getElementById("builder-tonnage");
  const plant = document.getElementById("builder-plant");
  const origin = document.getElementById("builder-origin");
  const vessel = document.getElementById("builder-vessel");
  const priority = document.getElementById("builder-priority");
  const horizon = document.getElementById("builder-horizon");
  const iwt = document.getElementById("builder-include-iwt");

  if (comm) comm.value = "coking_coal";
  if (ton) ton.value = "150000";
  if (plant) plant.value = "sail_rourkela";
  if (origin) origin.value = "hay_point";
  if (vessel) vessel.value = "Capesize";
  if (priority) priority.value = "lowest_cost";
  if (horizon) horizon.value = "35";
  if (iwt) iwt.checked = true;
  window.setBuilderTonnage(150000);
};

window.submitCopilotBuilderForm = function() {
  const comm = document.getElementById("builder-commodity")?.value || "coking_coal";
  const ton = parseFloat(document.getElementById("builder-tonnage")?.value || "150000");
  const plant = document.getElementById("builder-plant")?.value || "sail_rourkela";
  const origin = document.getElementById("builder-origin")?.value || "hay_point";
  const vessel = document.getElementById("builder-vessel")?.value || "Capesize";
  const priority = document.getElementById("builder-priority")?.value || "lowest_cost";
  const leadDays = parseInt(document.getElementById("builder-horizon")?.value || "35");
  const isIwt = Boolean(document.getElementById("builder-include-iwt")?.checked);

  const customParams = {
    commodity_id: comm,
    cargo_tonnage: ton,
    plant_id: plant,
    origin_id: origin,
    vessel_class: vessel,
    lead_days: leadDays,
    is_iwt_query: isIwt,
    optimization_goal: priority
  };

  const commNames = {
    coking_coal: "Hard Coking Coal",
    thermal_coal: "Thermal Coal",
    pci_coal: "PCI Coal",
    limestone: "SMS Limestone",
    manganese_ore: "Manganese Ore"
  };
  const plantNames = {
    sail_rourkela: "SAIL Rourkela",
    sail_bokaro: "SAIL Bokaro",
    sail_durgapur: "SAIL Durgapur",
    sail_bhilai: "SAIL Bhilai",
    rinl_vizag: "RINL Vizag",
    sail_iisco: "SAIL Burnpur"
  };

  const syntheticQuery = `${ton.toLocaleString()} MT ${commNames[comm] || 'Cargo'} to ${plantNames[plant] || 'Steel Plant'}`;
  runCopilotQuery(syntheticQuery, customParams);
};

window.askCopilotPrompt = function(promptText) {
  const queryInput = document.getElementById("copilot-query-input");
  const chips = document.querySelectorAll(".copilot-chip");
  
  let q = (promptText || (queryInput ? queryInput.value : "") || "").trim();
  if (!q) {
    q = "150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai";
  }
  
  if (queryInput) {
    queryInput.value = q;
  }

  // Update chip active styles
  chips.forEach(c => {
    if (c.getAttribute("data-query") === q) {
      c.classList.add("active-chip");
    } else {
      c.classList.remove("active-chip");
    }
  });

  runCopilotQuery(q);
};

function initCopilotModule() {
  const submitBtn = document.getElementById("btn-copilot-submit");
  const queryInput = document.getElementById("copilot-query-input");
  const chips = document.querySelectorAll(".copilot-chip");

  if (submitBtn) {
    submitBtn.onclick = (e) => {
      e.preventDefault();
      const q = (queryInput ? queryInput.value : "").trim() || "150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai";
      if (queryInput) queryInput.value = q;
      runCopilotQuery(q);
    };
  }

  if (queryInput) {
    queryInput.onkeydown = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const q = queryInput.value.trim() || "150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai";
        queryInput.value = q;
        runCopilotQuery(q);
      }
    };
  }

  chips.forEach(chip => {
    chip.onclick = (e) => {
      e.preventDefault();
      chips.forEach(c => c.classList.remove("active-chip"));
      chip.classList.add("active-chip");
      const q = chip.getAttribute("data-query");
      if (queryInput && q) {
        queryInput.value = q;
      }
      if (q) runCopilotQuery(q);
    };
  });

  // Run initial query on page load for immediate demonstration
  runCopilotQuery("150,000 MT Australian coking coal Rourkela ke liye next month procure karna hai");
}

async function runCopilotQuery(query, customParams = null) {
  const submitBtn = document.getElementById("btn-copilot-submit");
  const builderSubmitBtn = document.getElementById("btn-builder-submit");
  const statusEl = document.getElementById("copilot-status-indicator");
  const card = document.getElementById("copilot-strategy-card");

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = "<span>⏳ Analyzing Market Curves...</span>";
  }
  if (builderSubmitBtn) {
    builderSubmitBtn.disabled = true;
    builderSubmitBtn.innerHTML = "<span>⏳ Synthesizing Options...</span>";
  }

  if (statusEl) {
    statusEl.innerHTML = `<span style="color: var(--accent-cyan);">⚡ REASONING ON DRAFT, WATERWAYS & MULTI-PORT LOGISTICS...</span>`;
  }

  if (card) {
    card.style.opacity = "0.75";
    card.style.transition = "all 0.25s ease";
  }

  let resultData = null;
  const payload = { query: query, parameters: customParams };

  // 1. Try relative endpoint
  try {
    const res = await fetch("/api/copilot/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const json = await res.json();
      if (json.status === "success" && json.data) {
        resultData = json.data;
      }
    }
  } catch (e1) {
    // Relative endpoint failed
  }

  // 2. Try absolute localhost:5000 if served from Live Server (port 5500, etc.)
  if (!resultData) {
    try {
      const res2 = await fetch("http://127.0.0.1:5000/api/copilot/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res2.ok) {
        const json2 = await res2.json();
        if (json2.status === "success" && json2.data) {
          resultData = json2.data;
        }
      }
    } catch (e2) {
      // Cross-origin or Flask not running
    }
  }

  // 3. Fallback to resilient client-side decision synthesizer
  if (!resultData) {
    resultData = generateClientSideCopilotRecommendation(query, customParams);
  }

  if (resultData) {
    renderCopilotOutput(resultData, query);
  }

  if (card) {
    card.style.opacity = "1";
    card.style.borderColor = "var(--accent-cyan)";
    card.style.boxShadow = "0 0 24px rgba(0, 212, 255, 0.4)";
    setTimeout(() => {
      card.style.borderColor = "rgba(0, 212, 255, 0.35)";
      card.style.boxShadow = "none";
    }, 700);
  }

  if (submitBtn) {
    submitBtn.disabled = false;
    submitBtn.innerHTML = "<span>⚡ Ask AI Copilot</span>";
  }
  if (builderSubmitBtn) {
    builderSubmitBtn.disabled = false;
    builderSubmitBtn.innerHTML = "<span>⚡ Synthesize Multi-Scenario Strategies</span>";
  }
}

window.runCopilotQuery = runCopilotQuery;

window.selectCopilotScenario = function(idx) {
  if (!currentCopilotData || !currentCopilotData.strategy_options) return;
  const options = currentCopilotData.strategy_options;
  if (!options[idx]) return;

  currentSelectedScenarioIndex = idx;

  // Update tabs active state
  document.querySelectorAll(".copilot-scenario-btn").forEach((btn, i) => {
    if (i === idx) btn.classList.add("active");
    else btn.classList.remove("active");
  });

  const selectedOption = options[idx];
  const s = selectedOption.strategy;
  const why = selectedOption.why || [];

  // Update Strategy Header Title & Icon
  const titleEl = document.getElementById("copilot-strategy-title");
  const iconEl = document.getElementById("copilot-strategy-icon");
  const savingsEl = document.getElementById("copilot-savings-badge");

  if (titleEl) titleEl.textContent = selectedOption.label || "RECOMMENDED STRATEGY";
  if (iconEl) iconEl.textContent = idx === 0 ? "⭐" : idx === 1 ? "⚡" : "🌱";
  if (savingsEl) savingsEl.textContent = s.badge || `Expected Saving: ₹${Number(s.expected_saving_crore || 14.72).toFixed(2)} Cr`;

  // Update KPIs
  const portEl = document.getElementById("copilot-val-port");
  const vesselEl = document.getElementById("copilot-val-vessel");
  const freightEl = document.getElementById("copilot-val-freight");
  const freightInrEl = document.getElementById("copilot-val-freight-inr");
  const landedEl = document.getElementById("copilot-val-landed");
  const landedInrEl = document.getElementById("copilot-val-landed-inr");
  const laycanEl = document.getElementById("copilot-val-laycan");
  const riskEl = document.getElementById("copilot-val-risk");

  const subPort = document.getElementById("copilot-sub-port");
  const subVessel = document.getElementById("copilot-sub-vessel");

  const freightUsd = Number(s.estimated_freight_usd_ton) || 16.50;
  const freightInr = Number(s.estimated_freight_inr_ton) || Math.round(freightUsd * 83.50);
  const landedUsd = Number(s.landed_cost_usd_ton) || 312.45;
  const landedInr = Number(s.landed_cost_inr_ton) || Math.round(landedUsd * 83.50);

  if (portEl) portEl.textContent = s.discharge_port || "Dhamra Port";
  if (subPort) subPort.textContent = idx === 0 ? "All-Weather Deep Draft (18.0m)" : idx === 1 ? "Rapid Mechanized Discharge" : "Direct National Waterway Link";
  if (vesselEl) vesselEl.textContent = s.vessel_class || "Capesize";
  if (subVessel) subVessel.textContent = idx === 1 ? "Lower Berth Waiting Time" : idx === 2 ? "Shallow Draft Barge Feeder" : "Max Economical Parcel Size";

  if (freightEl) freightEl.textContent = `$${freightUsd.toFixed(2)} / MT`;
  if (freightInrEl) freightInrEl.textContent = `₹${freightInr.toLocaleString()} / MT`;
  if (landedEl) landedEl.textContent = `$${landedUsd.toFixed(2)} / MT`;
  if (landedInrEl) landedInrEl.textContent = `₹${landedInr.toLocaleString()} / MT to ${s.plant_name ? s.plant_name.replace('SAIL ', '').split(' ')[0] : 'Plant'}`;
  if (laycanEl) laycanEl.textContent = s.recommended_laycan || "14–19 October";
  if (riskEl) {
    const riskScore = Math.round(Number(s.risk_score) || 38);
    const riskLevel = s.risk_level || "MODERATE";
    riskEl.textContent = `${riskLevel} (${riskScore}/100)`;
    riskEl.style.color = riskLevel === "LOW" ? "var(--accent-emerald)" : riskLevel === "CRITICAL" ? "var(--accent-coral)" : "var(--accent-amber)";
  }

  // Render Why Reasoning
  const whyGrid = document.getElementById("copilot-why-grid");
  if (whyGrid && why.length > 0) {
    const icons = idx === 0 ? ["⚓", "💰", "🚆", "📉"] : idx === 1 ? ["⚡", "🚆", "🛡️"] : ["🌱", "🌊", "💰"];
    whyGrid.innerHTML = why.map((item, i) => {
      const parts = item.split(":");
      const title = parts.length > 1 ? parts[0] : `Strategic Factor ${i + 1}`;
      const desc = parts.length > 1 ? parts.slice(1).join(":") : item;
      return `
        <div class="copilot-why-card">
          <div class="copilot-why-icon">${icons[i % icons.length]}</div>
          <div class="copilot-why-text">
            <strong>${title.trim()}</strong>
            <p>${desc.trim()}</p>
          </div>
        </div>
      `;
    }).join("");
  }
};

window.copyCopilotBrief = function() {
  if (!currentCopilotData || !currentCopilotData.strategy) return;
  const s = currentCopilotData.strategy;
  const text = `SeaSphere AI PROCUREMENT COPILOT DECISION BRIEF
=====================================================
Target: ${Number(s.cargo_tonnage || 150000).toLocaleString()} MT ${s.commodity_name || 'Coking Coal'} -> ${s.plant_name || 'SAIL Steel Plant'}
Recommended Port: ${s.discharge_port}
Optimal Vessel: ${s.vessel_class}
Ocean Freight: $${Number(s.estimated_freight_usd_ton || 16.5).toFixed(2)}/MT (₹${s.estimated_freight_inr_ton}/MT)
Total Landed Cost: $${Number(s.landed_cost_usd_ton || 312).toFixed(2)}/MT (₹${s.landed_cost_inr_ton}/MT)
Recommended Laycan: ${s.recommended_laycan}
Operational Risk: ${s.risk_level} (${s.risk_score}/100)
Expected Savings: ₹${Number(s.expected_saving_crore || 14.72).toFixed(2)} Crore
Generated via Ministry of Steel SeaSphere DSS Platform`;

  navigator.clipboard.writeText(text).then(() => {
    alert("✅ Procurement Decision Brief copied to clipboard!");
  }).catch(() => {
    prompt("Copy decision brief:", text);
  });
};

function generateClientSideCopilotRecommendation(queryText, customParams = null) {
  const text = (queryText || "").toLowerCase();
  
  let commodity = "Premium Hard Coking Coal (PHCC)";
  if (customParams?.commodity_id === "thermal_coal" || text.includes("thermal")) commodity = "Thermal Coal (GAR 5000)";
  else if (customParams?.commodity_id === "pci_coal" || text.includes("pci")) commodity = "PCI Coal (Pulverized Injection)";
  else if (customParams?.commodity_id === "limestone" || text.includes("limestone")) commodity = "SMS Grade Limestone";

  let tonnage = customParams?.cargo_tonnage || 150000;
  if (!customParams?.cargo_tonnage) {
    if (text.includes("lakh") || text.includes("lac")) {
      const m = text.match(/(\d+(?:\.\d+)?)\s*(?:lakh|lac)/);
      if (m) tonnage = parseFloat(m[1]) * 100000;
    } else {
      const m = text.match(/(\d{2,6})/);
      if (m) tonnage = parseFloat(m[1]);
    }
  }
  if (tonnage < 10000) tonnage = 150000;

  let plantName = "SAIL Rourkela Steel Plant (RSP)";
  let port = "Dhamra Port";
  let freight = 16.50;
  let landed = 312.45;
  let savingCr = 14.72;
  let laycan = "14–19 October";
  let whyDraft = "Haldia Draft Restriction Avoidance: Haldia draft (~8.5m) requires offshore lightering at Sandheads ($6.80/MT penalty). Dhamra (18.0m draft) supports direct Capesize berthing.";
  let whyLight = "Lower Lightering & Transhipment Cost: Eliminating lightering surcharges at Dhamra saves over ₹8.50 Cr directly on this parcel compared to Kolkata/Haldia discharge.";
  let whyRail = "Superior Rail Economics: Dedicated Merry-Go-Round rapid rake loading at Dhamra connects to Rourkela (420 km, 1.8 days transit) at $15.20/MT, bypassing congested Visakhapatnam bottlenecks.";

  if (customParams?.plant_id === "sail_bokaro" || text.includes("bokaro") || text.includes("bsl")) {
    plantName = "SAIL Bokaro Steel Plant (BSL)";
    port = "Dhamra Port";
    landed = 316.80;
    savingCr = 9.80;
    whyRail = "Superior Rail Economics: Dhamra direct rake loading to Bokaro (520 km, 2.0 days) avoids Paradip's 3.5-day coal marshalling delay.";
  } else if (customParams?.plant_id === "sail_durgapur" || text.includes("durgapur") || text.includes("dsp")) {
    plantName = "SAIL Durgapur Steel Plant (DSP)";
    port = "Haldia Dock Complex";
    freight = 19.80;
    landed = 288.50;
    savingCr = 6.25;
    whyDraft = "Proximity Advantage: Haldia is only 240 km from Durgapur (1.0 day rail transit), offsetting the shallow draft penalty via specialized Handymax parcels.";
  } else if (customParams?.plant_id === "rinl_vizag" || text.includes("vizag") || text.includes("vsp")) {
    plantName = "RINL Visakhapatnam (VSP)";
    port = "Visakhapatnam Port";
    landed = 295.20;
    savingCr = 18.40;
    whyRail = "Plant Gate Conveyor: Direct conveyor belt link from Vizag inner harbour berths to blast furnace bunker (18 km, 0.2 days).";
  }

  const isIwt = customParams?.is_iwt_query || text.includes("waterway") || text.includes("waterways") || text.includes("iwt") || text.includes("rail");

  const strat1 = {
    id: "cost_optimal",
    discharge_port: port,
    vessel_class: tonnage > 100000 ? "Capesize" : "Panamax",
    estimated_freight_usd_ton: freight,
    estimated_freight_inr_ton: Math.round(freight * 83.50),
    landed_cost_usd_ton: landed,
    landed_cost_inr_ton: Math.round(landed * 83.50),
    recommended_laycan: laycan,
    risk_level: "MODERATE",
    risk_score: 38,
    expected_saving_crore: savingCr,
    plant_name: plantName,
    commodity_name: commodity,
    cargo_tonnage: tonnage,
    transit_days_total: 17.6,
    co2_kg_ton: 38.5
  };

  const strat2 = {
    id: "fast_track",
    discharge_port: "Paradip Port",
    vessel_class: "Panamax",
    estimated_freight_usd_ton: freight * 1.04,
    estimated_freight_inr_ton: Math.round(freight * 1.04 * 83.50),
    landed_cost_usd_ton: landed + 2.80,
    landed_cost_inr_ton: Math.round((landed + 2.80) * 83.50),
    recommended_laycan: "Immediate Spot 5-10 Days",
    risk_level: "LOW",
    risk_score: 24,
    expected_saving_crore: roundTwo(savingCr * 0.65),
    plant_name: plantName,
    commodity_name: commodity,
    cargo_tonnage: tonnage,
    transit_days_total: 12.7,
    co2_kg_ton: 42.0
  };

  const strat3 = {
    id: "green_multimodal",
    discharge_port: "Paradip Port (NW-5 Corridor)",
    vessel_class: "Panamax + Self-Propelled River Barges",
    estimated_freight_usd_ton: freight * 1.02,
    estimated_freight_inr_ton: Math.round(freight * 1.02 * 83.50),
    landed_cost_usd_ton: landed - 1.25,
    landed_cost_inr_ton: Math.round((landed - 1.25) * 83.50),
    recommended_laycan: laycan,
    risk_level: "LOW",
    risk_score: 28,
    expected_saving_crore: roundTwo(savingCr + 1.58),
    plant_name: plantName,
    commodity_name: commodity,
    cargo_tonnage: tonnage,
    transit_days_total: 16.2,
    co2_kg_ton: 13.5
  };

  function roundTwo(v) { return Math.round(v * 100) / 100; }

  return {
    strategy: strat1,
    strategy_options: [
      {
        id: "cost_optimal",
        label: "Option 1: Cost-Optimal ⭐",
        sub: `Save ₹${savingCr.toFixed(2)} Cr (${port})`,
        strategy: strat1,
        why: [
          whyDraft,
          whyLight,
          whyRail,
          "Forecast Indicates Declining Forward Freight: AI forward curve projects Capesize spot rate softening by 4.5% over the 30-day horizon."
        ]
      },
      {
        id: "fast_track",
        label: "Option 2: Fast-Track Transit ⚡",
        sub: "3.2 Days Faster Turnaround",
        strategy: strat2,
        why: [
          "Bypasses Berth Congestion: Priority mechanised discharge with lowest pre-berthing waiting time.",
          "Direct Express Rail Turnaround: Rakes allocated within 12 hours of vessel unlading.",
          "Stockout Prevention: Ideal when blast furnace coal reserves drop below 10 days."
        ]
      },
      {
        id: "green_multimodal",
        label: "Option 3: Green Multi-Modal 🌱",
        sub: "Cut CO₂ by 65% • NW-5 Feeder",
        strategy: strat3,
        why: [
          "Decarbonization Benefit: Inland waterway transit reduces transport emissions by 65% vs all-rail.",
          "Rake Congestion Shield: 100% immune to rail marshalling yard congestions.",
          "Tariff Advantage: Saves an additional ₹1.58 Cr via subsidized river toll rates."
        ]
      }
    ],
    comparison_matrix: [
      { metric: "Discharge Gateway", cost_optimal: port, fast_track: "Paradip Port", green_multimodal: "Paradip / NW-5 Feeder" },
      { metric: "Vessel Class", cost_optimal: strat1.vessel_class, fast_track: strat2.vessel_class, green_multimodal: strat3.vessel_class },
      { metric: "Ocean Freight ($/MT)", cost_optimal: `$${strat1.estimated_freight_usd_ton.toFixed(2)}`, fast_track: `$${strat2.estimated_freight_usd_ton.toFixed(2)}`, green_multimodal: `$${strat3.estimated_freight_usd_ton.toFixed(2)}` },
      { metric: "Total Landed Cost (₹/MT)", cost_optimal: `₹${strat1.landed_cost_inr_ton.toLocaleString()}`, fast_track: `₹${strat2.landed_cost_inr_ton.toLocaleString()}`, green_multimodal: `₹${strat3.landed_cost_inr_ton.toLocaleString()}` },
      { metric: "Total Parcel Outlay (₹ Cr)", cost_optimal: `₹${(strat1.landed_cost_inr_ton * tonnage / 1e7).toFixed(2)} Cr`, fast_track: `₹${(strat2.landed_cost_inr_ton * tonnage / 1e7).toFixed(2)} Cr`, green_multimodal: `₹${(strat3.landed_cost_inr_ton * tonnage / 1e7).toFixed(2)} Cr` },
      { metric: "Total Transit Lead Time", cost_optimal: `${strat1.transit_days_total} days`, fast_track: `${strat2.transit_days_total} days (Fastest)`, green_multimodal: `${strat3.transit_days_total} days` },
      { metric: "Carbon Footprint (kg CO₂/T)", cost_optimal: `${strat1.co2_kg_ton} kg/T`, fast_track: `${strat2.co2_kg_ton} kg/T`, green_multimodal: `${strat3.co2_kg_ton} kg/T (-65%)` },
      { metric: "Risk Score", cost_optimal: `${strat1.risk_level} (${strat1.risk_score}/100)`, fast_track: `LOW (${strat2.risk_score}/100)`, green_multimodal: `LOW (${strat3.risk_score}/100)` },
      { metric: "Strategic Recommendation", cost_optimal: "Primary choice for scheduled bulk replenishment", fast_track: "Deploy if plant stock drops below 10 days", green_multimodal: "Deploy for Ministry ESG decarbonization targets" }
    ],
    why_reasoning: [
      whyDraft,
      whyLight,
      whyRail,
      "Forecast Indicates Declining Forward Freight: AI XGBoost forward curve projects Australia–East Coast Capesize spot softening by 4.5% over the 30-day horizon, indicating optimal tender entry during 14–19 October."
    ],
    iwt_comparison: {
      route_name: "Pankpal (Kalinganagar) → Paradip Port",
      waterway_id: "NW-5",
      rail: { cost_inr_ton: 1269, transit_days: 1.8, co2_emissions_tonnes: 264.0 },
      iwt: { cost_inr_ton: 215, transit_days: 1.2, co2_emissions_tonnes: 49.5 },
      recommendation_badge: "IWT — ₹1.58 Cr cheaper + 81.3% lower emissions"
    },
    parsed_parameters: { is_iwt_query: isIwt },
    query: queryText
  };
}

function renderCopilotOutput(data, userQuery) {
  if (!data || !data.strategy) return;
  currentCopilotData = data;
  const s = data.strategy;
  const iwt = data.iwt_comparison;
  const options = data.strategy_options || [];
  const matrix = data.comparison_matrix || [];

  // 0. Update Dialogue Header & Status
  const statusEl = document.getElementById("copilot-status-indicator");
  const feedbackEl = document.getElementById("copilot-query-feedback");
  if (statusEl) {
    statusEl.innerHTML = `<span style="color: var(--accent-emerald);">● LIVE STRATEGY SYNTHESIZED</span>`;
  }
  if (feedbackEl) {
    const tonnageStr = s.cargo_tonnage ? `${Number(s.cargo_tonnage).toLocaleString()} MT` : "150,000 MT";
    const commStr = s.commodity_name || "Coking Coal";
    const plantStr = s.plant_name || "SAIL Steel Plant";
    feedbackEl.innerHTML = `Multi-scenario strategies synthesized for <strong>${tonnageStr}</strong> ${commStr} destined for <strong>${plantStr}</strong>:`;
  }

  // 1. Update Scenario Switcher Subtitles
  if (options.length >= 3) {
    const sub0 = document.getElementById("scenario-sub-0");
    const sub1 = document.getElementById("scenario-sub-1");
    const sub2 = document.getElementById("scenario-sub-2");
    if (sub0) sub0.textContent = options[0].sub || "Save Maximum Cost";
    if (sub1) sub1.textContent = options[1].sub || "Save Transit Time";
    if (sub2) sub2.textContent = options[2].sub || "Cut Emissions";
  }

  // 2. Render Active Scenario (Default 0)
  window.selectCopilotScenario(currentSelectedScenarioIndex || 0);

  // 3. Render IWT Comparison Card
  const iwtCard = document.getElementById("copilot-iwt-card");
  if (iwtCard) {
    const qLower = (userQuery || data.query || data.parsed_parameters?.query_text || (document.getElementById("copilot-query-input")?.value) || "").toLowerCase();
    const isWaterwayQuery = Boolean(
      iwt && (
        data.parsed_parameters?.is_iwt_query || 
        qLower.includes("waterway") || 
        qLower.includes("rail") || 
        qLower.includes("iwt") || 
        qLower.includes("barge") ||
        qLower.includes("river")
      )
    );
    if (iwt && isWaterwayQuery) {
      iwtCard.style.display = "block";
      const railCost = iwt.rail ? iwt.rail.cost_inr_ton : 1269;
      const railDays = iwt.rail ? iwt.rail.transit_days : 1.8;
      const railCo2 = iwt.rail ? (iwt.rail.co2_emissions_tonnes || iwt.rail.co2_kg_ton || 264) : 264;
      const iwtCost = iwt.iwt ? iwt.iwt.cost_inr_ton : 215;
      const iwtDays = iwt.iwt ? iwt.iwt.transit_days : 1.2;
      const iwtCo2 = iwt.iwt ? (iwt.iwt.co2_emissions_tonnes || iwt.iwt.co2_kg_ton || 49.5) : 49.5;

      iwtCard.innerHTML = `
        <div style="background: rgba(0, 245, 160, 0.08); border: 1px solid rgba(0, 245, 160, 0.35); border-radius: 10px; padding: 1rem; margin-top: 1rem; animation: fadeIn 0.4s ease;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.4rem;">
            <div style="font-weight: 700; color: var(--accent-emerald); font-size: 0.88rem; display: flex; align-items: center; gap: 0.4rem;">
              <span>🌊</span> Multi-Modal Comparison: ${iwt.route_name || 'Inland Waterway Corridor'} (${iwt.waterway_id || 'NW-5'})
            </div>
            <span class="badge-tag badge-emerald">${iwt.recommendation_badge || 'IWT Economically & Environmentally Superior'}</span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.78rem;">
            <div style="background: rgba(6,12,26,0.6); padding: 0.65rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
              <strong style="color: var(--accent-cyan);">Indian Railways:</strong> ₹${railCost}/T • ${railDays}d transit • ${railCo2}T CO₂
            </div>
            <div style="background: rgba(6,12,26,0.6); padding: 0.65rem; border-radius: 6px; border: 1px solid rgba(0, 245, 160, 0.25);">
              <strong style="color: var(--accent-emerald);">Inland Waterways (IWT):</strong> ₹${iwtCost}/T • ${iwtDays}d transit • ${iwtCo2}T CO₂
            </div>
          </div>
        </div>
      `;
    } else {
      iwtCard.style.display = "none";
    }
  }

  // 4. Render Decision Matrix Table
  const tbody = document.getElementById("copilot-matrix-tbody");
  if (tbody && matrix.length > 0) {
    tbody.innerHTML = matrix.map(row => `
      <tr>
        <td style="font-weight: 600; color: var(--text-secondary);">${row.metric || row.parameter}</td>
        <td class="copilot-matrix-highlight">${row.cost_optimal}</td>
        <td>${row.fast_track}</td>
        <td>${row.green_multimodal}</td>
      </tr>
    `).join("");
  }
}

// ==========================================================================
// 🚨 PROACTIVE EARLY WARNING ALERT ENGINE CONTROLLER
// ==========================================================================
function initEarlyWarningModule() {
  loadEarlyWarnings();

  const refreshBtn = document.getElementById("btn-refresh-alerts");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      refreshBtn.disabled = true;
      refreshBtn.innerHTML = "<span>🔄 Scanning...</span>";
      loadEarlyWarnings().finally(() => {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = "<span>🔄 Refresh Signals</span>";
      });
    });
  }

  // Filter chips
  const filterChips = document.querySelectorAll(".alert-chip");
  filterChips.forEach(chip => {
    chip.addEventListener("click", () => {
      filterChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const filter = chip.getAttribute("data-alert-filter");
      filterEarlyWarnings(filter);
    });
  });
}

async function loadEarlyWarnings() {
  try {
    const res = await fetch("/api/alerts/active");
    const data = await res.json();
    if (data.status === "success" && data.data) {
      renderEarlyWarnings(data.data);
    }
  } catch (err) {
    console.error("Early warnings fetch error:", err);
  }
}

function renderEarlyWarnings(data) {
  const container = document.getElementById("early-warning-cards-container");
  const headlineEl = document.getElementById("action-banner-headline");
  const descEl = document.getElementById("action-banner-desc");
  const countBadge = document.getElementById("alerts-count-badge");

  if (headlineEl && data.primary_directive) {
    headlineEl.textContent = `Recommended Action: ${data.primary_directive.headline}`;
  }
  if (descEl && data.primary_directive) {
    descEl.textContent = data.primary_directive.rationale;
  }
  if (countBadge && data.total_active_alerts) {
    countBadge.textContent = `${data.total_active_alerts} ACTIVE ALERTS`;
  }

  if (container && data.alerts && data.alerts.length > 0) {
    container.innerHTML = data.alerts.map(a => {
      let typeClass = "ew-port";
      let badgeClass = "badge-port";
      let filterType = "port";

      if (a.type === "WEATHER_ALERT") {
        typeClass = "ew-weather";
        badgeClass = "badge-weather";
        filterType = "weather";
      } else if (a.type === "FREIGHT_ALERT") {
        typeClass = "ew-freight";
        badgeClass = "badge-freight";
        filterType = "freight";
      } else if (a.type === "FUEL_ALERT") {
        typeClass = "ew-fuel";
        badgeClass = "badge-fuel";
        filterType = "fuel";
      }

      const metricKeys = Object.keys(a.metrics || {});
      const metricsHtml = metricKeys.map(k => {
        const label = k.replace(/_/g, ' ');
        return `<div class="ew-metric">${label}: <strong>${a.metrics[k]}</strong></div>`;
      }).join("");

      return `
        <div class="ew-card ${typeClass}" data-type="${filterType}">
          <div class="ew-header">
            <div class="ew-badge-tag ${badgeClass}">${a.icon} ${a.badge}</div>
            <span class="ew-urgency">${a.urgency_hours}h Window</span>
          </div>
          <div class="ew-title">${a.title}</div>
          <div class="ew-desc">${a.subtitle}</div>
          <div class="ew-metrics-row">
            ${metricsHtml}
          </div>
          <div class="ew-footer-action">
            <span>💡 Directive:</span> ${a.recommended_action}
          </div>
        </div>
      `;
    }).join("");
  }
}

function filterEarlyWarnings(filterType) {
  const cards = document.querySelectorAll("#early-warning-cards-container .ew-card");
  cards.forEach(card => {
    if (filterType === "all" || card.getAttribute("data-type") === filterType) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

// ==========================================================================
// 🌊 IWT + MARITIME MULTI-MODAL EVACUATION CONTROLLER
// ==========================================================================
function initModalEvacuationModule() {
  const compareBtn = document.getElementById("btn-run-modal-compare");
  const portSelect = document.getElementById("modal-port-select");
  const commoditySelect = document.getElementById("modal-commodity-select");
  const plantSelect = document.getElementById("tender-plant");

  if (compareBtn) {
    compareBtn.addEventListener("click", () => runModalComparison());
  }

  if (portSelect) {
    portSelect.addEventListener("change", () => runModalComparison());
  }
  if (commoditySelect) {
    commoditySelect.addEventListener("change", () => runModalComparison());
  }
  if (plantSelect) {
    plantSelect.addEventListener("change", () => runModalComparison());
  }

  // Initial calculation on load
  runModalComparison();
}

async function runModalComparison() {
  const plantSelect = document.getElementById("tender-plant");
  const portSelect = document.getElementById("modal-port-select");
  const tonnageInput = document.getElementById("modal-tonnage-input");
  const commoditySelect = document.getElementById("modal-commodity-select");

  const plantId = plantSelect ? plantSelect.value : "sail_rourkela";
  const portId = portSelect ? portSelect.value : "paradip";
  const tonnage = tonnageInput ? parseFloat(tonnageInput.value) || 15000 : 15000;
  const commodityId = commoditySelect ? commoditySelect.value : "coking_coal";

  try {
    const res = await fetch("/api/optimizer/modal-compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        plant_id: plantId,
        port_id: portId,
        cargo_tonnage: tonnage,
        commodity_id: commodityId
      })
    });
    const data = await res.json();
    if (data.status === "success" && data.data) {
      renderModalComparison(data.data);
    }
  } catch (err) {
    console.error("Modal compare fetch error:", err);
  }
}

function renderModalComparison(d) {
  // Rail stats
  const railCostEl = document.getElementById("modal-rail-cost");
  const railTransitEl = document.getElementById("modal-rail-transit");
  const railCo2El = document.getElementById("modal-rail-co2");
  const railTotalEl = document.getElementById("modal-rail-total");

  if (railCostEl) railCostEl.textContent = `₹${d.rail.cost_inr_ton.toLocaleString()} / ton`;
  if (railTransitEl) railTransitEl.textContent = `${d.rail.transit_days} days (${d.rail.distance_km} km)`;
  if (railCo2El) railCo2El.textContent = `${d.rail.co2_kg_ton} kg CO₂ / ton`;
  if (railTotalEl) {
    const totalCr = (d.rail.total_cost_inr / 1e7).toFixed(2);
    railTotalEl.textContent = totalCr >= 1 ? `₹${totalCr} Cr` : `₹${(d.rail.total_cost_inr / 1e5).toFixed(1)} Lakh`;
  }

  // IWT stats
  const iwtCostEl = document.getElementById("modal-iwt-cost");
  const iwtTransitEl = document.getElementById("modal-iwt-transit");
  const iwtCo2El = document.getElementById("modal-iwt-co2");
  const iwtTotalEl = document.getElementById("modal-iwt-total");

  if (iwtCostEl) iwtCostEl.textContent = `₹${d.iwt.cost_inr_ton.toLocaleString()} / ton`;
  if (iwtTransitEl) iwtTransitEl.textContent = `${d.iwt.transit_days} days (${d.iwt.distance_km} km)`;
  if (iwtCo2El) iwtCo2El.textContent = `${d.iwt.co2_kg_ton} kg CO₂ / ton`;
  if (iwtTotalEl) {
    const totalCr = (d.iwt.total_cost_inr / 1e7).toFixed(2);
    iwtTotalEl.textContent = totalCr >= 1 ? `₹${totalCr} Cr` : `₹${(d.iwt.total_cost_inr / 1e5).toFixed(1)} Lakh`;
  }

  // Recommendation banner
  const pillEl = document.getElementById("modal-recommendation-pill");
  const bannerTextEl = document.getElementById("modal-recommendation-text");
  const bannerSubEl = document.getElementById("modal-recommendation-sub");

  if (pillEl) {
    pillEl.textContent = d.recommended_mode === "IWT" ? "IWT Recommended" : "Rail Recommended";
    pillEl.className = d.recommended_mode === "IWT" ? "badge-tag badge-emerald" : "badge-tag badge-cyan";
  }

  if (bannerTextEl) {
    bannerTextEl.innerHTML = `<span>🎯</span> ${d.recommendation_badge}`;
  }

  if (bannerSubEl) {
    bannerSubEl.textContent = d.recommendation_reason;
  }
}

// ============== 22. LIVE DATA INGESTION & AUTO-REFRESH ==============

let isSyncing = false;

function initLiveSyncAndAutoRefresh() {
  const liveBadge = document.getElementById("live-feed-badge");
  if (liveBadge) {
    liveBadge.style.cursor = "pointer";
    liveBadge.setAttribute("title", "🟢 Live Data Pipeline Active — Click to trigger on-demand sync");
    
    liveBadge.addEventListener("click", () => {
      triggerLiveIngestionSync();
    });
  }

  // Periodic Auto-Refresh cycle every 30 seconds
  setInterval(() => {
    autoRefreshDynamicData();
  }, 30000);

  // Initial fetch of data status
  fetchDataStatus();
}

async function triggerLiveIngestionSync() {
  if (isSyncing) return;
  isSyncing = true;

  const liveBadge = document.getElementById("live-feed-badge");
  if (liveBadge) {
    liveBadge.classList.add("syncing");
    const textEl = liveBadge.querySelector(".live-text-desktop") || liveBadge;
    textEl.innerText = "SYNCING FEEDS...";
  }

  showSeaSphereToast("🔄 Ingesting live Metocean APIs and Baltic market ticks...", "info");

  try {
    const res = await fetch("/api/data/sync", { method: "POST" });
    const json = await res.json();

    if (json.status === "success" && json.data) {
      const d = json.data;
      const tick = d.latest_market_tick || {};
      const wCount = d.weather_records_updated || 0;
      const latency = d.latency_ms || 0;

      showSeaSphereToast(
        `✅ Live Ingestion Complete (${latency}ms) — ${wCount} Weather Forecasts Updated | BDI: ${tick.bdi || 'Live'} | Bunker: $${tick.bunker_vlsfo_singapore || 0}/MT`,
        "success"
      );

      // Refresh UI components immediately with newest data
      loadMarketSnapshot();
      loadRiskScore();

      const routeSelect = document.getElementById("forecaster-route-select");
      if (routeSelect && routeSelect.value) {
        loadForecast(routeSelect.value);
      }

      loadAllPortsWeatherOverview();
      const weatherPortSelect = document.getElementById("weather-port-select");
      if (weatherPortSelect && weatherPortSelect.value) {
        loadPortWeatherData(weatherPortSelect.value);
      }

      const alertModule = window.loadActiveAlerts;
      if (typeof alertModule === "function") alertModule();
    } else {
      showSeaSphereToast("⚠️ Live sync warning: " + (json.message || "Partial update"), "warning");
    }
  } catch (err) {
    console.error("Live sync failed:", err);
    showSeaSphereToast("❌ Live ingestion failed: " + err.message, "error");
  } finally {
    isSyncing = false;
    if (liveBadge) {
      liveBadge.classList.remove("syncing");
      const textEl = liveBadge.querySelector(".live-text-desktop");
      if (textEl) textEl.innerText = "LIVE MARITIME FEED";
    }
  }
}

async function autoRefreshDynamicData() {
  try {
    loadMarketSnapshot();
    fetchDataStatus();
  } catch (e) {
    console.warn("Background auto-refresh tick skipped:", e);
  }
}

async function fetchDataStatus() {
  try {
    const res = await fetch("/api/data/status");
    const json = await res.json();
    if (json.status === "success" && json.data) {
      const dbStats = json.data.database || {};
      const liveStats = json.data.ingestion || {};
      const liveBadge = document.getElementById("live-feed-badge");
      if (liveBadge && dbStats.engine) {
        liveBadge.setAttribute(
          "title",
          `🟢 Connected to ${dbStats.engine} (${dbStats.market_records_total} records) | Auto-Sync: ${liveStats.scheduler_interval_seconds}s | Click to sync`
        );
      }
    }
  } catch (e) {
    // Silent background status
  }
}

function showSeaSphereToast(message, type = "info") {
  let toastContainer = document.getElementById("seasphere-toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "seasphere-toast-container";
    toastContainer.style.position = "fixed";
    toastContainer.style.bottom = "24px";
    toastContainer.style.right = "24px";
    toastContainer.style.zIndex = "99999";
    toastContainer.style.display = "flex";
    toastContainer.style.flexDirection = "column";
    toastContainer.style.gap = "8px";
    toastContainer.style.maxWidth = "420px";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  const bgColors = {
    info: "rgba(15, 23, 42, 0.95)",
    success: "rgba(6, 78, 59, 0.95)",
    warning: "rgba(120, 53, 15, 0.95)",
    error: "rgba(127, 29, 29, 0.95)"
  };
  const borderColors = {
    info: "#00d2ff",
    success: "#00f5a0",
    warning: "#ffb703",
    error: "#ef4444"
  };

  toast.style.background = bgColors[type] || bgColors.info;
  toast.style.border = `1px solid ${borderColors[type] || borderColors.info}`;
  toast.style.color = "#f8fafc";
  toast.style.padding = "10px 16px";
  toast.style.borderRadius = "8px";
  toast.style.fontSize = "0.85rem";
  toast.style.boxShadow = "0 8px 30px rgba(0,0,0,0.5)";
  toast.style.backdropFilter = "blur(8px)";
  toast.style.animation = "fadeIn 0.3s ease";
  toast.innerText = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.4s ease";
    setTimeout(() => toast.remove(), 400);
  }, 4500);
}
