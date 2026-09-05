"""
Maritime Domain Knowledge Base for Indian East Coast Bulk Cargo Procurement.
Covers major global origin ports, East Coast destination ports, vessel specifications,
commodity parameters, and inland rail logistics to major Indian steel plants.
"""

# Destination Ports along East Coast of India
EAST_COAST_PORTS = {
    "paradip": {
        "id": "paradip",
        "name": "Paradip Port",
        "state": "Odisha",
        "coordinates": [20.2644, 86.6715],
        "max_draft_meters": 17.1,
        "max_dwt": 180000,
        "max_beam_meters": 45.0,
        "suitable_vessels": ["Capesize", "Kamsarmax", "Panamax", "Supramax"],
        "berth_type": "Deepwater Bulk Berths (Mechanized Coal Handling Plant)",
        "avg_waiting_days": 2.8,
        "demurrage_usd_day": 22000,
        "port_dues_usd_ton": 3.85,
        "handling_charges_usd_ton": 2.10,
        "lightering_required": False,
        "lightering_cost_usd_ton": 0.0,
        "description": "Major deep-draft hub for coking coal and thermal coal. Capesize fully laden capable."
    },
    "visakhapatnam": {
        "id": "visakhapatnam",
        "name": "Visakhapatnam Port (Vizag)",
        "state": "Andhra Pradesh",
        "coordinates": [17.6868, 83.2185],
        "max_draft_meters": 18.1,
        "max_dwt": 200000,
        "max_beam_meters": 48.0,
        "suitable_vessels": ["Capesize", "Kamsarmax", "Panamax", "Supramax"],
        "berth_type": "Outer Harbour Mechanized Iron Ore & Coal Berths",
        "avg_waiting_days": 2.2,
        "demurrage_usd_day": 24000,
        "port_dues_usd_ton": 4.10,
        "handling_charges_usd_ton": 2.30,
        "lightering_required": False,
        "lightering_cost_usd_ton": 0.0,
        "description": "Premier deep-draft port adjacent to RINL (Vizag Steel Plant). Outer harbor takes Capesize."
    },
    "haldia": {
        "id": "haldia",
        "name": "Haldia Dock Complex (SMP Kolkata)",
        "state": "West Bengal",
        "coordinates": [22.0232, 88.0645],
        "max_draft_meters": 8.5,
        "max_dwt": 55000,
        "max_beam_meters": 32.2,
        "suitable_vessels": ["Supramax", "Handymax", "Handysize"],
        "berth_type": "Riverine Lock-gate Impounded Dock",
        "avg_waiting_days": 4.5,
        "demurrage_usd_day": 18000,
        "port_dues_usd_ton": 5.20,
        "handling_charges_usd_ton": 3.40,
        "lightering_required": True,
        "lightering_cost_usd_ton": 6.80,
        "description": "Critical riverine port closest to Durgapur and IISCO. Strict draft restrictions (~8m); Capesize/Panamax require offshore lightering at Sandheads/Dhamra."
    },
    "dhamra": {
        "id": "dhamra",
        "name": "Dhamra Port",
        "state": "Odisha",
        "coordinates": [20.8333, 86.9667],
        "max_draft_meters": 18.0,
        "max_dwt": 185000,
        "max_beam_meters": 46.0,
        "suitable_vessels": ["Capesize", "Kamsarmax", "Panamax", "Supramax"],
        "berth_type": "All-Weather Deep Draft Bulk Terminal",
        "avg_waiting_days": 1.9,
        "demurrage_usd_day": 23000,
        "port_dues_usd_ton": 4.25,
        "handling_charges_usd_ton": 2.05,
        "lightering_required": False,
        "lightering_cost_usd_ton": 0.0,
        "description": "High-efficiency deep-draft private terminal with rapid rail rake loading capabilities."
    },
    "krishnapatnam": {
        "id": "krishnapatnam",
        "name": "Krishnapatnam Port",
        "state": "Andhra Pradesh",
        "coordinates": [14.2530, 80.1256],
        "max_draft_meters": 18.5,
        "max_dwt": 200000,
        "max_beam_meters": 47.0,
        "suitable_vessels": ["Capesize", "Kamsarmax", "Panamax", "Supramax"],
        "berth_type": "Deepwater Automated Bulk Terminal",
        "avg_waiting_days": 1.7,
        "demurrage_usd_day": 22500,
        "port_dues_usd_ton": 3.90,
        "handling_charges_usd_ton": 1.95,
        "lightering_required": False,
        "lightering_cost_usd_ton": 0.0,
        "description": "Deepwater automated bulk hub with direct rail links to South/Central India steel mills."
    },
    "gangavaram": {
        "id": "gangavaram",
        "name": "Gangavaram Port",
        "state": "Andhra Pradesh",
        "coordinates": [17.6200, 83.2350],
        "max_draft_meters": 21.0,
        "max_dwt": 200000,
        "max_beam_meters": 50.0,
        "suitable_vessels": ["Capesize", "Kamsarmax", "Panamax", "Supramax"],
        "berth_type": "Super-deep Bulk Berths",
        "avg_waiting_days": 2.0,
        "demurrage_usd_day": 23500,
        "port_dues_usd_ton": 4.00,
        "handling_charges_usd_ton": 2.15,
        "lightering_required": False,
        "lightering_cost_usd_ton": 0.0,
        "description": "One of India's deepest ports (21m draft) catering to heavy Capesize and Baby-Cape dry bulkers."
    }
}

