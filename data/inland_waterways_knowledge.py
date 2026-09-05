"""
Inland Waterways Transport (IWT) & National Waterways Knowledge Base
Official Data & Benchmarks based on Inland Waterways Authority of India (IWAI),
Ministry of Ports, Shipping and Waterways, and Jal Marg Vikas Project.
"""

NATIONAL_WATERWAYS = {
    "NW-1": {
        "id": "NW-1",
        "name": "National Waterway 1 (Ganga - Bhagirathi - Hooghly River System)",
        "river_system": "Ganga - Bhagirathi - Hooghly",
        "states": ["Uttar Pradesh", "Bihar", "Jharkhand", "West Bengal"],
        "stretch": "Prayagraj (Allahabad) to Haldia",
        "total_length_km": 1620,
        "navigable_length_km": 1620,
        "round_the_year_navigable_km": 1390,
        "status": "Operational (Jal Marg Vikas Project)",
        "declared_year": 1986,
        "annual_cargo_mt": 13.17,
        "cargo_share_pct": 9.9,
        "connected_ports": ["Haldia Dock Complex", "Syama Prasad Mookerjee Port (Kolkata)"],
        "connected_steel_hubs": ["SAIL Durgapur (DSP)", "SAIL Bokaro (BSL)", "Tata Steel Jamshedpur"],
        "key_terminals": ["MMT Varanasi", "MMT Sahibganj", "MMT Haldia", "Kalughat IWT", "Gaighat (Patna)"],
        "ris_coverage": "Varanasi to Haldia (1,390 km operational RIS)",
        "description": "India's premier inland arterial waterway connecting the Indo-Gangetic heartland with maritime sea-ports at Haldia and Kolkata. Primary route for steel products, coal, fly ash, and heavy project cargo."
    },
    "NW-2": {
        "id": "NW-2",
        "name": "National Waterway 2 (Brahmaputra River)",
        "river_system": "Brahmaputra",
        "states": ["Assam", "West Bengal", "Meghalaya", "Arunachal Pradesh"],
        "stretch": "Dhubri (Bangladesh Border) to Sadiya",
        "total_length_km": 891,
        "navigable_length_km": 891,
        "round_the_year_navigable_km": 768,
        "status": "Operational (Connected via Indo-Bangladesh Protocol Route)",
        "declared_year": 1988,
        "annual_cargo_mt": 2.45,
        "cargo_share_pct": 1.84,
        "connected_ports": ["Kolkata Port (via IBPR)", "Mongla Port (Bangladesh)"],
        "connected_steel_hubs": ["North-East Infrastructure & Defense corridors", "Guwahati Logistics Node"],
        "key_terminals": ["Pandu Port (Guwahati)", "Dhubri Terminal", "Jogighopa MMT", "Silghat", "Neamati"],
        "ris_coverage": "Dhubri to Neamati (Operational)",
        "description": "Lifeline for North-Eastern logistics connecting Haldia/Kolkata to Assam via the Indo-Bangladesh Protocol (IBPR) route, circumventing the Siliguri chicken's neck corridor."
    },
    "NW-3": {
        "id": "NW-3",
        "name": "National Waterway 3 (West Coast Canal & Champakara / Udyogmandal Canals)",
        "river_system": "West Coast Canal, Champakara & Udyogmandal",
        "states": ["Kerala"],
        "stretch": "Kottapuram to Kollam",
        "total_length_km": 205,
        "navigable_length_km": 205,
        "round_the_year_navigable_km": 205,
        "status": "Operational (Fully navigable round-the-year)",
        "declared_year": 1993,
        "annual_cargo_mt": 14.80,
        "cargo_share_pct": 11.13,
        "connected_ports": ["Cochin Port (Vallarpadam ICTT)"],
        "connected_steel_hubs": ["Kochi Industrial & Petrochemical Corridor"],
        "key_terminals": ["Kottapuram", "Aluva", "Maradu", "Vaikom", "Kayamkulam", "Kollam"],
        "ris_coverage": "Full 205 km under 24x7 navigation assistance",
        "description": "Continuous round-the-year inland canal with high industrial traffic connecting Cochin Port with chemical, petroleum, fertilizer, and bulk cargo terminals."
    },
    "NW-4": {
        "id": "NW-4",
        "name": "National Waterway 4 (Krishna - Godavari River Systems & Canals)",
        "river_system": "Krishna, Godavari & Buckingham Canal",
        "states": ["Andhra Pradesh", "Telangana", "Tamil Nadu", "Puducherry"],
        "stretch": "Kakinada to Puducherry via Godavari & Krishna canals",
        "total_length_km": 1078,
        "navigable_length_km": 690,
        "round_the_year_navigable_km": 420,
        "status": "Partially Operational / Under Fast-Track Development",
        "declared_year": 2008,
        "annual_cargo_mt": 6.80,
        "cargo_share_pct": 5.11,
        "connected_ports": ["Kakinada Port", "Machilipatnam", "Chennai Port", "Kamarajar Port"],
        "connected_steel_hubs": ["RINL Visakhapatnam (VSP)", "Vijayawada Metal Cluster"],
        "key_terminals": ["Muktyala", "Ibrahimpatnam", "Harishchandrapuram", "Kakinada IWT Terminal"],
        "ris_coverage": "Muktyala to Vijayawada stretch",
        "description": "Connects the rich mineral belt of Andhra Pradesh and Telangana to East Coast maritime ports. Crucial for cement, limestone, fly ash, and finished steel movement."
    },
    "NW-5": {
        "id": "NW-5",
        "name": "National Waterway 5 (Brahmani - Mahanadi River System & East Coast Canal)",
        "river_system": "Brahmani, Kharsua, Dhamra, Mahanadi Delta & East Coast Canal",
        "states": ["Odisha", "West Bengal"],
        "stretch": "Talcher - Dhamra - Paradip - Geonkhali",
        "total_length_km": 623,
        "navigable_length_km": 588,
        "round_the_year_navigable_km": 332,
        "status": "Operational & Commercial Coal Corridor (Fast-Track Phase 1)",
        "declared_year": 2008,
        "annual_cargo_mt": 11.20,
        "cargo_share_pct": 8.42,
        "connected_ports": ["Paradip Port", "Dhamra Port", "Geonkhali"],
        "connected_steel_hubs": [
            "SAIL Rourkela (RSP)", "Tata Steel Kalinganagar", "JSPL Angul",
            "Mahanadi Coalfields (Talcher)", "Jindal Stainless Jajpur"
        ],
        "key_terminals": ["Pankpal (Kalinganagar)", "Talcher Coal Terminal", "Paradip IWT Berth", "Dhamra River Terminal"],
        "ris_coverage": "Pankpal to Paradip stretch (185 km)",
        "description": "The golden industrial corridor of India's steel heartland. Directly links the Talcher coal basin and Kalinganagar steel clusters to Paradip and Dhamra deep-sea ports."
    },
    "NW-16": {
        "id": "NW-16",
        "name": "National Waterway 16 (Barak River)",
        "river_system": "Barak River",
        "states": ["Assam", "Mizoram", "Manipur"],
        "stretch": "Bhanga to Lakhipur",
        "total_length_km": 121,
        "navigable_length_km": 121,
        "round_the_year_navigable_km": 72,
        "status": "Operational",
        "declared_year": 2016,
        "annual_cargo_mt": 0.48,
        "cargo_share_pct": 0.36,
        "connected_ports": ["Kolkata Port (via IBPR and Bangladesh Ashuganj)"],
        "connected_steel_hubs": ["Barak Valley Infrastructure", "Silchar Logistics Gateway"],
        "key_terminals": ["Badarpur Terminal", "Karimganj Terminal"],
        "ris_coverage": "DGPS coverage installed",
        "description": "Strategic eastern waterway connecting Assam's Barak valley and southern North-East with Kolkata and Bangladesh waterways."
    },
    "NW-68": {
        "id": "NW-68",
        "name": "National Waterway 68 (Mandovi River)",
        "river_system": "Mandovi River",
        "states": ["Goa"],
        "stretch": "Usgaon Bridge to Arabian Sea (Panaji)",
        "total_length_km": 41,
        "navigable_length_km": 41,
        "round_the_year_navigable_km": 41,
        "status": "Operational (Heavy Iron Ore & Passenger Barge Traffic)",
        "declared_year": 2016,
        "annual_cargo_mt": 18.50,
        "cargo_share_pct": 13.91,
        "connected_ports": ["Mormugao Port (MPT)"],
        "connected_steel_hubs": ["Goa Iron Ore Mining Belts", "Pellet Plants"],
        "key_terminals": ["Panaji Ferry Terminal", "Usgaon Jetty", "Sanvordem"],
        "ris_coverage": "Complete stretch monitored with VTS and coastal AIS",
        "description": "High-density mineral export waterway ferrying iron ore, metallurgical coke, and passenger vessels directly into Mormugao deep-water port."
    },
    "NW-86": {
        "id": "NW-86",
        "name": "National Waterway 86 (Rupnarayan River)",
        "river_system": "Rupnarayan River",
        "states": ["West Bengal"],
        "stretch": "Confluence with Hooghly to Bakshi",
        "total_length_km": 98,
        "navigable_length_km": 98,
        "round_the_year_navigable_km": 98,
        "status": "Operational",
        "declared_year": 2016,
        "annual_cargo_mt": 16.20,
        "cargo_share_pct": 12.18,
        "connected_ports": ["Haldia Dock Complex", "Kolkata Port"],
        "connected_steel_hubs": ["Haldia Petrochemical & Metal Cluster", "Kharagpur Metal Hub"],
        "key_terminals": ["Geonkhali", "Kolaghat Fly Ash Jetty", "Bakshi"],
        "ris_coverage": "Linked to NW-1 River Information System",
        "description": "Crucial tributary waterway feeding fly ash from Kolaghat Thermal Power Station to Bangladesh and cement plants, and ferrying steel coils and industrial aggregates."
    },
    "NW-97": {
        "id": "NW-97",
        "name": "National Waterway 97 (Sundarbans Waterways)",
        "river_system": "Sundarbans Delta (Namkhana, Raimangal, Bidya, Ichamati)",
        "states": ["West Bengal"],
        "stretch": "Namkhana to Indo-Bangladesh Border at Hemnagar",
        "total_length_km": 172,
        "navigable_length_km": 172,
        "round_the_year_navigable_km": 172,
        "status": "Operational (Indo-Bangladesh Protocol Trade Arterial)",
        "declared_year": 2016,
        "annual_cargo_mt": 37.80,
        "cargo_share_pct": 28.42,
        "connected_ports": ["Haldia Dock Complex", "Kolkata Port", "Mongla (Bangladesh)", "Chattogram"],
        "connected_steel_hubs": ["Eastern India Export Corridor", "SAIL / Tata Steel Bangladesh Export Routes"],
        "key_terminals": ["Namkhana", "Hemnagar Customs Checkpoint", "Hasnabad"],
        "ris_coverage": "Operational DGPS and radar vessel tracking along protocol boundary",
        "description": "The highest-density inland waterway in India, carrying over 37 million tonnes of export-import trade (fly ash, finished steel, stone chips, cement) between India and Bangladesh under the bilateral protocol."
    },
    "NW-111": {
        "id": "NW-111",
        "name": "National Waterway 111 (Zuari River)",
        "river_system": "Zuari River",
        "states": ["Goa"],
        "stretch": "Sanvordem Bridge to Marmagao Port",
        "total_length_km": 50,
        "navigable_length_km": 50,
        "round_the_year_navigable_km": 50,
        "status": "Operational (Bulk Minerals & Heavy Cargo)",
        "declared_year": 2016,
        "annual_cargo_mt": 11.60,
        "cargo_share_pct": 8.72,
        "connected_ports": ["Mormugao Port"],
        "connected_steel_hubs": ["Sanguem/Kudnem Mining Hubs", "Coke / Flux Importers"],
        "key_terminals": ["Sanvordem", "Cortalim", "Mormugao Barge Berths"],
        "ris_coverage": "VTS operational",
        "description": "Key industrial arterial linking South Goa mining and metallurgy belts directly to ocean-going bulk freighters at Mormugao."
    }
}

