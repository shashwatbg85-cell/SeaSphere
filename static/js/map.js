/**
 * Interactive Maritime Shipping Lanes & Port Infrastructure Map (Leaflet.js)
 * Visualizes overseas bulk origins, East Coast India discharge ports, and great-circle sailing corridors.
 */

let mapInstance = null;
let routePolylines = {};
let portMarkers = {};
let animatedVesselMarker = null;
let animationFrameId = null;

// Route definitions connecting overseas hubs to East Coast ports
const TRADE_LANES = {
  "aus_paradip": {
    name: "Australia (Hay Point) -> Paradip Port",
    commodity: "Coking Coal",
    vessel: "Capesize (175k DWT)",
    color: "#00d2ff",
    coords: [
      [-21.2833, 149.3000],  // Hay Point
      [-10.5000, 142.2000],  // Torres Strait / Coral Sea
      [-8.5000, 115.5000],   // Lombok Strait
      [5.5000, 95.0000],     // Malacca / North Sumatra
      [15.0000, 89.0000],    // Bay of Bengal South
      [20.2644, 86.6715]     // Paradip Port
    ]
  },
  "aus_vizag": {
    name: "Australia (Gladstone) -> Visakhapatnam",
    commodity: "Coking Coal",
    vessel: "Capesize (175k DWT)",
    color: "#38bdf8",
    coords: [
      [-23.8427, 151.2567],  // Gladstone
      [-11.0000, 143.0000],  // Coral Sea
      [-8.5000, 115.5000],   // Lombok Strait
      [6.0000, 93.0000],     // Andaman Sea
      [17.6868, 83.2185]     // Vizag Port
    ]
  },
  "indo_paradip": {
    name: "Indonesia (Taboneo) -> Paradip",
    commodity: "Thermal / PCI Coal",
    vessel: "Panamax (75k DWT)",
    color: "#00f5a0",
    coords: [
      [-3.7500, 114.4500],   // Taboneo Anchorage (Kalimantan)
      [-5.8000, 106.0000],   // Sunda Strait
      [5.8000, 95.3000],     // Malacca Strait Northwest
      [14.0000, 88.0000],    // Central Bay of Bengal
      [20.2644, 86.6715]     // Paradip
    ]
  },
  "rsa_vizag": {
    name: "South Africa (Richards Bay) -> Vizag",
    commodity: "Steam / Coking Coal",
    vessel: "Capesize (175k DWT)",
    color: "#ffb703",
    coords: [
      [-28.8000, 32.0833],   // Richards Bay
      [-20.0000, 45.0000],   // Mozambique Channel
      [-5.0000, 60.0000],    // Mid Indian Ocean
      [6.0000, 78.0000],     // South of Sri Lanka (Dondra Head)
      [17.6868, 83.2185]     // Vizag
    ]
  },
  "usa_paradip": {
    name: "USA (Hampton Roads) -> Paradip via Cape",
    commodity: "Met Coal (Appalachian)",
    vessel: "Capesize (175k DWT)",
    color: "#f43f5e",
    coords: [
      [36.9500, -76.3333],   // Norfolk
      [25.0000, -50.0000],   // Mid North Atlantic
      [0.0000, -25.0000],    // Equator Atlantic
      [-34.5000, 18.5000],   // Cape of Good Hope
      [-25.0000, 50.0000],   // South Indian Ocean
      [5.5000, 80.5000],     // Sri Lanka
      [20.2644, 86.6715]     // Paradip
    ]
  },
  "uae_haldia": {
    name: "UAE (Fujairah) -> Haldia",
    commodity: "Limestone / Dolomite Flux",
    vessel: "Supramax (58k DWT)",
    color: "#a855f7",
    coords: [
      [25.1800, 56.3600],    // Fujairah
      [20.0000, 65.0000],    // Arabian Sea
      [7.5000, 77.5000],     // Cape Comorin
      [6.0000, 81.0000],     // South Sri Lanka
      [22.0232, 88.0645]     // Haldia Dock
    ]
  }
};

function initMaritimeMap() {
  const mapElement = document.getElementById("leaflet-map");
  if (!mapElement) return;

  // Center on Indian Ocean / Bay of Bengal
  mapInstance = L.map("leaflet-map", {
    center: [12.0, 85.0],
    zoom: 3,
    minZoom: 2,
    maxZoom: 10,
    zoomControl: true
  });

  // Dark Maritime Basemap Tile Layer (Free, No API Key Required, Clean Dark Aesthetic)
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
    attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16
  }).addTo(mapInstance);

  // Subtle Country & Maritime Reference Layer (No API Key Required)
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", {
    attribution: '',
    maxZoom: 16,
    opacity: 0.85
  }).addTo(mapInstance);

  // Load Port and Origin Markers
  loadPortMarkers();
  loadTradeLanePolylines();
}