# Major Global Bulk Cargo Origin Ports
ORIGIN_PORTS = {
    "hay_point": {
        "id": "hay_point",
        "name": "Hay Point / Dalrymple Bay",
        "country": "Australia",
        "region": "Queensland",
        "coordinates": [-21.2833, 149.3000],
        "commodities": ["coking_coal"],
        "distance_nm_to_vizag": 4900,
        "distance_nm_to_paradip": 5050,
        "distance_nm_to_haldia": 5150,
        "avg_sailing_days_cape": 16.5,
        "avg_sailing_days_panamax": 17.5,
        "description": "World's largest metallurgical coking coal export terminal."
    },
    "gladstone": {
        "id": "gladstone",
        "name": "Port of Gladstone",
        "country": "Australia",
        "region": "Queensland",
        "coordinates": [-23.8427, 151.2567],
        "commodities": ["coking_coal", "thermal_coal"],
        "distance_nm_to_vizag": 5050,
        "distance_nm_to_paradip": 5200,
        "distance_nm_to_haldia": 5300,
        "avg_sailing_days_cape": 17.0,
        "avg_sailing_days_panamax": 18.0,
        "description": "Major Queensland bulk coal exporting hub."
    },
    "taboneo": {
        "id": "taboneo",
        "name": "Taboneo Anchorage (Kalimantan)",
        "country": "Indonesia",
        "region": "South Kalimantan",
        "coordinates": [-3.7500, 114.4500],
        "commodities": ["thermal_coal", "pci_coal"],
        "distance_nm_to_vizag": 2100,
        "distance_nm_to_paradip": 2250,
        "distance_nm_to_haldia": 2350,
        "avg_sailing_days_cape": 7.5,
        "avg_sailing_days_panamax": 8.0,
        "description": "Key anchorage for Indonesian thermal and Pulverized Coal Injection (PCI) coals."
    },
    "richards_bay": {
        "id": "richards_bay",
        "name": "Richards Bay Coal Terminal (RBCT)",
        "country": "South Africa",
        "region": "KwaZulu-Natal",
        "coordinates": [-28.8000, 32.0833],
        "commodities": ["coking_coal", "thermal_coal"],
        "distance_nm_to_vizag": 4500,
        "distance_nm_to_paradip": 4650,
        "distance_nm_to_haldia": 4750,
        "avg_sailing_days_cape": 15.0,
        "avg_sailing_days_panamax": 16.0,
        "description": "Single largest coal export facility in Africa."
    },
    "hampton_roads": {
        "id": "hampton_roads",
        "name": "Hampton Roads / Norfolk",
        "country": "USA",
        "region": "Virginia / US East Coast",
        "coordinates": [36.9500, -76.3333],
        "commodities": ["coking_coal"],
        "distance_nm_to_vizag": 11500,
        "distance_nm_to_paradip": 11650,
        "distance_nm_to_haldia": 11750,
        "avg_sailing_days_cape": 38.0,
        "avg_sailing_days_panamax": 40.0,
        "description": "High-volatile Appalachian coking coal. Routed via Cape of Good Hope."
    },
    "taman": {
        "id": "taman",
        "name": "Port of Taman (Black Sea)",
        "country": "Russia",
        "region": "Black Sea / Azov",
        "coordinates": [45.1300, 36.6800],
        "commodities": ["coking_coal", "pci_coal", "anthracite"],
        "distance_nm_to_vizag": 5600,
        "distance_nm_to_paradip": 5750,
        "distance_nm_to_haldia": 5850,
        "avg_sailing_days_cape": 19.0,
        "avg_sailing_days_panamax": 20.0,
        "description": "Russian coal export terminal on Black Sea via Suez Canal / Bab el-Mandeb."
    },
    "fujairah": {
        "id": "fujairah",
        "name": "Port of Fujairah / Mina Saqr",
        "country": "UAE / Oman",
        "region": "Middle East",
        "coordinates": [25.1800, 56.3600],
        "commodities": ["limestone", "dolomite"],
        "distance_nm_to_vizag": 1950,
        "distance_nm_to_paradip": 2100,
        "distance_nm_to_haldia": 2200,
        "avg_sailing_days_cape": 6.8,
        "avg_sailing_days_panamax": 7.2,
        "description": "Primary overseas source of high-purity limestone and dolomite flux for steel blast furnaces."
    }
}