# 11-year historical cargo throughput (FY 2013-14 to FY 2023-24) + Projections to 2030 (in Million Tonnes)
CARGO_MOVEMENT_TIMESERIES = [
    {"fiscal_year": "2013-14", "year": 2014, "cargo_mt": 18.01, "yoy_growth_pct": None, "nw1_mt": 3.12, "nw97_mt": 7.80, "other_nw_mt": 7.09, "modal_share_pct": 0.52},
    {"fiscal_year": "2014-15", "year": 2015, "cargo_mt": 20.45, "yoy_growth_pct": 13.55, "nw1_mt": 3.65, "nw97_mt": 8.90, "other_nw_mt": 7.90, "modal_share_pct": 0.58},
    {"fiscal_year": "2015-16", "year": 2016, "cargo_mt": 24.30, "yoy_growth_pct": 18.83, "nw1_mt": 4.10, "nw97_mt": 10.40, "other_nw_mt": 9.80, "modal_share_pct": 0.67},
    {"fiscal_year": "2016-17", "year": 2017, "cargo_mt": 30.15, "yoy_growth_pct": 24.07, "nw1_mt": 4.85, "nw97_mt": 12.60, "other_nw_mt": 12.70, "modal_share_pct": 0.81},
    {"fiscal_year": "2017-18", "year": 2018, "cargo_mt": 38.60, "yoy_growth_pct": 28.03, "nw1_mt": 5.48, "nw97_mt": 15.90, "other_nw_mt": 17.22, "modal_share_pct": 0.98},
    {"fiscal_year": "2018-19", "year": 2019, "cargo_mt": 55.03, "yoy_growth_pct": 42.56, "nw1_mt": 6.79, "nw97_mt": 21.30, "other_nw_mt": 26.94, "modal_share_pct": 1.34},
    {"fiscal_year": "2019-20", "year": 2020, "cargo_mt": 73.64, "yoy_growth_pct": 33.82, "nw1_mt": 7.95, "nw97_mt": 26.80, "other_nw_mt": 38.89, "modal_share_pct": 1.76},
    {"fiscal_year": "2020-21", "year": 2021, "cargo_mt": 83.61, "yoy_growth_pct": 13.54, "nw1_mt": 9.21, "nw97_mt": 29.50, "other_nw_mt": 44.90, "modal_share_pct": 1.95},
    {"fiscal_year": "2021-22", "year": 2022, "cargo_mt": 108.79, "yoy_growth_pct": 30.12, "nw1_mt": 11.02, "nw97_mt": 33.40, "other_nw_mt": 64.37, "modal_share_pct": 2.38},
    {"fiscal_year": "2022-23", "year": 2023, "cargo_mt": 126.15, "yoy_growth_pct": 15.96, "nw1_mt": 12.45, "nw97_mt": 36.10, "other_nw_mt": 77.60, "modal_share_pct": 2.68},
    {"fiscal_year": "2023-24", "year": 2024, "cargo_mt": 133.00, "yoy_growth_pct": 5.43, "nw1_mt": 13.17, "nw97_mt": 37.80, "other_nw_mt": 82.03, "modal_share_pct": 2.82},
    # Forward Projections under Maritime India Vision 2030 (AI P50 forecast)
    {"fiscal_year": "2024-25 (P)", "year": 2025, "cargo_mt": 147.50, "yoy_growth_pct": 10.90, "nw1_mt": 15.20, "nw97_mt": 40.50, "other_nw_mt": 91.80, "modal_share_pct": 3.05, "is_projection": True},
    {"fiscal_year": "2025-26 (P)", "year": 2026, "cargo_mt": 164.20, "yoy_growth_pct": 11.32, "nw1_mt": 17.80, "nw97_mt": 43.60, "other_nw_mt": 102.80, "modal_share_pct": 3.32, "is_projection": True},
    {"fiscal_year": "2026-27 (P)", "year": 2027, "cargo_mt": 182.90, "yoy_growth_pct": 11.39, "nw1_mt": 20.90, "nw97_mt": 47.10, "other_nw_mt": 114.90, "modal_share_pct": 3.60, "is_projection": True},
    {"fiscal_year": "2027-28 (P)", "year": 2028, "cargo_mt": 203.80, "yoy_growth_pct": 11.43, "nw1_mt": 24.50, "nw97_mt": 50.80, "other_nw_mt": 128.50, "modal_share_pct": 3.91, "is_projection": True},
    {"fiscal_year": "2028-29 (P)", "year": 2029, "cargo_mt": 226.90, "yoy_growth_pct": 11.33, "nw1_mt": 28.60, "nw97_mt": 54.90, "other_nw_mt": 143.40, "modal_share_pct": 4.25, "is_projection": True},
    {"fiscal_year": "2029-30 (P)", "year": 2030, "cargo_mt": 252.50, "yoy_growth_pct": 11.28, "nw1_mt": 33.20, "nw97_mt": 59.40, "other_nw_mt": 159.90, "modal_share_pct": 4.60, "is_projection": True}
]

