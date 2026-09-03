"""
Realistic Maritime Historical Dataset Generator for Bulk Freight to East Coast of India.
Generates comprehensive daily timeseries (2020 - 2026) capturing:
- Baltic Dry Indices (BDI, BCI, BPI, BSI)
- Marine Bunker Fuel prices (Singapore VLSFO, IFO380)
- Global commodity benchmarks (Coking Coal FOB Australia, Iron Ore CFR China, Brent Crude)
- Port congestion queues (Queensland, South Kalimantan, Bay of Bengal)
- Monsoon seasonality and geopolitical disruption factors
- Route-specific spot freight rates ($/Metric Tonne) across all major Indian import corridors.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime

def generate_historical_maritime_data(start_date="2020-01-01", end_date="2026-08-31", random_seed=42):
    np.random.seed(random_seed)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    n = len(date_range)
    
    # Time indices for seasonality and multi-year macroeconomic cycles
    days = np.arange(n)
    t = days / 365.25
    day_of_year = date_range.dayofyear.values
    month = date_range.month.values
    
    # 1. Macro-cycle driver (COVID crash early 2020, 2021-2022 supercycle, 2023 normalization, 2024-2026 steady growth)
    macro_cycle = (
        1.0 
        - 0.35 * np.exp(-((days - 75) ** 2) / (2 * 45 ** 2))   # Q1 2020 COVID dip
        + 1.80 * np.exp(-((days - 650) ** 2) / (2 * 180 ** 2))  # Late 2021 post-pandemic shipping squeeze
        + 1.40 * np.exp(-((days - 880) ** 2) / (2 * 120 ** 2))  # Mid 2022 commodity boom / geopolitical shock
        + 0.25 * np.sin(2 * np.pi * t * 0.8)                   # Cyclical 1.2-year freight cycle
    )
    
    # 2. Seasonality (Bay of Bengal Monsoon June-Sept, Q1 Chinese New Year / Aussie cyclone lull)
    monsoon_factor = 1.0 + 0.18 * np.exp(-((day_of_year - 205) ** 2) / (2 * 40 ** 2))  # Peaks July/August
    q1_aussie_wet = 1.0 + 0.12 * np.exp(-((day_of_year - 45) ** 2) / (2 * 30 ** 2))    # Peaks Feb (Queensland rain/cyclones)
    seasonal_composite = monsoon_factor * q1_aussie_wet
    
    # 3. Base Commodity & Energy Indicators
    # Brent Crude ($/bbl)
    crude_trend = 60.0 + 18.0 * t + 35.0 * np.exp(-((days - 850) ** 2) / (2 * 100 ** 2))
    crude_noise = np.cumsum(np.random.normal(0, 0.9, n)) * 0.15
    crude_brent = np.clip(crude_trend + crude_noise, 25.0, 125.0)
    
    # Singapore VLSFO Bunker Fuel ($/MT) - tightly coupled to crude
    vlsfo_spread = 220.0 + np.random.normal(0, 15, n)
    bunker_vlsfo = np.clip(crude_brent * 5.8 + vlsfo_spread, 320.0, 1120.0)
    bunker_ifo380 = bunker_vlsfo * 0.78 + np.random.normal(0, 12, n)
    
    # Premium Coking Coal FOB Australia ($/MT)
    coal_base = 160.0 + 220.0 * np.exp(-((days - 800) ** 2) / (2 * 140 ** 2)) + 60.0 * np.sin(2 * np.pi * t * 0.5)
    coal_noise = np.cumsum(np.random.normal(0, 2.5, n)) * 0.2
    coking_coal_fob = np.clip(coal_base + coal_noise, 105.0, 620.0)
    
    # Iron Ore 62% CFR China ($/MT)
    iron_ore = np.clip(85.0 + 80.0 * np.exp(-((days - 550) ** 2) / (2 * 110 ** 2)) + np.random.normal(0, 4.0, n), 75.0, 230.0)
    
    # 4. Baltic Dry Indices
    # Baltic Capesize Index (BCI) - highly volatile, high beta
    bci_base = 1800.0 * macro_cycle * seasonal_composite
    bci_ar = np.zeros(n)
    bci_ar[0] = 1800
    for i in range(1, n):
        bci_ar[i] = 0.95 * bci_ar[i-1] + 0.05 * bci_base[i] + np.random.normal(0, 110)
    bci = np.clip(bci_ar, 450.0, 10500.0)
    
    # Baltic Panamax Index (BPI)
    bpi_base = 1400.0 * (macro_cycle ** 0.85) * monsoon_factor
    bpi_ar = np.zeros(n)
    bpi_ar[0] = 1400
    for i in range(1, n):
        bpi_ar[i] = 0.96 * bpi_ar[i-1] + 0.04 * bpi_base[i] + np.random.normal(0, 65)
    bpi = np.clip(bpi_ar, 550.0, 4500.0)
    
    # Baltic Supramax Index (BSI)
    bsi_ar = np.zeros(n)
    bsi_ar[0] = 1000
    for i in range(1, n):
        bsi_ar[i] = 0.97 * bsi_ar[i-1] + 0.03 * (1150.0 * (macro_cycle[i] ** 0.75)) + np.random.normal(0, 45)
    bsi = np.clip(bsi_ar, 480.0, 3900.0)
    
    # Baltic Dry Index (Composite weighted BDI)
    bdi = 0.40 * bci + 0.35 * bpi + 0.25 * bsi
    
    # 5. Port Congestion Metrics (Waiting days)
    port_congestion_aus = np.clip(4.5 + 3.5 * q1_aussie_wet + np.random.normal(0, 1.2, n), 1.5, 22.0)
    port_congestion_indo = np.clip(3.0 + 2.0 * monsoon_factor + np.random.normal(0, 0.9, n), 1.0, 14.0)
    port_congestion_india_east = np.clip(2.5 + 2.8 * (monsoon_factor - 1.0) * 4.0 + np.random.normal(0, 0.8, n), 1.0, 12.0)
    
    # 6. Route-Specific Freight Rates ($/Metric Tonne)
    # Australia (Hay Point) -> Paradip (Capesize, ~5050 nm)
    fuel_comp_aus_cape = (5050 / (12.5 * 24)) * 44.0 * (bunker_vlsfo / 175000)
    freight_aus_paradip_cape = np.clip(
        fuel_comp_aus_cape + (bci / 1000.0) * 2.85 + 4.5 + np.random.normal(0, 0.35, n),
        8.20, 32.50
    )
    
    # Australia -> Vizag (Capesize, ~4900 nm)
    freight_aus_vizag_cape = freight_aus_paradip_cape * 0.97 + np.random.normal(0, 0.15, n)
    
    # Australia -> Haldia (Panamax lightering route, ~5150 nm)
    freight_aus_haldia_panamax = np.clip(
        freight_aus_paradip_cape * 1.32 + (bpi / 1000.0) * 1.6 + np.random.normal(0, 0.45, n),
        12.50, 42.00
    )
    
    # Indonesia (Taboneo) -> Paradip (Panamax, ~2250 nm)
    fuel_comp_indo_pana = (2250 / (13.0 * 24)) * 26.0 * (bunker_vlsfo / 75000)
    freight_indo_paradip_panamax = np.clip(
        fuel_comp_indo_pana + (bpi / 1000.0) * 1.85 + 2.8 + np.random.normal(0, 0.25, n),
        5.40, 21.50
    )
    
    # Indonesia -> Vizag (Supramax, ~2100 nm)
    freight_indo_vizag_supramax = freight_indo_paradip_panamax * 1.15 + np.random.normal(0, 0.20, n)
    
    # South Africa (Richards Bay) -> Vizag (Capesize, ~4500 nm)
    freight_rsa_vizag_cape = np.clip(
        freight_aus_vizag_cape * 0.94 + (bci / 1000.0) * 0.75 + np.random.normal(0, 0.30, n),
        9.00, 31.00
    )
    
    # USA (Hampton Roads) -> Paradip (Capesize via Cape of Good Hope, ~11650 nm)
    fuel_comp_usa = (11650 / (12.5 * 24)) * 44.0 * (bunker_vlsfo / 175000)
    freight_usa_paradip_cape = np.clip(
        fuel_comp_usa + (bci / 1000.0) * 4.90 + 14.5 + np.random.normal(0, 0.65, n),
        26.00, 72.00
    )
    
    # Russia (Taman) -> Vizag (Panamax, ~5600 nm)
    freight_russia_vizag_panamax = np.clip(
        (5600 / (13.0 * 24)) * 26.0 * (bunker_vlsfo / 75000) + (bpi / 1000.0) * 2.70 + 8.5 + np.random.normal(0, 0.50, n),
        16.50, 52.00
    )
    
    # UAE (Fujairah) -> Paradip (Supramax Limestone, ~2100 nm)
    freight_uae_paradip_supramax = np.clip(
        (2100 / (13.5 * 24)) * 23.0 * (bunker_vlsfo / 58000) + (bsi / 1000.0) * 1.65 + 3.2 + np.random.normal(0, 0.25, n),
        7.10, 24.50
    )
    
    # Create clean DataFrame
    df = pd.DataFrame({
        "date": date_range.strftime("%Y-%m-%d"),
        "bdi": np.round(bdi, 1),
        "bci": np.round(bci, 1),
        "bpi": np.round(bpi, 1),
        "bsi": np.round(bsi, 1),
        "bunker_vlsfo_singapore": np.round(bunker_vlsfo, 2),
        "bunker_ifo380_singapore": np.round(bunker_ifo380, 2),
        "crude_brent": np.round(crude_brent, 2),
        "coking_coal_fob_aus": np.round(coking_coal_fob, 2),
        "iron_ore_cfr_china": np.round(iron_ore, 2),
        "port_congestion_aus_days": np.round(port_congestion_aus, 1),
        "port_congestion_indo_days": np.round(port_congestion_indo, 1),
        "port_congestion_india_east_days": np.round(port_congestion_india_east, 1),
        "monsoon_index": np.round(monsoon_factor, 3),
        # Freight rates ($/MT)
        "freight_aus_paradip_cape": np.round(freight_aus_paradip_cape, 2),
        "freight_aus_vizag_cape": np.round(freight_aus_vizag_cape, 2),
        "freight_aus_haldia_panamax": np.round(freight_aus_haldia_panamax, 2),
        "freight_indo_paradip_panamax": np.round(freight_indo_paradip_panamax, 2),
        "freight_indo_vizag_supramax": np.round(freight_indo_vizag_supramax, 2),
        "freight_rsa_vizag_cape": np.round(freight_rsa_vizag_cape, 2),
        "freight_usa_paradip_cape": np.round(freight_usa_paradip_cape, 2),
        "freight_russia_vizag_panamax": np.round(freight_russia_vizag_panamax, 2),
        "freight_uae_paradip_supramax": np.round(freight_uae_paradip_supramax, 2),
    })
    
    return df

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(output_dir, "historical_freight.csv")
    print(f"Generating realistic maritime historical dataset to {csv_path}...")
    df = generate_historical_maritime_data()
    df.to_csv(csv_path, index=False)
    print(f"Successfully generated {len(df)} daily records from {df['date'].iloc[0]} to {df['date'].iloc[-1]}.")
    print("Sample records:\n", df.head(3).T)