# Dry Bulk Vessel Categories and Technical Specifications
VESSEL_CLASSES = {
    "Capesize": {
        "dwt_range": [130000, 200000],
        "typical_dwt": 175000,
        "design_draft_meters": 17.8,
        "ballast_draft_meters": 9.5,
        "beam_meters": 45.0,
        "loa_meters": 290,
        "speed_knots_laden": 12.5,
        "speed_knots_ballast": 13.5,
        "daily_fuel_consumption_ton": 44.0,  # VLSFO
        "typical_daily_tc_rate_usd": 24500,
        "freight_cost_factor": 1.0,  # Base benchmark
        "description": "Economies of scale leader for long-haul routes (Australia/S.Africa/USA). Deep-draft only."
    },
    "Kamsarmax": {
        "dwt_range": [80000, 85000],
        "typical_dwt": 82000,
        "design_draft_meters": 14.4,
        "ballast_draft_meters": 7.5,
        "beam_meters": 32.26,
        "loa_meters": 229,
        "speed_knots_laden": 13.0,
        "speed_knots_ballast": 14.0,
        "daily_fuel_consumption_ton": 28.0,
        "typical_daily_tc_rate_usd": 16800,
        "freight_cost_factor": 1.22,
        "description": "Maximized Panamax vessel suitable for all deep ports and moderately draft-restricted berths."
    },
    "Panamax": {
        "dwt_range": [70000, 79000],
        "typical_dwt": 75000,
        "design_draft_meters": 14.0,
        "ballast_draft_meters": 7.2,
        "beam_meters": 32.2,
        "loa_meters": 225,
        "speed_knots_laden": 13.0,
        "speed_knots_ballast": 14.0,
        "daily_fuel_consumption_ton": 26.0,
        "typical_daily_tc_rate_usd": 15200,
        "freight_cost_factor": 1.28,
        "description": "Standard workhorse for global dry bulk trade."
    },
    "Supramax": {
        "dwt_range": [52000, 64000],
        "typical_dwt": 58000,
        "design_draft_meters": 12.8,
        "ballast_draft_meters": 6.8,
        "beam_meters": 32.2,
        "loa_meters": 190,
        "speed_knots_laden": 13.5,
        "speed_knots_ballast": 14.5,
        "daily_fuel_consumption_ton": 23.0,
        "typical_daily_tc_rate_usd": 13500,
        "freight_cost_factor": 1.45,
        "description": "Geared with own cranes. Can access shallow riverine ports like Haldia directly without lightering."
    }
}