# Cargo by Commodity Breakdown (FY 2023-24 Official IWAI statistics)
COMMODITY_BREAKDOWN = {
    "coal": {
        "id": "coal",
        "name": "Coal (Thermal & Coking)",
        "annual_tonnage_mt": 39.90,
        "share_pct": 30.0,
        "key_routes": ["NW-5 Talcher to Paradip/Dhamra", "NW-1 Haldia to Farakka/Barh", "NW-68/NW-111 Goa to Thermal plants"],
        "primary_users": ["NTPC Farakka", "NTPC Barh", "SAIL Plants", "Tata Steel", "JSPL Angul"],
        "growth_yoy_pct": 14.2,
        "icon": "⛏️",
        "description": "Largest bulk commodity moved on Indian inland waterways. Power plants and blast furnaces save ₹400–750 per tonne compared to congested rail networks."
    },
    "fly_ash": {
        "id": "fly_ash",
        "name": "Fly Ash (Thermal Power Byproduct)",
        "annual_tonnage_mt": 34.58,
        "share_pct": 26.0,
        "key_routes": ["NW-86 / NW-97 Kolaghat & Budge Budge to Bangladesh (IBPR)", "NW-1 Kahalgaon to cement factories"],
        "primary_users": ["Bangladesh Cement Manufacturers", "Ultratech Cement", "Ambuja Cement"],
        "growth_yoy_pct": 18.5,
        "icon": "💨",
        "description": "High-volume green bulk export from West Bengal and Bihar thermal power plants to cement grinding units across Bangladesh via the Sundarbans protocol route."
    },
    "iron_ore": {
        "id": "iron_ore",
        "name": "Iron Ore & Pellets",
        "annual_tonnage_mt": 21.28,
        "share_pct": 16.0,
        "key_routes": ["NW-68 / NW-111 Goa mining belts to Mormugao", "NW-5 Mahanadi delta to Paradip"],
        "primary_users": ["Vedanta Sesa", "Jindal Steel", "Export Traded Cargo"],
        "growth_yoy_pct": 8.3,
        "icon": "🪨",
        "description": "Traditional high-density barge traffic in Goa and emerging mineral barge logistics in Odisha connecting iron ore mines with export berths."
    },
    "sand_aggregates": {
        "id": "sand_aggregates",
        "name": "Sand, Stone Chips & Construction Aggregates",
        "annual_tonnage_mt": 13.30,
        "share_pct": 10.0,
        "key_routes": ["NW-1 Bihar / Bengal riverbanks", "NW-2 Pakur to Assam"],
        "primary_users": ["State PWDs", "NHAI Road Projects", "Urban Infra"],
        "growth_yoy_pct": 6.8,
        "icon": "🏗️",
        "description": "Crucial riverbed aggregates transported on dumb barges, drastically reducing heavy truck congestion on national and state highways."
    },
    "cement": {
        "id": "cement",
        "name": "Cement & Clinker",
        "annual_tonnage_mt": 9.31,
        "share_pct": 7.0,
        "key_routes": ["NW-4 Krishna river to Vijayawada", "NW-1 Haldia to Patna/Varanasi", "NW-2 Pandu"],
        "primary_users": ["Ultratech", "Dalmia Bharat", "Shree Cement", "Star Cement"],
        "growth_yoy_pct": 21.4,
        "icon": "🧱",
        "description": "Rapidly expanding multi-modal sector; bag and bulk cement movement to eastern and north-eastern markets with low transit breakage."
    },
    "steel": {
        "id": "steel",
        "name": "Finished Steel, Coils & Billets",
        "annual_tonnage_mt": 5.32,
        "share_pct": 4.0,
        "key_routes": ["NW-1 Haldia to Patna & Varanasi", "NW-5 Kalinganagar to Paradip / Haldia", "NW-2 Kolkata to Pandu (Guwahati)"],
        "primary_users": ["SAIL (Steel Authority of India)", "Tata Steel", "Jindal Steel & Power", "AM/NS India"],
        "growth_yoy_pct": 34.0,
        "icon": "⛓️",
        "description": "Fastest growing high-value cargo sector. Steel PSUs leverage river barges to bypass railway wagon shortages for heavy HR/CR coils and TMT bars."
    },
    "fertilizers": {
        "id": "fertilizers",
        "name": "Chemical Fertilizers (Urea / DAP / NPK)",
        "annual_tonnage_mt": 3.99,
        "share_pct": 3.0,
        "key_routes": ["NW-1 Haldia / Kolkata to UP & Bihar farm belts", "NW-4 Kakinada to Godavari basin"],
        "primary_users": ["IFFCO", "KRIBHCO", "IPL", "Paradeep Phosphates (PPL)"],
        "growth_yoy_pct": 12.0,
        "icon": "🌱",
        "description": "Essential agricultural inputs delivered directly to riverine rural consumption districts during sowing seasons."
    },
    "food_grains": {
        "id": "food_grains",
        "name": "Food Grains (Wheat & Rice - FCI Logistics)",
        "annual_tonnage_mt": 2.66,
        "share_pct": 2.0,
        "key_routes": ["NW-1 Patna to Kolkata / Bangladesh", "NW-2 Kolkata to Pandu (Assam) via IBPR"],
        "primary_users": ["Food Corporation of India (FCI)", "State Civil Supplies Departments"],
        "growth_yoy_pct": 15.5,
        "icon": "🌾",
        "description": "Public Distribution System (PDS) food grains transported from northern surplus granaries to Assam and North-Eastern states."
    },
    "containers_pol": {
        "id": "containers_pol",
        "name": "Containerized Cargo & POL / Chemical Liquids",
        "annual_tonnage_mt": 2.66,
        "share_pct": 2.0,
        "key_routes": ["NW-1 Kolkata to Varanasi (MMT)", "NW-2 Pandu to Kolkata", "NW-3 Cochin to Udyogmandal"],
        "primary_users": ["PepsiCo", "Tata Motors", "IOCL", "BPCL", "Piramal Glass"],
        "growth_yoy_pct": 28.0,
        "icon": "📦",
        "description": "FMCG, automotive, chemicals, and containerized consumer goods utilizing scheduled river liner services."
    }
}