function loadPortMarkers() {
  Promise.all([
    fetch("/api/metadata/all").then(r => r.json()).catch(() => ({ status: "error" })),
    fetch("/api/weather/ports").then(r => r.json()).catch(() => ({ status: "error" }))
  ]).then(([metaRes, weatherRes]) => {
    if (metaRes.status !== "success") return;
    const metadata = metaRes.data;
    const weatherMap = {};
    if (weatherRes.status === "success" && Array.isArray(weatherRes.data)) {
      weatherRes.data.forEach(w => {
        weatherMap[w.port_name.toLowerCase()] = w;
      });
    }

    // 1. Render All Indian Major Ports (West & East Coasts)
    const majorPorts = metadata.major_ports || metadata.ports;
    Object.entries(majorPorts).forEach(([id, port]) => {
      const isWestCoast = port.coast === "West Coast";
      const accentColor = isWestCoast ? "#00f5a0" : "#00d2ff";
      
      const customIcon = L.divIcon({
        className: "custom-port-marker",
        html: `
          <div style="position:relative;">
            <div style="width: 14px; height: 14px; background: ${accentColor}; border: 2px solid #ffffff; border-radius: 50%; box-shadow: 0 0 12px ${accentColor};"></div>
            <div style="position: absolute; top:-7px; left:-7px; width: 28px; height: 28px; border: 1px solid rgba(0, 210, 255, 0.4); border-radius: 50%; animation: pulse 2s infinite;"></div>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      const marker = L.marker(port.coordinates, { icon: customIcon }).addTo(mapInstance);
      const displayName = port.port || port.name;
      const throughput = port.traffic_2022_23_mt ? `${port.traffic_2022_23_mt} MT` : "Major Hub";
      const overseasPct = port.overseas_share_pct ? `${port.overseas_share_pct}%` : "76%";
      const coastalPct = port.coastal_share_pct ? `${port.coastal_share_pct}%` : "24%";
      const rankText = port.traffic_rank_2022_23 ? `#${port.traffic_rank_2022_23} in India` : "";

      // Match port weather
      let portWeather = null;
      const dLow = displayName.toLowerCase();
      for (const [wKey, wData] of Object.entries(weatherMap)) {
        if (dLow.includes(wKey) || wKey.includes(dLow)) {
          portWeather = wData;
          break;
        }
      }

      let weatherSnippet = "";
      if (portWeather && portWeather.current_weather) {
        const cw = portWeather.current_weather;
        weatherSnippet = `
          <div style="font-size: 11px; margin-top: 5px; padding: 4px 6px; background: #e0f2fe; color: #0369a1; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; font-weight: 600;">
            <span>${cw.icon || '☀️'} ${cw.condition} (${cw.temp_max}°C)</span>
            <span>💨 ${cw.wind_kmh} km/h</span>
          </div>
        `;
      }

      const popupContent = `
        <div style="color: #070d1e; font-family: sans-serif; min-width: 230px;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding-bottom: 4px;">
            <div style="font-weight: 800; font-size: 14px; color: #0077b6;">${displayName}</div>
            <span style="font-size: 10px; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-weight: 700;">${rankText}</span>
          </div>
          ${weatherSnippet}
          <div style="font-size: 11px; margin-top: 5px; color: #555;">State: <b>${port.state}</b> (${port.coast || 'Coastal'})</div>
          <div style="font-size: 11px; color: #555;">FY23 Throughput: <b style="color: #0284c7;">${throughput}</b></div>
          <div style="font-size: 11px; color: #555;">Trade Split: <b style="color: #0369a1;">${overseasPct} OS</b> / <b style="color: #b45309;">${coastalPct} CS</b></div>
          <div style="font-size: 11px; color: #555;">Max Draft: <b>${port.max_draft_meters || 14.5}m</b></div>
          <div style="font-size: 10px; margin-top: 6px; padding: 4px; background: #ecfdf5; color: #047857; border-radius: 4px; font-weight: 600;">
            ${port.description || 'Major commercial gateway under Ministry of Ports, Shipping & Waterways'}
          </div>
        </div>
      `;
      marker.bindPopup(popupContent);
      portMarkers[id] = marker;
    });

      // 2. Render Overseas Origin Hubs (Amber / Cargo Icon)
      Object.entries(metadata.origins).forEach(([id, origin]) => {
        const originIcon = L.divIcon({
          className: "custom-origin-marker",
          html: `
            <div style="width: 12px; height: 12px; background: #ffb703; border: 2px solid #ffffff; border-radius: 50%; box-shadow: 0 0 10px #ffb703;"></div>
          `,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });

        const marker = L.marker(origin.coordinates, { icon: originIcon }).addTo(mapInstance);
        const popupContent = `
          <div style="color: #070d1e; font-family: sans-serif; min-width: 200px;">
            <div style="font-weight: 800; font-size: 13px; color: #d97706; border-bottom: 1px solid #ddd; padding-bottom: 4px;">${origin.name}</div>
            <div style="font-size: 11px; margin-top: 5px; color: #555;">Country: <b>${origin.country}</b> (${origin.region})</div>
            <div style="font-size: 11px; color: #555;">Distance to Vizag: <b>${origin.distance_nm_to_vizag.toLocaleString()} NM</b></div>
            <div style="font-size: 11px; color: #555;">Sailing Time (Cape): <b>${origin.avg_sailing_days_cape} days</b></div>
          </div>
        `;
        marker.bindPopup(popupContent);
        portMarkers[id] = marker;
      });
    });
}

function loadTradeLanePolylines() {
  Object.entries(TRADE_LANES).forEach(([laneKey, lane]) => {
    const polyline = L.polyline(lane.coords, {
      color: lane.color,
      weight: 2.5,
      opacity: 0.65,
      dashArray: "6, 6"
    }).addTo(mapInstance);

    polyline.bindTooltip(`
      <div style="font-weight: 700; font-size: 12px; color: #070d1e;">${lane.name}</div>
      <div style="font-size: 10px; color: #555;">Cargo: ${lane.commodity} | Vessel: ${lane.vessel}</div>
    `);

    polyline.on("click", () => {
      highlightTradeLane(laneKey);
    });

    routePolylines[laneKey] = polyline;
  });

  // Start animated vessel on the primary Australia corridor
  startVesselAnimation(TRADE_LANES["aus_paradip"].coords);
}

function highlightTradeLane(laneKey) {
  Object.entries(routePolylines).forEach(([key, poly]) => {
    if (key === laneKey) {
      poly.setStyle({ weight: 4.5, opacity: 1.0, dashArray: null });
      if (TRADE_LANES[key]) {
        startVesselAnimation(TRADE_LANES[key].coords);
      }
    } else {
      poly.setStyle({ weight: 2.0, opacity: 0.35, dashArray: "6, 6" });
    }
  });
}

function startVesselAnimation(routeCoordinates) {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }

  if (animatedVesselMarker) {
    mapInstance.removeLayer(animatedVesselMarker);
  }

  const shipIcon = L.divIcon({
    className: "animated-ship-marker",
    html: `
      <div style="width: 22px; height: 22px; background: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px #00f5a0; border: 2px solid #00f5a0;">
        <span style="font-size: 11px;">🚢</span>
      </div>
    `,
    iconSize: [22, 22],
    iconAnchor: [11, 11]
  });

  animatedVesselMarker = L.marker(routeCoordinates[0], { icon: shipIcon }).addTo(mapInstance);

  let progress = 0.0;
  const speed = 0.0007; // Speed of ship animation

  function animate() {
    progress += speed;
    if (progress >= 1.0) progress = 0.0;

    // Interpolate coordinate along the multi-point path
    const totalSegments = routeCoordinates.length - 1;
    const currentSegmentIndex = Math.min(Math.floor(progress * totalSegments), totalSegments - 1);
    const segmentProgress = (progress * totalSegments) - currentSegmentIndex;

    const p1 = routeCoordinates[currentSegmentIndex];
    const p2 = routeCoordinates[currentSegmentIndex + 1];

    const lat = p1[0] + (p2[0] - p1[0]) * segmentProgress;
    const lng = p1[1] + (p2[1] - p1[1]) * segmentProgress;

    animatedVesselMarker.setLatLng([lat, lng]);
    animationFrameId = requestAnimationFrame(animate);
  }

  animate();
}

window.initMaritimeMap = initMaritimeMap;
window.highlightTradeLane = highlightTradeLane;