# Major Steel Plants (SAIL & RINL) Inland Rail Freight Matrix
STEEL_PLANTS = {
    "sail_rourkela": {
        "id": "sail_rourkela",
        "name": "SAIL Rourkela Steel Plant (RSP)",
        "state": "Odisha",
        "annual_coking_coal_demand_mt": 3.8,
        "preferred_ports": {
            "paradip": {"distance_km": 395, "rail_freight_usd_ton": 14.50, "transit_days": 1.5},
            "dhamra": {"distance_km": 420, "rail_freight_usd_ton": 15.20, "transit_days": 1.8},
            "visakhapatnam": {"distance_km": 720, "rail_freight_usd_ton": 22.80, "transit_days": 2.8},
            "haldia": {"distance_km": 490, "rail_freight_usd_ton": 17.60, "transit_days": 2.0}
        }
    },
    "sail_bokaro": {
        "id": "sail_bokaro",
        "name": "SAIL Bokaro Steel Plant (BSL)",
        "state": "Jharkhand",
        "annual_coking_coal_demand_mt": 4.5,
        "preferred_ports": {
            "haldia": {"distance_km": 380, "rail_freight_usd_ton": 13.90, "transit_days": 1.4},
            "paradip": {"distance_km": 540, "rail_freight_usd_ton": 18.20, "transit_days": 2.1},
            "dhamra": {"distance_km": 520, "rail_freight_usd_ton": 17.80, "transit_days": 2.0},
            "visakhapatnam": {"distance_km": 870, "rail_freight_usd_ton": 26.50, "transit_days": 3.2}
        }
    },
    "sail_durgapur": {
        "id": "sail_durgapur",
        "name": "SAIL Durgapur Steel Plant (DSP)",
        "state": "West Bengal",
        "annual_coking_coal_demand_mt": 2.4,
        "preferred_ports": {
            "haldia": {"distance_km": 240, "rail_freight_usd_ton": 9.80, "transit_days": 1.0},
            "dhamra": {"distance_km": 460, "rail_freight_usd_ton": 16.40, "transit_days": 1.8},
            "paradip": {"distance_km": 510, "rail_freight_usd_ton": 17.50, "transit_days": 2.0},
            "visakhapatnam": {"distance_km": 910, "rail_freight_usd_ton": 27.20, "transit_days": 3.4}
        }
    },
    "sail_iisco": {
        "id": "sail_iisco",
        "name": "SAIL IISCO Steel Plant (Burnpur)",
        "state": "West Bengal",
        "annual_coking_coal_demand_mt": 2.2,
        "preferred_ports": {
            "haldia": {"distance_km": 280, "rail_freight_usd_ton": 11.20, "transit_days": 1.1},
            "dhamra": {"distance_km": 490, "rail_freight_usd_ton": 17.10, "transit_days": 1.9},
            "paradip": {"distance_km": 540, "rail_freight_usd_ton": 18.40, "transit_days": 2.2},
            "visakhapatnam": {"distance_km": 940, "rail_freight_usd_ton": 28.00, "transit_days": 3.5}
        }
    },
    "sail_bhilai": {
        "id": "sail_bhilai",
        "name": "SAIL Bhilai Steel Plant (BSP)",
        "state": "Chhattisgarh",
        "annual_coking_coal_demand_mt": 4.8,
        "preferred_ports": {
            "visakhapatnam": {"distance_km": 560, "rail_freight_usd_ton": 18.60, "transit_days": 2.2},
            "gangavaram": {"distance_km": 565, "rail_freight_usd_ton": 18.70, "transit_days": 2.2},
            "paradip": {"distance_km": 680, "rail_freight_usd_ton": 21.90, "transit_days": 2.6},
            "dhamra": {"distance_km": 710, "rail_freight_usd_ton": 22.80, "transit_days": 2.8}
        }
    },
    "rinl_vizag": {
        "id": "rinl_vizag",
        "name": "RINL Visakhapatnam Steel Plant (VSP)",
        "state": "Andhra Pradesh",
        "annual_coking_coal_demand_mt": 3.6,
        "preferred_ports": {
            "visakhapatnam": {"distance_km": 18, "rail_freight_usd_ton": 1.80, "transit_days": 0.2},
            "gangavaram": {"distance_km": 12, "rail_freight_usd_ton": 1.40, "transit_days": 0.2},
            "paradip": {"distance_km": 620, "rail_freight_usd_ton": 20.50, "transit_days": 2.4},
            "krishnapatnam": {"distance_km": 490, "rail_freight_usd_ton": 16.80, "transit_days": 2.0}
        }
    }
}