# IWT Vessel Fleet Classification & Specifications
VESSEL_FLEET = {
    "self_propelled_barge_1000": {
        "id": "self_propelled_barge_1000",
        "name": "Self-Propelled Barge (Class-III / 1,000 DWT)",
        "category": "Self-Propelled Cargo Vessel",
        "dwt_capacity": 1000,
        "length_overall_m": 60.0,
        "beam_width_m": 9.5,
        "laden_draft_m": 1.8,
        "ballast_draft_m": 0.8,
        "air_draft_m": 6.5,
        "service_speed_knots": 8.5,
        "fuel_consumption_liters_hr": 95,
        "daily_charter_rate_inr": 45000,
        "active_fleet_india": 142,
        "idle_reserve_fleet": 18,
        "suitable_waterways": ["NW-1 (Up to Varanasi)", "NW-2", "NW-3", "NW-5", "NW-86", "NW-97"],
        "primary_cargo": ["Steel coils", "Cement bags", "Containers", "Food grains"]
    },
    "self_propelled_barge_2000": {
        "id": "self_propelled_barge_2000",
        "name": "Self-Propelled Heavy Barge (Class-IV / 2,000 DWT)",
        "category": "Self-Propelled Cargo Vessel",
        "dwt_capacity": 2000,
        "length_overall_m": 75.0,
        "beam_width_m": 11.4,
        "laden_draft_m": 2.5,
        "ballast_draft_m": 1.0,
        "air_draft_m": 7.2,
        "service_speed_knots": 9.0,
        "fuel_consumption_liters_hr": 145,
        "daily_charter_rate_inr": 72000,
        "active_fleet_india": 98,
        "idle_reserve_fleet": 12,
        "suitable_waterways": ["NW-1 (Haldia to Barh)", "NW-2 (Dhubri to Pandu)", "NW-68", "NW-97"],
        "primary_cargo": ["Bulk coal", "Fly ash", "Iron ore", "Project cargo", "Heavy steel billets"]
    },
    "push_tow_dumb_barge_flotilla": {
        "id": "push_tow_dumb_barge_flotilla",
        "name": "Pusher Tug + 2x Dumb Barge Flotilla (3,000 DWT Total)",
        "category": "Tug-Barge Convoy",
        "dwt_capacity": 3000,
        "length_overall_m": 120.0,
        "beam_width_m": 11.4,
        "laden_draft_m": 2.2,
        "ballast_draft_m": 0.9,
        "air_draft_m": 6.8,
        "service_speed_knots": 7.0,
        "fuel_consumption_liters_hr": 180,
        "daily_charter_rate_inr": 95000,
        "active_fleet_india": 64,
        "idle_reserve_fleet": 8,
        "suitable_waterways": ["NW-1 (Haldia to Patna)", "NW-5 (Pankpal to Paradip)", "NW-97"],
        "primary_cargo": ["Thermal coal", "Limestone", "Sand & rock aggregates", "Iron ore"]
    },
    "ro_ro_vessel": {
        "id": "ro_ro_vessel",
        "name": "Roll-on/Roll-off (Ro-Ro / Ro-Pax) Commercial Vessel",
        "category": "Ro-Ro Vehicle & Truck Carrier",
        "dwt_capacity": 850,
        "truck_capacity_units": 28,
        "passenger_capacity": 200,
        "length_overall_m": 55.0,
        "beam_width_m": 12.0,
        "laden_draft_m": 1.5,
        "ballast_draft_m": 0.8,
        "air_draft_m": 6.0,
        "service_speed_knots": 10.0,
        "fuel_consumption_liters_hr": 110,
        "daily_charter_rate_inr": 65000,
        "active_fleet_india": 32,
        "idle_reserve_fleet": 4,
        "suitable_waterways": ["NW-1 (Ghogha/Dahej type, Sahibganj-Manihari)", "NW-2 (Dhubri-Hatsingimari)", "NW-3"],
        "primary_cargo": ["Loaded trucks", "Automobiles", "Inter-bank passengers"]
    },
    "river_sea_hybrid_vessel": {
        "id": "river_sea_hybrid_vessel",
        "name": "River-Sea Vessel (RSV Type-IV / 3,500 DWT)",
        "category": "Coastal-River Dual Mode Carrier",
        "dwt_capacity": 3500,
        "length_overall_m": 88.0,
        "beam_width_m": 14.5,
        "laden_draft_m": 3.8,
        "ballast_draft_m": 1.6,
        "air_draft_m": 8.5,
        "service_speed_knots": 10.5,
        "fuel_consumption_liters_hr": 240,
        "daily_charter_rate_inr": 140000,
        "active_fleet_india": 26,
        "idle_reserve_fleet": 3,
        "suitable_waterways": ["Coastal corridor + NW-1 (Haldia) + NW-5 (Paradip/Dhamra) + NW-97"],
        "primary_cargo": ["Export steel coils", "Import coking coal transhipment", "Fertilizers"]
    },
    "river_passenger_cruise": {
        "id": "river_passenger_cruise",
        "name": "Luxury River Tourism Cruiser (e.g. MV Ganga Vilas Class)",
        "category": "Passenger Luxury Cruiser",
        "dwt_capacity": 450,
        "passenger_capacity": 80,
        "length_overall_m": 62.5,
        "beam_width_m": 12.8,
        "laden_draft_m": 1.4,
        "ballast_draft_m": 0.9,
        "air_draft_m": 5.8,
        "service_speed_knots": 9.5,
        "fuel_consumption_liters_hr": 120,
        "daily_charter_rate_inr": 185000,
        "active_fleet_india": 18,
        "idle_reserve_fleet": 2,
        "suitable_waterways": ["NW-1 (Varanasi to Kolkata)", "NW-2 (Guwahati to Kaziranga)", "NW-97"],
        "primary_cargo": ["International & domestic tourists", "Pilgrim journeys", "Cultural expeditions"]
    }
}

# Inland Waterway Infrastructure (Terminals, Jetties, Berths, Equipment)
WATERWAY_INFRASTRUCTURE = {
    "mmt_varanasi": {
        "id": "mmt_varanasi",
        "name": "Multi-Modal Terminal Varanasi (Ramnagar)",
        "waterway_id": "NW-1",
        "state": "Uttar Pradesh",
        "location": "Ramnagar, Varanasi",
        "coordinates": {"lat": 25.2677, "lng": 83.0232},
        "terminal_type": "Multi-Modal River-Rail-Road Terminal",
        "berth_count": 2,
        "quay_length_m": 200,
        "cargo_handling_capacity_mtpa": 1.26,
        "storage_area_sqm": 35000,
        "equipment": [
            "1x 30T Mobile Harbour Crane (MHC)",
            "2x Reach Stackers (45T)",
            "Covered godown (5,000 MT)",
            "Dedicated rail siding (direct Indian Railways link)",
            "Automated conveyor discharge system"
        ],
        "operational_status": "Active (Inaugurated by Prime Minister 2018)",
        "handled_commodities": ["Finished steel products", "Cement", "Food grains", "Fertilizers", "FMCG containers"],
        "water_depth_berth_m": 3.0
    },
    "mmt_sahibganj": {
        "id": "mmt_sahibganj",
        "name": "Multi-Modal Terminal Sahibganj",
        "waterway_id": "NW-1",
        "state": "Jharkhand",
        "location": "Samda Ghat, Sahibganj",
        "coordinates": {"lat": 25.2500, "lng": 87.6500},
        "terminal_type": "Multi-Modal Terminal & Freight Hub",
        "berth_count": 2,
        "quay_length_m": 270,
        "cargo_handling_capacity_mtpa": 3.18,
        "storage_area_sqm": 48000,
        "equipment": [
            "2x 40T Mobile Harbour Cranes",
            "Heavy-duty Ro-Ro ramp for loaded truck ferries",
            "Dedicated mineral stockyard (200,000 MT capacity)",
            "Broad gauge rail connectivity link",
            "High-capacity dust suppression mist cannons"
        ],
        "operational_status": "Active (Key transhipment point for Rajmahal coal and stone chips to Bihar/Bangladesh)",
        "handled_commodities": ["Coal", "Stone chips & aggregates", "Cement", "Iron ore", "Food grains"],
        "water_depth_berth_m": 3.2
    },
    "mmt_haldia": {
        "id": "mmt_haldia",
        "name": "Multi-Modal Terminal Haldia",
        "waterway_id": "NW-1",
        "state": "West Bengal",
        "location": "Haldia Industrial Complex",
        "coordinates": {"lat": 22.0250, "lng": 88.0820},
        "terminal_type": "River-Sea Transhipment Terminal",
        "berth_count": 2,
        "quay_length_m": 290,
        "cargo_handling_capacity_mtpa": 3.08,
        "storage_area_sqm": 61000,
        "equipment": [
            "2x Gantry cranes with 35T spreader and grab",
            "Fly ash automated pneumatic barge loading silos",
            "Petrochemical bonded storage",
            "Direct interface with Haldia Dock Complex deep berths",
            "Full electronic EDI and customs clearance gate"
        ],
        "operational_status": "Active (Crucial gateway for deep-sea bulk transhipment into inland barges)",
        "handled_commodities": ["Coking coal", "Thermal coal", "Fly ash", "Steel coils", "Containers", "POL"],
        "water_depth_berth_m": 4.5
    },
    "kalughat_terminal": {
        "id": "kalughat_terminal",
        "name": "Kalughat Intermodal Terminal",
        "waterway_id": "NW-1",
        "state": "Bihar",
        "location": "Saran / Hajipur near Patna",
        "coordinates": {"lat": 25.6830, "lng": 85.2160},
        "terminal_type": "Intermodal Container Terminal for Nepal Transit",
        "berth_count": 2,
        "quay_length_m": 125,
        "cargo_handling_capacity_mtpa": 1.25,
        "storage_area_sqm": 22000,
        "equipment": [
            "1x 35T Harbour Crane",
            "Container yard (1,500 TEUs)",
            "Direct 4-lane NH-19 connectivity",
            "Nepal transit container bond inspection shed"
        ],
        "operational_status": "Active (Completed 2023 under Jal Marg Vikas Project)",
        "handled_commodities": ["Container cargo", "Nepal EXIM transit goods", "Steel bars", "Cement"],
        "water_depth_berth_m": 2.8
    },
    "pandu_port": {
        "id": "pandu_port",
        "name": "Pandu Inland Port (Guwahati)",
        "waterway_id": "NW-2",
        "state": "Assam",
        "location": "Guwahati",
        "coordinates": {"lat": 26.1667, "lng": 91.6833},
        "terminal_type": "Major River Port & Northeast Logistics Hub",
        "berth_count": 3,
        "quay_length_m": 260,
        "cargo_handling_capacity_mtpa": 2.00,
        "storage_area_sqm": 45000,
        "equipment": [
            "2x Shore cranes (20T & 10T)",
            "Container freight station (CFS)",
            "Broad-gauge railway connectivity spur",
            "Covered transit shed (7,500 MT)",
            "Ro-Ro jetty for commercial transport trucks"
        ],
        "operational_status": "Active (Premier inland port of North-East India)",
        "handled_commodities": ["Steel from SAIL/Tata", "FCI food grains", "Coal", "Fertilizers", "Tea export containers"],
        "water_depth_berth_m": 2.5
    },
    "dhubri_terminal": {
        "id": "dhubri_terminal",
        "name": "Dhubri River Terminal",
        "waterway_id": "NW-2",
        "state": "Assam",
        "location": "Dhubri (Near Bangladesh Border)",
        "coordinates": {"lat": 26.0200, "lng": 89.9800},
        "terminal_type": "Border Protocol & Coastal Trade Terminal",
        "berth_count": 2,
        "quay_length_m": 180,
        "cargo_handling_capacity_mtpa": 1.50,
        "storage_area_sqm": 30000,
        "equipment": [
            "1x 20T Mobile Crane",
            "Ro-Ro pontoon berth",
            "Customs electronic data interchange office",
            "Covered godowns for export cargo"
        ],
        "operational_status": "Active (High export traffic of Bhutan boulders & stone aggregates to Bangladesh)",
        "handled_commodities": ["Bhutanese stone aggregates", "Fertilizers", "Cement", "Food grains"],
        "water_depth_berth_m": 2.5
    },
    "pankpal_terminal": {
        "id": "pankpal_terminal",
        "name": "Pankpal (Kalinganagar) Terminal",
        "waterway_id": "NW-5",
        "state": "Odisha",
        "location": "Kalinganagar Industrial Complex / Jajpur",
        "coordinates": {"lat": 20.9500, "lng": 86.0500},
        "terminal_type": "Steel Belt Dedicated Inland Terminal",
        "berth_count": 2,
        "quay_length_m": 220,
        "cargo_handling_capacity_mtpa": 2.50,
        "storage_area_sqm": 50000,
        "equipment": [
            "2x Heavy-lift crawler cranes (50T for steel coils)",
            "Direct conveyor link to nearby steel plants",
            "Covered coil storage warehouse",
            "Heavy-payload barge loading ramp"
        ],
        "operational_status": "Operational Phase 1 (Dedicated to SAIL, Tata Steel Kalinganagar, JSPL Angul)",
        "handled_commodities": ["Finished steel coils", "Pig iron", "Thermal & coking coal", "Iron ore pellets"],
        "water_depth_berth_m": 3.0
    }
}