# Bulk Commodities details
COMMODITIES = {
    "coking_coal": {
        "name": "Premium Hard Coking Coal (PHCC)",
        "category": "Raw Material - Blast Furnace",
        "benchmark_price_usd_ton": 245.0,
        "density_t_m3": 0.85,
        "default_origin": "hay_point",
        "default_vessel": "Capesize"
    },
    "thermal_coal": {
        "name": "Thermal / Non-Coking Coal (GAR 5000)",
        "category": "Energy / Captive Power",
        "benchmark_price_usd_ton": 95.0,
        "density_t_m3": 0.82,
        "default_origin": "taboneo",
        "default_vessel": "Panamax"
    },
    "pci_coal": {
        "name": "Pulverized Coal Injection (PCI)",
        "category": "Fuel / Injection",
        "benchmark_price_usd_ton": 165.0,
        "density_t_m3": 0.84,
        "default_origin": "taman",
        "default_vessel": "Panamax"
    },
    "limestone": {
        "name": "Blast Furnace Grade Limestone / Dolomite",
        "category": "Flux Material",
        "benchmark_price_usd_ton": 28.0,
        "density_t_m3": 1.35,
        "default_origin": "fujairah",
        "default_vessel": "Supramax"
    }
}

# ---------------------------------------------------------
# Comprehensive Metadata & Throughput for All 12 Major Ports
# ---------------------------------------------------------
ALL_MAJOR_PORTS = {
    "deendayal": {
        "id": "deendayal",
        "port": "Deendayal",
        "aliases": ["Kandla", "Deendayal Port Authority", "DPA"],
        "state": "Gujarat",
        "coast": "West Coast",
        "coordinates": [23.0033, 70.2186],
        "max_draft_meters": 14.5,
        "max_dwt": 120000,
        "traffic_2022_23_mt": 137.56,
        "traffic_rank_2022_23": 1,
        "overseas_total_000t": 122236,
        "coastal_total_000t": 15325,
        "grand_total_000t": 137561,
        "overseas_share_pct": 88.86,
        "coastal_share_pct": 11.14,
        "major_commodities": ["Crude Oil (Vadinar)", "POL", "Dry Bulk", "Fertilizer", "Grain"],
        "description": "India's highest cargo throughput port, premier gateway for crude oil and agricultural bulk."
    },
    "paradip": {
        "id": "paradip",
        "port": "Paradip",
        "aliases": ["Paradip Port Authority", "PPA"],
        "state": "Odisha",
        "coast": "East Coast",
        "coordinates": [20.2644, 86.6715],
        "max_draft_meters": 17.1,
        "max_dwt": 180000,
        "traffic_2022_23_mt": 135.36,
        "traffic_rank_2022_23": 2,
        "overseas_total_000t": 76938,
        "coastal_total_000t": 58423,
        "grand_total_000t": 135361,
        "overseas_share_pct": 56.84,
        "coastal_share_pct": 43.16,
        "major_commodities": ["Thermal Coal", "Coking Coal", "Iron Ore Pellets", "Crude Oil"],
        "description": "Premier deep-draft hub on East Coast; top thermal coal evacuation and coking coal import terminal."
    },
    "jl_nehru": {
        "id": "jl_nehru",
        "port": "J.L. Nehru",
        "aliases": ["JNPT", "Jawaharlal Nehru Port", "Nhava Sheva", "J.L.Nehru"],
        "state": "Maharashtra",
        "coast": "West Coast",
        "coordinates": [18.9499, 72.9515],
        "max_draft_meters": 15.0,
        "max_dwt": 140000,
        "traffic_2022_23_mt": 83.86,
        "traffic_rank_2022_23": 3,
        "overseas_total_000t": 78884,
        "coastal_total_000t": 4977,
        "grand_total_000t": 83861,
        "overseas_share_pct": 94.07,
        "coastal_share_pct": 5.93,
        "major_commodities": ["Containerized Cargo", "Liquid Chemical Bulk", "Automobiles"],
        "description": "India's premier container transshipment and gateway hub handling over 50% of container traffic."
    },
    "visakhapatnam": {
        "id": "visakhapatnam",
        "port": "Visakhapatnam",
        "aliases": ["Vizag", "Visakhapatnam Port Authority", "VPA"],
        "state": "Andhra Pradesh",
        "coast": "East Coast",
        "coordinates": [17.6868, 83.2185],
        "max_draft_meters": 18.1,
        "max_dwt": 200000,
        "traffic_2022_23_mt": 73.75,
        "traffic_rank_2022_23": 4,
        "overseas_total_000t": 54600,
        "coastal_total_000t": 19150,
        "grand_total_000t": 73750,
        "overseas_share_pct": 74.03,
        "coastal_share_pct": 25.97,
        "major_commodities": ["Coking Coal", "Iron Ore", "POL Products", "Thermal Coal", "Alumina"],
        "description": "Key industrial port on Bay of Bengal directly feeding Vizag Steel (RINL) and NMDC export corridors."
    },
    "smp_haldia": {
        "id": "smp_haldia",
        "port": "SMP (Haldia Dock Complex)",
        "aliases": ["Syama Prasad Mookerjee Port - Haldia", "Haldia", "HDC", "SMP(Kolkata/Haldia)"],
        "state": "West Bengal",
        "coast": "East Coast",
        "coordinates": [22.0232, 88.0645],
        "max_draft_meters": 8.5,
        "max_dwt": 55000,
        "traffic_2022_23_mt": 48.61,
        "traffic_rank_2022_23": 5,
        "overseas_total_000t": 43656,
        "coastal_total_000t": 4952,
        "grand_total_000t": 48608,
        "overseas_share_pct": 89.81,
        "coastal_share_pct": 10.19,
        "major_commodities": ["Coking Coal", "POL Products", "LPG", "Petrochemicals", "Thermal Coal"],
        "description": "Strategic riverine bulk dock closest to Durgapur and Burnpur steel clusters."
    },
    "chennai": {
        "id": "chennai",
        "port": "Chennai",
        "aliases": ["Madras Port", "Chennai Port Authority", "ChPA"],
        "state": "Tamil Nadu",
        "coast": "East Coast",
        "coordinates": [13.0844, 80.2974],
        "max_draft_meters": 15.5,
        "max_dwt": 120000,
        "traffic_2022_23_mt": 48.95,
        "traffic_rank_2022_23": 6,
        "overseas_total_000t": 43032,
        "coastal_total_000t": 5917,
        "grand_total_000t": 48949,
        "overseas_share_pct": 87.91,
        "coastal_share_pct": 12.09,
        "major_commodities": ["Automobiles", "Containers", "POL Products", "Clean Cargo"],
        "description": "One of India's oldest artificial deepwater ports and major automotive export gateway."
    },
    "kamarajar": {
        "id": "kamarajar",
        "port": "Kamarajar",
        "aliases": ["Ennore", "Kamarajar Port Limited", "KPL"],
        "state": "Tamil Nadu",
        "coast": "East Coast",
        "coordinates": [13.2625, 80.3347],
        "max_draft_meters": 16.0,
        "max_dwt": 150000,
        "traffic_2022_23_mt": 43.51,
        "traffic_rank_2022_23": 7,
        "overseas_total_000t": 26006,
        "coastal_total_000t": 17501,
        "grand_total_000t": 43507,
        "overseas_share_pct": 59.77,
        "coastal_share_pct": 40.23,
        "major_commodities": ["Thermal Coal", "Automobiles (Ro-Ro)", "POL / LPG", "Containers"],
        "description": "India's only corporatized major port; primary energy and coal supply gateway for TANGEDCO power plants."
    },
    "new_mangalore": {
        "id": "new_mangalore",
        "port": "New Mangalore",
        "aliases": ["NMPA", "Panambur"],
        "state": "Karnataka",
        "coast": "West Coast",
        "coordinates": [12.9287, 74.8214],
        "max_draft_meters": 15.1,
        "max_dwt": 125000,
        "traffic_2022_23_mt": 41.42,
        "traffic_rank_2022_23": 8,
        "overseas_total_000t": 32341,
        "coastal_total_000t": 9076,
        "grand_total_000t": 41417,
        "overseas_share_pct": 78.09,
        "coastal_share_pct": 21.91,
        "major_commodities": ["POL Crude", "LPG", "Fertilizers", "Iron Ore Pellets", "Coal"],
        "description": "Deepwater all-weather port on the West Coast serving MRPL refinery and Kudremukh pellet plants."
    },
    "vo_chidambaranar": {
        "id": "vo_chidambaranar",
        "port": "V.O. Chidambaranar",
        "aliases": ["Tuticorin", "VOC Port", "Thoothukudi", "V.O.Chidambaranar"],
        "state": "Tamil Nadu",
        "coast": "East Coast",
        "coordinates": [8.7538, 78.1884],
        "max_draft_meters": 14.2,
        "max_dwt": 95000,
        "traffic_2022_23_mt": 38.04,
        "traffic_rank_2022_23": 9,
        "overseas_total_000t": 25470,
        "coastal_total_000t": 12572,
        "grand_total_000t": 38041,
        "overseas_share_pct": 66.95,
        "coastal_share_pct": 33.05,
        "major_commodities": ["Thermal Coal", "Containers", "Fertilizers", "Industrial Chemicals"],
        "description": "Strategic southern gateway on the Gulf of Mannar near international East-West shipping lanes."
    },
    "cochin": {
        "id": "cochin",
        "port": "Cochin",
        "aliases": ["Kochi", "Cochin Port Authority", "Vallarpadam"],
        "state": "Kerala",
        "coast": "West Coast",
        "coordinates": [9.9656, 76.2690],
        "max_draft_meters": 14.5,
        "max_dwt": 115000,
        "traffic_2022_23_mt": 35.26,
        "traffic_rank_2022_23": 10,
        "overseas_total_000t": 23150,
        "coastal_total_000t": 12106,
        "grand_total_000t": 35256,
        "overseas_share_pct": 65.66,
        "coastal_share_pct": 34.34,
        "major_commodities": ["Crude Oil (BPCL Kochi)", "Containers (ICTT)", "LNG", "Dry Bulk"],
        "description": "Natural harbor located just 11 nautical miles from the primary East-West maritime route."
    },
    "mumbai": {
        "id": "mumbai",
        "port": "Mumbai",
        "aliases": ["Mumbai Port Trust", "MbPT"],
        "state": "Maharashtra",
        "coast": "West Coast",
        "coordinates": [18.9438, 72.8466],
        "max_draft_meters": 11.5,
        "max_dwt": 80000,
        "traffic_2022_23_mt": 63.61,
        "traffic_rank_2022_23": 11,
        "overseas_total_000t": 41006,
        "coastal_total_000t": 22602,
        "grand_total_000t": 63608,
        "overseas_share_pct": 64.47,
        "coastal_share_pct": 35.53,
        "major_commodities": ["POL Products", "General Cargo", "Vehicles", "Cruise Vessels"],
        "description": "Historic natural deepwater port handling heavy liquid bulk and general coastal cargo."
    },
    "mormugao": {
        "id": "mormugao",
        "port": "Mormugao",
        "aliases": ["Goa Port", "Mormugao Port Authority", "MPA"],
        "state": "Goa",
        "coast": "West Coast",
        "coordinates": [15.4137, 73.8016],
        "max_draft_meters": 14.1,
        "max_dwt": 85000,
        "traffic_2022_23_mt": 17.33,
        "traffic_rank_2022_23": 12,
        "overseas_total_000t": 15601,
        "coastal_total_000t": 1733,
        "grand_total_000t": 17334,
        "overseas_share_pct": 90.00,
        "coastal_share_pct": 10.00,
        "major_commodities": ["Iron Ore", "Thermal Coal", "Met Coke", "Cruise"],
        "description": "Leading iron ore and bulk coal terminal on the mouth of Zuari River in Goa."
    },
    "smp_kolkata": {
        "id": "smp_kolkata",
        "port": "SMP (Kolkata Dock System)",
        "aliases": ["Syama Prasad Mookerjee Port - Kolkata", "Kolkata", "KDS", "Calcutta Port"],
        "state": "West Bengal",
        "coast": "East Coast",
        "coordinates": [22.5448, 88.3184],
        "max_draft_meters": 7.5,
        "max_dwt": 30000,
        "traffic_2022_23_mt": 17.05,
        "traffic_rank_2022_23": 13,
        "overseas_total_000t": 16660,
        "coastal_total_000t": 391,
        "grand_total_000t": 17051,
        "overseas_share_pct": 97.71,
        "coastal_share_pct": 2.29,
        "major_commodities": ["Containers", "Break Bulk", "Nepal & Bhutan Transit Cargo", "Timber"],
        "description": "Inland riverine dock system and principal transit lifeline for landlocked neighboring countries."
    }
}