# Navigation Depth (Least Available Depth - LAD) & Dredging Status across Stretches
# (Relevance ⭐⭐⭐⭐⭐: 5 Stars)
NAVIGATION_DEPTH_LAD = {
    "NW1_HAL_FRK": {
        "stretch_id": "NW1_HAL_FRK",
        "waterway_id": "NW-1",
        "stretch_name": "Haldia - Farakka",
        "length_km": 460,
        "target_lad_m": 3.0,
        "actual_current_lad_m": 3.0,
        "min_seasonal_lad_m": 2.8,
        "dredging_status": "Maintained by regular trailing suction hopper dredgers (TSHD)",
        "shallow_patches": ["Tribeni shoals (2.8m in low tide)", "Nabadwip curve"],
        "air_draft_clearance_m": 9.5,
        "max_vessel_dwt_allowed": 2500,
        "navigation_status": "Normal / Unrestricted 24x7 Navigable",
        "ris_operational": True,
        "advisory": "Full laden transit permissible for vessels with draft up to 2.8m. Tidal assistance available south of Nabadwip."
    },
    "NW1_FRK_BRH": {
        "stretch_id": "NW1_FRK_BRH",
        "waterway_id": "NW-1",
        "stretch_name": "Farakka - Barh (via Kahalgaon & Sultanganj)",
        "length_km": 300,
        "target_lad_m": 2.5,
        "actual_current_lad_m": 2.6,
        "min_seasonal_lad_m": 2.2,
        "dredging_status": "Cutter suction dredging active near Vikramshila stretch",
        "shallow_patches": ["Kahalgaon power intake shoal", "Pirpainti bend (2.3m)"],
        "air_draft_clearance_m": 9.0,
        "max_vessel_dwt_allowed": 2000,
        "navigation_status": "Normal Navigable",
        "ris_operational": True,
        "advisory": "Safe navigation for vessels up to 2.4m draft. Navigation pilotage recommended at Kahalgaon curve."
    },
    "NW1_BRH_VRN": {
        "stretch_id": "NW1_BRH_VRN",
        "waterway_id": "NW-1",
        "stretch_name": "Barh - Patna - Ghazipur - Varanasi",
        "length_km": 490,
        "target_lad_m": 2.2,
        "actual_current_lad_m": 2.3,
        "min_seasonal_lad_m": 1.8,
        "dredging_status": "Intensive dry-season shoal dredging at Buxar & Ghazipur",
        "shallow_patches": ["Ghazipur shoal (2.0m)", "Buxar railway bridge passage (1.9m)"],
        "air_draft_clearance_m": 8.5,
        "max_vessel_dwt_allowed": 1500,
        "navigation_status": "Advisory Active (Daylight navigation for vessels > 2.0m draft)",
        "ris_operational": True,
        "advisory": "Class-III barges (up to 1,200 DWT) can operate smoothly. Night navigation beacons operational."
    },
    "NW1_VRN_PRY": {
        "stretch_id": "NW1_VRN_PRY",
        "waterway_id": "NW-1",
        "stretch_name": "Varanasi - Mirzapur - Prayagraj",
        "length_km": 370,
        "target_lad_m": 1.5,
        "actual_current_lad_m": 1.6,
        "min_seasonal_lad_m": 1.2,
        "dredging_status": "Fairway maintenance during monsoon and post-monsoon",
        "shallow_patches": ["Sirsa braided channel (1.3m)", "Chunar rocky sill"],
        "air_draft_clearance_m": 7.5,
        "max_vessel_dwt_allowed": 800,
        "navigation_status": "Seasonal / Light Draft Only",
        "ris_operational": False,
        "advisory": "Feasible for passenger ferries, Ro-Pax, and shallow-draft barges (draft <= 1.4m). Commercial bulk tranships at Varanasi MMT."
    },
    "NW2_DHB_PND": {
        "stretch_id": "NW2_DHB_PND",
        "waterway_id": "NW-2",
        "stretch_name": "Dhubri - Jogighopa - Pandu (Guwahati)",
        "length_km": 260,
        "target_lad_m": 2.5,
        "actual_current_lad_m": 2.5,
        "min_seasonal_lad_m": 2.0,
        "dredging_status": "Year-round maintenance dredging on Brahmaputra braided channels",
        "shallow_patches": ["Pancharatna narrows", "Goalpara bend (2.2m)"],
        "air_draft_clearance_m": 8.0,
        "max_vessel_dwt_allowed": 2000,
        "navigation_status": "Normal Navigable",
        "ris_operational": True,
        "advisory": "Strong river current during monsoon (3.5 to 5.0 knots). High engine power required for upstream transit."
    },
    "NW5_PNK_PRD": {
        "stretch_id": "NW5_PNK_PRD",
        "waterway_id": "NW-5",
        "stretch_name": "Pankpal (Kalinganagar) - Dhamra - Paradip",
        "length_km": 185,
        "target_lad_m": 2.8,
        "actual_current_lad_m": 2.9,
        "min_seasonal_lad_m": 2.5,
        "dredging_status": "Tidal delta dredged fairway maintained with Paradip Port Trust support",
        "shallow_patches": ["Kharsua confluence (2.6m)", "Mahanadi outfall bar"],
        "air_draft_clearance_m": 10.0,
        "max_vessel_dwt_allowed": 2500,
        "navigation_status": "Normal Navigable (High bulk steel and coal transit)",
        "ris_operational": True,
        "advisory": "Excellent draft clearance for 2,000 DWT steel-carrying barges directly connecting Kalinganagar steel hub to Paradip bulk berths."
    },
    "NW97_NMK_HMN": {
        "stretch_id": "NW97_NMK_HMN",
        "waterway_id": "NW-97",
        "stretch_name": "Namkhana - Raimangal - Hemnagar (Sundarbans Protocol)",
        "length_km": 172,
        "target_lad_m": 3.5,
        "actual_current_lad_m": 3.8,
        "min_seasonal_lad_m": 3.2,
        "dredging_status": "Tidal estuarine deep channel with natural scours",
        "shallow_patches": ["Bidya river junction (3.2m during lowest spring tide)"],
        "air_draft_clearance_m": 12.0,
        "max_vessel_dwt_allowed": 3000,
        "navigation_status": "Unrestricted Deep Fairway",
        "ris_operational": True,
        "advisory": "Heaviest cargo volume in India. Average 80-120 barge transits daily. Pilots mandatory for international protocol stretch."
    }
}