def find_major_port(query_str):
    """
    Looks up a port in ALL_MAJOR_PORTS by exact ID, display name, or alias.
    Case-insensitive.
    """
    if not query_str:
        return None
    q = str(query_str).strip().lower()
    
    # Check ID direct match
    if q in ALL_MAJOR_PORTS:
        return ALL_MAJOR_PORTS[q]
        
    for port_id, data in ALL_MAJOR_PORTS.items():
        if data["port"].lower() == q:
            return data
        for alias in data.get("aliases", []):
            if alias.lower() == q or q in alias.lower():
                return data
                
    return None

def get_national_port_cargo_totals():
    """
    Returns aggregated figures for all major Indian ports (FY 2022-23 benchmark).
    """
    return {
        "total_traffic_mt": 784.30,
        "grand_total_000t": 784305,
        "overseas_unloaded_000t": 439801,
        "overseas_loaded_000t": 146283,
        "overseas_transhipment_000t": 13495,
        "overseas_total_000t": 599579,
        "overseas_share_pct": 76.45,
        "coastal_unloaded_000t": 73796,
        "coastal_loaded_000t": 100627,
        "coastal_transhipment_000t": 10302,
        "coastal_total_000t": 184725,
        "coastal_share_pct": 23.55,
        "active_major_ports": len(ALL_MAJOR_PORTS),
        "top_ports_by_volume": ["deendayal", "paradip", "jl_nehru", "visakhapatnam", "mumbai"]
    }