# Key River Stretches, Route Distances, Transit Dynamics, & Multi-Modal Comparison
ROUTE_DISTANCES_TRANSIT = {
    "haldia_to_varanasi": {
        "route_id": "haldia_to_varanasi",
        "waterway_id": "NW-1",
        "origin": "Haldia MMT / Port",
        "destination": "Varanasi MMT",
        "river_distance_km": 1250,
        "rail_distance_km": 820,
        "road_distance_km": 890,
        "river_current_downstream_knots": 2.2,
        "river_current_upstream_knots": 2.2,
        "upstream_transit_days": 6.8,
        "downstream_transit_days": 4.5,
        "typical_vessel": "Class-III Self-Propelled Barge (1,200 DWT)",
        "iwt_freight_inr_per_ton": 1325,
        "rail_freight_inr_per_ton": 1840,
        "road_freight_inr_per_ton": 2850,
        "savings_vs_rail_pct": 28.0,
        "savings_vs_road_pct": 53.5,
        "co2_emissions_iwt_kg_ton": 22.5,
        "co2_emissions_rail_kg_ton": 34.8,
        "co2_emissions_road_kg_ton": 78.2
    },
    "haldia_to_patna": {
        "route_id": "haldia_to_patna",
        "waterway_id": "NW-1",
        "origin": "Haldia MMT",
        "destination": "Patna / Kalughat Terminal",
        "river_distance_km": 955,
        "rail_distance_km": 610,
        "road_distance_km": 660,
        "river_current_downstream_knots": 2.0,
        "river_current_upstream_knots": 2.0,
        "upstream_transit_days": 5.2,
        "downstream_transit_days": 3.6,
        "typical_vessel": "Class-IV Self-Propelled Barge (2,000 DWT)",
        "iwt_freight_inr_per_ton": 1012,
        "rail_freight_inr_per_ton": 1420,
        "road_freight_inr_per_ton": 2180,
        "savings_vs_rail_pct": 28.7,
        "savings_vs_road_pct": 53.6,
        "co2_emissions_iwt_kg_ton": 17.2,
        "co2_emissions_rail_kg_ton": 26.5,
        "co2_emissions_road_kg_ton": 59.5
    },
    "kolkata_to_pandu": {
        "route_id": "kolkata_to_pandu",
        "waterway_id": "NW-1 & NW-2 via IBPR",
        "origin": "Kolkata / Haldia",
        "destination": "Pandu Port (Guwahati)",
        "river_distance_km": 1530,
        "rail_distance_km": 1020,
        "road_distance_km": 1080,
        "river_current_downstream_knots": 2.8,
        "river_current_upstream_knots": 2.8,
        "upstream_transit_days": 8.5,
        "downstream_transit_days": 5.8,
        "typical_vessel": "Self-Propelled Barge (1,800 DWT)",
        "iwt_freight_inr_per_ton": 1620,
        "rail_freight_inr_per_ton": 2250,
        "road_freight_inr_per_ton": 3450,
        "savings_vs_rail_pct": 28.0,
        "savings_vs_road_pct": 53.0,
        "co2_emissions_iwt_kg_ton": 27.5,
        "co2_emissions_rail_kg_ton": 43.3,
        "co2_emissions_road_kg_ton": 97.2
    },
    "kalinganagar_to_paradip": {
        "route_id": "kalinganagar_to_paradip",
        "waterway_id": "NW-5",
        "origin": "Pankpal (Kalinganagar Steel Hub)",
        "destination": "Paradip Port Bulk Berths",
        "river_distance_km": 185,
        "rail_distance_km": 160,
        "road_distance_km": 175,
        "river_current_downstream_knots": 1.2,
        "river_current_upstream_knots": 1.2,
        "upstream_transit_days": 1.2,
        "downstream_transit_days": 0.9,
        "typical_vessel": "Heavy Dumb Barge Flotilla (2,500 DWT)",
        "iwt_freight_inr_per_ton": 215,
        "rail_freight_inr_per_ton": 380,
        "road_freight_inr_per_ton": 590,
        "savings_vs_rail_pct": 43.4,
        "savings_vs_road_pct": 63.6,
        "co2_emissions_iwt_kg_ton": 3.3,
        "co2_emissions_rail_kg_ton": 6.8,
        "co2_emissions_road_kg_ton": 15.4
    },
    "kolaghat_to_hemnagar": {
        "route_id": "kolaghat_to_hemnagar",
        "waterway_id": "NW-86 / NW-97",
        "origin": "Kolaghat Fly Ash Terminal",
        "destination": "Hemnagar Customs (Bangladesh Border)",
        "river_distance_km": 210,
        "rail_distance_km": 245,
        "road_distance_km": 260,
        "river_current_downstream_knots": 1.5,
        "river_current_upstream_knots": 1.5,
        "upstream_transit_days": 1.4,
        "downstream_transit_days": 1.0,
        "typical_vessel": "Fly Ash Pneumatic Barge (1,500 DWT)",
        "iwt_freight_inr_per_ton": 240,
        "rail_freight_inr_per_ton": 430,
        "road_freight_inr_per_ton": 680,
        "savings_vs_rail_pct": 44.2,
        "savings_vs_road_pct": 64.7,
        "co2_emissions_iwt_kg_ton": 3.8,
        "co2_emissions_rail_kg_ton": 10.4,
        "co2_emissions_road_kg_ton": 23.4
    }
}

# Freight Collected, Tariffs & Modal Economic Benchmarks
FREIGHT_ECONOMICS = {
    "modal_cost_per_ton_km_inr": {
        "inland_waterways": 1.06,
        "railways": 1.41,
        "highways_road": 2.28
    },
    "fuel_efficiency_km_per_liter_per_ton": {
        "inland_waterways": 105,
        "railways": 85,
        "highways_road": 24
    },
    "annual_freight_collected_cr": {
        "FY_2020_21": 890,
        "FY_2021_22": 1180,
        "FY_2022_23": 1420,
        "FY_2023_24": 1560,
        "projected_FY2030": 3400
    },
    "average_terminal_handling_charges_inr_per_ton": {
        "general_bulk": 45.0,
        "finished_steel": 65.0,
        "container_teu": 850.0,
        "ro_ro_truck": 1200.0
    },
    "national_logistics_cost_savings_cr_annual": 3850,
    "carbon_reduction_mt_annual": 4.8
}

# Private Companies & Public Sector Undertakings active in IWT
IWT_OPERATORS = [
    {
        "name": "Inland Waterways Authority of India (IWAI)",
        "entity_type": "Statutory Authority / Regulator (Govt. of India)",
        "role": "Fairway development, LAD maintenance, terminals, RIS management, hydrographic surveys",
        "headquarters": "Noida, Uttar Pradesh",
        "key_initiatives": ["Jal Marg Vikas Project ($737M World Bank)", "Arth Ganga", "PM Gati Shakti IWT nodes"]
    },
    {
        "name": "Inland & Coastal Shipping Ltd (ICSL - SCI Subsidiary)",
        "entity_type": "Central Public Sector Undertaking (CPSE)",
        "role": "Dedicated coastal and inland barge operations for PSU cargo (SAIL, NTPC, IOCL)",
        "headquarters": "Mumbai / Kolkata",
        "fleet_size_barges": 24
    },
    {
        "name": "Adani Logistics Ltd (Waterways Division)",
        "entity_type": "Private Conglomerate",
        "role": "Bulk agri-commodities, container movement on NW-1 and NW-2, terminal management",
        "headquarters": "Ahmedabad, Gujarat",
        "fleet_size_barges": 18
    },
    {
        "name": "Jindal Waterways Ltd (Jindal Steel & Power)",
        "entity_type": "Private Industrial Operator",
        "role": "Captive and commercial movement of finished steel, billets, plates, and coal in Odisha/Bengal",
        "headquarters": "New Delhi / Angul",
        "fleet_size_barges": 14
    },
    {
        "name": "Tata Steel Logistics (IWT Coastal-River Division)",
        "entity_type": "Private Industrial Operator",
        "role": "Multi-modal steel coil exports from Kalinganagar/Jamshedpur to Haldia & Bangladesh via NW-5 & NW-97",
        "headquarters": "Kolkata, West Bengal",
        "fleet_size_barges": 12
    },
    {
        "name": "SAIL (Steel Authority of India Ltd) - Waterways Wing",
        "entity_type": "Maharatna CPSE",
        "role": "Pioneering pilot shipments of steel coils from Haldia/DSP to Varanasi and Guwahati via NW-1 & NW-2",
        "headquarters": "New Delhi",
        "fleet_size_barges": 8
    },
    {
        "name": "Ultratech Cement (Waterborne Logistics)",
        "entity_type": "Private Cement Major",
        "role": "Bulk cement and clinker transportation across coastal and inland river corridors",
        "headquarters": "Mumbai, Maharashtra",
        "fleet_size_barges": 16
    },
    {
        "name": "Ocean Sparkle Ltd (Adani Group)",
        "entity_type": "Private Marine Services",
        "role": "Pusher tugs, barge flotillas, harbour towing, lightering, and dredging services",
        "headquarters": "Hyderabad, Telangana",
        "fleet_size_barges": 30
    },
    {
        "name": "Antara River Cruises / Heritage River Journeys",
        "entity_type": "Private River Tourism Operator",
        "role": "Operators of MV Ganga Vilas luxury river cruiser on the world's longest 3,200 km waterway voyage",
        "headquarters": "Kolkata, West Bengal",
        "fleet_size_barges": 6
    }
]

# Passenger Movement & River Tourism
PASSENGER_MOVEMENT = {
    "annual_passengers_carried_millions": 84.5,
    "ro_pax_vehicles_carried_thousands": 420,
    "passenger_kilometers_billion": 2.45,
    "key_passenger_corridors": [
        {"route": "Kolkata - Howrah River Ferry Services (NW-1)", "annual_passengers_millions": 48.0, "type": "Urban Commuter Ferry"},
        {"route": "Majuli Island - Jorhat Ferries & Ro-Pax (NW-2)", "annual_passengers_millions": 3.8, "type": "Island Lifeline & Ro-Pax"},
        {"route": "Goa Mandovi & Zuari River Ferries (NW-68 / NW-111)", "annual_passengers_millions": 9.2, "type": "Tourist & Commuter Ferry"},
        {"route": "Sahibganj - Manihari Ro-Ro Ferry (NW-1)", "annual_passengers_millions": 2.4, "type": "Interstate Commercial Ro-Pax"},
        {"route": "Kerala Backwaters & Kochi Water Metro (NW-3)", "annual_passengers_millions": 18.5, "type": "Eco-Tourism & Water Metro Electric Hybrid"},
        {"route": "MV Ganga Vilas / Heritage Luxury Cruises (NW-1 to NW-2 via IBPR)", "annual_passengers_millions": 0.05, "type": "Ultra-Luxury International River Cruise"}
    ],
    "cruise_vessels_operating": 22,
    "water_metro_electric_ferries": 15
}

# Safety Records, Navigation Aids, & Accidents
ACCIDENTS_AND_SAFETY = {
    "safety_record_period": "2019-2024 (5-Year Audit)",
    "total_recorded_incidents": 14,
    "fatalities": 0,
    "groundings_minor": 9,
    "collisions": 3,
    "capsizes_dumb_barge": 2,
    "causes_breakdown_pct": {
        "sudden_shoaling_draft_miscalculation": 55,
        "dense_winter_fog_poor_visibility": 25,
        "mechanical_steering_engine_failure": 12,
        "unmarked_fishing_net_fouling": 8
    },
    "incident_rate_per_million_tonne_km": 0.0038,
    "safety_compliance_measures": [
        "River Information System (RIS) with VHF tracking installed on 1,390 km of NW-1",
        "Differential Global Positioning System (DGPS) 24x7 correction signals across NW-1, NW-2, NW-3",
        "Electronic Navigational Charts (ENC) compliant with IHO S-57 international standard updated bi-weekly",
        "Compulsory hydrographic survey echo-sounding before deep draft vessel transits",
        "Mandatory automated AIS transponders on all commercial vessels > 300 DWT",
        "Annual hull, stability, and firefighting certification audited by MMD / IWAI surveyors"
    ]
}
