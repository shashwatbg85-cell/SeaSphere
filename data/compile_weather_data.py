import json
import csv

# 10-day cycles observed in data:
# Let's write the exact parsed data from the OCR of the document.

page1_part1 = """2026-08-04 Dhamra 20.78 86.95 31 25
2026-08-05 Dhamra 20.78 86.95 32.3 25.6
2026-08-06 Dhamra 20.78 86.95 31.7 25
2026-08-07 Dhamra 20.78 86.95 31.2 25.6
2026-08-08 Dhamra 20.78 86.95 32.4 25
2026-08-09 Dhamra 20.78 86.95 31.9 25.6
2026-08-10 Dhamra 20.78 86.95 31.4 25
2026-08-11 Dhamra 20.78 86.95 32.6 25.6
2026-08-12 Dhamra 20.78 86.95 32.1 25
2026-08-13 Dhamra 20.78 86.95 31.5 25.6
2026-08-14 Dhamra 20.78 86.95 31 25
2026-08-15 Dhamra 20.78 86.95 32.3 25.6
2026-08-16 Dhamra 20.78 86.95 31.7 25
2026-08-17 Dhamra 20.78 86.95 31.2 25.6
2026-08-18 Dhamra 20.78 86.95 32.4 25
2026-08-19 Dhamra 20.78 86.95 31.9 25.6
2026-08-20 Dhamra 20.78 86.95 31.4 25
2026-08-21 Dhamra 20.78 86.95 32.6 25.6
2026-08-22 Dhamra 20.78 86.95 32.1 25
2026-08-23 Dhamra 20.78 86.95 31.5 25.6
2026-08-24 Dhamra 20.78 86.95 31 25
2026-08-25 Dhamra 20.78 86.95 32.3 25.6
2026-08-26 Dhamra 20.78 86.95 31.7 25
2026-08-27 Dhamra 20.78 86.95 31.2 25.6
2026-08-28 Dhamra 20.78 86.95 32.4 25
2026-08-29 Dhamra 20.78 86.95 31.9 25.6
2026-08-30 Dhamra 20.78 86.95 31.4 25
2026-08-31 Dhamra 20.78 86.95 32.6 25.6
2026-09-01 Dhamra 20.78 86.95 32.1 25
2026-09-02 Dhamra 20.78 86.95 31.5 25.6
2026-08-04 Paradip 20.32 86.61 31 25
2026-08-05 Paradip 20.32 86.61 32.3 25.6
2026-08-06 Paradip 20.32 86.61 31.7 25
2026-08-07 Paradip 20.32 86.61 31.2 25.6
2026-08-08 Paradip 20.32 86.61 32.4 25
2026-08-09 Paradip 20.32 86.61 31.9 25.6
2026-08-10 Paradip 20.32 86.61 31.4 25
2026-08-11 Paradip 20.32 86.61 32.6 25.6
2026-08-12 Paradip 20.32 86.61 32.1 25
2026-08-13 Paradip 20.32 86.61 31.5 25.6
2026-08-14 Paradip 20.32 86.61 31 25
2026-08-15 Paradip 20.32 86.61 32.3 25.6
2026-08-16 Paradip 20.32 86.61 31.7 25"""

page2_part1 = """2026-08-17 Paradip 20.32 86.61 31.2 25.6
2026-08-18 Paradip 20.32 86.61 32.4 25
2026-08-19 Paradip 20.32 86.61 31.9 25.6
2026-08-20 Paradip 20.32 86.61 31.4 25
2026-08-21 Paradip 20.32 86.61 32.6 25.6
2026-08-22 Paradip 20.32 86.61 32.1 25
2026-08-23 Paradip 20.32 86.61 31.5 25.6
2026-08-24 Paradip 20.32 86.61 31 25
2026-08-25 Paradip 20.32 86.61 32.3 25.6
2026-08-26 Paradip 20.32 86.61 31.7 25
2026-08-27 Paradip 20.32 86.61 31.2 25.6
2026-08-28 Paradip 20.32 86.61 32.4 25
2026-08-29 Paradip 20.32 86.61 31.9 25.6
2026-08-30 Paradip 20.32 86.61 31.4 25
2026-08-31 Paradip 20.32 86.61 32.6 25.6
2026-09-01 Paradip 20.32 86.61 32.1 25
2026-09-02 Paradip 20.32 86.61 31.5 25.6
2026-08-04 Visakhapatnam 17.69 83.22 31 25
2026-08-05 Visakhapatnam 17.69 83.22 32.3 25.6
2026-08-06 Visakhapatnam 17.69 83.22 31.7 25
2026-08-07 Visakhapatnam 17.69 83.22 31.2 25.6
2026-08-08 Visakhapatnam 17.69 83.22 32.4 25
2026-08-09 Visakhapatnam 17.69 83.22 31.9 25.6
2026-08-10 Visakhapatnam 17.69 83.22 31.4 25
2026-08-11 Visakhapatnam 17.69 83.22 32.6 25.6
2026-08-12 Visakhapatnam 17.69 83.22 32.1 25
2026-08-13 Visakhapatnam 17.69 83.22 31.5 25.6
2026-08-14 Visakhapatnam 17.69 83.22 31 25
2026-08-15 Visakhapatnam 17.69 83.22 32.3 25.6
2026-08-16 Visakhapatnam 17.69 83.22 31.7 25
2026-08-17 Visakhapatnam 17.69 83.22 31.2 25.6
2026-08-18 Visakhapatnam 17.69 83.22 32.4 25
2026-08-19 Visakhapatnam 17.69 83.22 31.9 25.6
2026-08-20 Visakhapatnam 17.69 83.22 31.4 25
2026-08-21 Visakhapatnam 17.69 83.22 32.6 25.6
2026-08-22 Visakhapatnam 17.69 83.22 32.1 25
2026-08-23 Visakhapatnam 17.69 83.22 31.5 25.6
2026-08-24 Visakhapatnam 17.69 83.22 31 25
2026-08-25 Visakhapatnam 17.69 83.22 32.3 25.6
2026-08-26 Visakhapatnam 17.69 83.22 31.7 25
2026-08-27 Visakhapatnam 17.69 83.22 31.2 25.6
2026-08-28 Visakhapatnam 17.69 83.22 32.4 25
2026-08-29 Visakhapatnam 17.69 83.22 31.9 25.6
2026-08-30 Visakhapatnam 17.69 83.22 31.4 25"""

page3_part1 = """2026-08-31 Visakhapatnam 17.69 83.22 32.6 25.6
2026-09-01 Visakhapatnam 17.69 83.22 32.1 25
2026-09-02 Visakhapatnam 17.69 83.22 31.5 25.6
2026-08-04 Kolkata 22.55 88.33 31 25
2026-08-05 Kolkata 22.55 88.33 32.3 25.6
2026-08-06 Kolkata 22.55 88.33 31.7 25
2026-08-07 Kolkata 22.55 88.33 31.2 25.6
2026-08-08 Kolkata 22.55 88.33 32.4 25
2026-08-09 Kolkata 22.55 88.33 31.9 25.6
2026-08-10 Kolkata 22.55 88.33 31.4 25
2026-08-11 Kolkata 22.55 88.33 32.6 25.6
2026-08-12 Kolkata 22.55 88.33 32.1 25
2026-08-13 Kolkata 22.55 88.33 31.5 25.6
2026-08-14 Kolkata 22.55 88.33 31 25
2026-08-15 Kolkata 22.55 88.33 32.3 25.6
2026-08-16 Kolkata 22.55 88.33 31.7 25
2026-08-17 Kolkata 22.55 88.33 31.2 25.6
2026-08-18 Kolkata 22.55 88.33 32.4 25
2026-08-19 Kolkata 22.55 88.33 31.9 25.6
2026-08-20 Kolkata 22.55 88.33 31.4 25
2026-08-21 Kolkata 22.55 88.33 32.6 25.6
2026-08-22 Kolkata 22.55 88.33 32.1 25
2026-08-23 Kolkata 22.55 88.33 31.5 25.6
2026-08-24 Kolkata 22.55 88.33 31 25
2026-08-25 Kolkata 22.55 88.33 32.3 25.6
2026-08-26 Kolkata 22.55 88.33 31.7 25
2026-08-27 Kolkata 22.55 88.33 31.2 25.6
2026-08-28 Kolkata 22.55 88.33 32.4 25
2026-08-29 Kolkata 22.55 88.33 31.9 25.6
2026-08-30 Kolkata 22.55 88.33 31.4 25
2026-08-31 Kolkata 22.55 88.33 32.6 25.6
2026-09-01 Kolkata 22.55 88.33 32.1 25
2026-09-02 Kolkata 22.55 88.33 31.5 25.6
2026-08-04 Chennai 13.1 80.29 31 25
2026-08-05 Chennai 13.1 80.29 32.3 25.6
2026-08-06 Chennai 13.1 80.29 31.7 25
2026-08-07 Chennai 13.1 80.29 31.2 25.6
2026-08-08 Chennai 13.1 80.29 32.4 25
2026-08-09 Chennai 13.1 80.29 31.9 25.6
2026-08-10 Chennai 13.1 80.29 31.4 25
2026-08-11 Chennai 13.1 80.29 32.6 25.6
2026-08-12 Chennai 13.1 80.29 32.1 25
2026-08-13 Chennai 13.1 80.29 31.5 25.6
2026-08-14 Chennai 13.1 80.29 31 25"""

page4_part1 = """2026-08-15 Chennai 13.1 80.29 32.3 25.6
2026-08-16 Chennai 13.1 80.29 31.7 25
2026-08-17 Chennai 13.1 80.29 31.2 25.6
2026-08-18 Chennai 13.1 80.29 32.4 25
2026-08-19 Chennai 13.1 80.29 31.9 25.6
2026-08-20 Chennai 13.1 80.29 31.4 25
2026-08-21 Chennai 13.1 80.29 32.6 25.6
2026-08-22 Chennai 13.1 80.29 32.1 25
2026-08-23 Chennai 13.1 80.29 31.5 25.6
2026-08-24 Chennai 13.1 80.29 31 25
2026-08-25 Chennai 13.1 80.29 32.3 25.6
2026-08-26 Chennai 13.1 80.29 31.7 25
2026-08-27 Chennai 13.1 80.29 31.2 25.6
2026-08-28 Chennai 13.1 80.29 32.4 25
2026-08-29 Chennai 13.1 80.29 31.9 25.6
2026-08-30 Chennai 13.1 80.29 31.4 25
2026-08-31 Chennai 13.1 80.29 32.6 25.6
2026-09-01 Chennai 13.1 80.29 32.1 25
2026-09-02 Chennai 13.1 80.29 31.5 25.6
2026-08-04 Kamarajar 13.25 80.32 31 25
2026-08-05 Kamarajar 13.25 80.32 32.3 25.6
2026-08-06 Kamarajar 13.25 80.32 31.7 25
2026-08-07 Kamarajar 13.25 80.32 31.2 25.6
2026-08-08 Kamarajar 13.25 80.32 32.4 25
2026-08-09 Kamarajar 13.25 80.32 31.9 25.6
2026-08-10 Kamarajar 13.25 80.32 31.4 25
2026-08-11 Kamarajar 13.25 80.32 32.6 25.6
2026-08-12 Kamarajar 13.25 80.32 32.1 25
2026-08-13 Kamarajar 13.25 80.32 31.5 25.6
2026-08-14 Kamarajar 13.25 80.32 31 25
2026-08-15 Kamarajar 13.25 80.32 32.3 25.6
2026-08-16 Kamarajar 13.25 80.32 31.7 25
2026-08-17 Kamarajar 13.25 80.32 31.2 25.6
2026-08-18 Kamarajar 13.25 80.32 32.4 25
2026-08-19 Kamarajar 13.25 80.32 31.9 25.6
2026-08-20 Kamarajar 13.25 80.32 31.4 25
2026-08-21 Kamarajar 13.25 80.32 32.6 25.6
2026-08-22 Kamarajar 13.25 80.32 32.1 25
2026-08-23 Kamarajar 13.25 80.32 31.5 25.6
2026-08-24 Kamarajar 13.25 80.32 31 25
2026-08-25 Kamarajar 13.25 80.32 32.3 25.6
2026-08-26 Kamarajar 13.25 80.32 31.7 25
2026-08-27 Kamarajar 13.25 80.32 31.2 25.6
2026-08-28 Kamarajar 13.25 80.32 32.4 25"""

page5_part1 = """2026-08-29 Kamarajar 13.25 80.32 31.9 25.6
2026-08-30 Kamarajar 13.25 80.32 31.4 25
2026-08-31 Kamarajar 13.25 80.32 32.6 25.6
2026-09-01 Kamarajar 13.25 80.32 32.1 25
2026-09-02 Kamarajar 13.25 80.32 31.5 25.6
2026-08-04 V.O.Chidambaranar 8.8 78.2 31 25
2026-08-05 V.O.Chidambaranar 8.8 78.2 32.3 25.6
2026-08-06 V.O.Chidambaranar 8.8 78.2 31.7 25
2026-08-07 V.O.Chidambaranar 8.8 78.2 31.2 25.6
2026-08-08 V.O.Chidambaranar 8.8 78.2 32.4 25
2026-08-09 V.O.Chidambaranar 8.8 78.2 31.9 25.6
2026-08-10 V.O.Chidambaranar 8.8 78.2 31.4 25
2026-08-11 V.O.Chidambaranar 8.8 78.2 32.6 25.6
2026-08-12 V.O.Chidambaranar 8.8 78.2 32.1 25
2026-08-13 V.O.Chidambaranar 8.8 78.2 31.5 25.6
2026-08-14 V.O.Chidambaranar 8.8 78.2 31 25
2026-08-15 V.O.Chidambaranar 8.8 78.2 32.3 25.6
2026-08-16 V.O.Chidambaranar 8.8 78.2 31.7 25
2026-08-17 V.O.Chidambaranar 8.8 78.2 31.2 25.6
2026-08-18 V.O.Chidambaranar 8.8 78.2 32.4 25
2026-08-19 V.O.Chidambaranar 8.8 78.2 31.9 25.6
2026-08-20 V.O.Chidambaranar 8.8 78.2 31.4 25
2026-08-21 V.O.Chidambaranar 8.8 78.2 32.6 25.6
2026-08-22 V.O.Chidambaranar 8.8 78.2 32.1 25
2026-08-23 V.O.Chidambaranar 8.8 78.2 31.5 25.6
2026-08-24 V.O.Chidambaranar 8.8 78.2 31 25
2026-08-25 V.O.Chidambaranar 8.8 78.2 32.3 25.6
2026-08-26 V.O.Chidambaranar 8.8 78.2 31.7 25
2026-08-27 V.O.Chidambaranar 8.8 78.2 31.2 25.6
2026-08-28 V.O.Chidambaranar 8.8 78.2 32.4 25
2026-08-29 V.O.Chidambaranar 8.8 78.2 31.9 25.6
2026-08-30 V.O.Chidambaranar 8.8 78.2 31.4 25
2026-08-31 V.O.Chidambaranar 8.8 78.2 32.6 25.6
2026-09-01 V.O.Chidambaranar 8.8 78.2 32.1 25
2026-09-02 V.O.Chidambaranar 8.8 78.2 31.5 25.6"""

# Now the 10-day cycle for columns: precipitation_mm, max_wind_kmh, weather_code
# Notice the values in pages 6, 7, 8, 9, 10:
# Day 1: 0, 18, 1
# Day 2: 2.4, 21.8, 2
# Day 3: 8.6, 25.5, 61
# Day 4: 0, 19.2, 3
# Day 5: 14.2, 23, 63
# Day 6: 3.1, 26.8, 80
# Day 7: 0, 20.5, 1
# Day 8: 5.8, 24.2, 61
# Day 9: 0, 18, 2
# Day 10: 1.2, 21.8, 3
# Day 11: 0, 25.5, 1
# Day 12: 2.4, 19.2, 2
# Day 13: 8.6, 23, 61
# Day 14: 0, 26.8, 3
# Day 15: 14.2, 20.5, 63
# Day 16: 3.1, 24.2, 80
# Day 17: 0, 18, 1
# Day 18: 5.8, 21.8, 61
# Day 19: 0, 25.5, 2
# Day 20: 1.2, 19.2, 3
# Day 21: 0, 23, 1
# Day 22: 2.4, 26.8, 2
# Day 23: 8.6, 20.5, 61
# Day 24: 0, 24.2, 3
# Day 25: 14.2, 18, 63
# Day 26: 3.1, 21.8, 80
# Day 27: 0, 25.5, 1
# Day 28: 5.8, 19.2, 61
# Day 29: 0, 23, 2
# Day 30: 1.2, 26.8, 3

part2_per_port = [
    (0.0, 18.0, 1),
    (2.4, 21.8, 2),
    (8.6, 25.5, 61),
    (0.0, 19.2, 3),
    (14.2, 23.0, 63),
    (3.1, 26.8, 80),
    (0.0, 20.5, 1),
    (5.8, 24.2, 61),
    (0.0, 18.0, 2),
    (1.2, 21.8, 3),
    (0.0, 25.5, 1),
    (2.4, 19.2, 2),
    (8.6, 23.0, 61),
    (0.0, 26.8, 3),
    (14.2, 20.5, 63),
    (3.1, 24.2, 80),
    (0.0, 18.0, 1),
    (5.8, 21.8, 61),
    (0.0, 25.5, 2),
    (1.2, 19.2, 3),
    (0.0, 23.0, 1),
    (2.4, 26.8, 2),
    (8.6, 20.5, 61),
    (0.0, 24.2, 3),
    (14.2, 18.0, 63),
    (3.1, 21.8, 80),
    (0.0, 25.5, 1),
    (5.8, 19.2, 61),
    (0.0, 23.0, 2),
    (1.2, 26.8, 3)
]

WEATHER_DESCRIPTIONS = {
    1: {"condition": "Mainly Clear", "icon": "☀️", "risk": "Low", "operations": "Normal berthing & unloading"},
    2: {"condition": "Partly Cloudy", "icon": "⛅", "risk": "Low", "operations": "Optimal cargo handling"},
    3: {"condition": "Overcast", "icon": "☁️", "risk": "Low-Moderate", "operations": "Standard operations"},
    61: {"condition": "Slight Rain", "icon": "🌦️", "risk": "Moderate", "operations": "Moisture-sensitive hatches monitor"},
    63: {"condition": "Moderate Rain", "icon": "🌧️", "risk": "Elevated", "operations": "Temporary hatch closure on coal/limestone"},
    80: {"condition": "Rain Showers / Wind Swell", "icon": "⛈️", "risk": "High Alert", "operations": "Lightering caution & crane wind warning"}
}

all_part1_lines = []
for block in [page1_part1, page2_part1, page3_part1, page4_part1, page5_part1]:
    for line in block.strip().split("\n"):
        line = line.strip()
        if line:
            all_part1_lines.append(line)

print(f"Total part 1 rows: {len(all_part1_lines)}")

rows = []
for i, line in enumerate(all_part1_lines):
    parts = line.split()
    date = parts[0]
    location = parts[1]
    lat = float(parts[2])
    lon = float(parts[3])
    t_max = float(parts[4])
    t_min = float(parts[5])
    
    port_day_idx = i % 30
    precip, wind, code = part2_per_port[port_day_idx]
    
    weather_meta = WEATHER_DESCRIPTIONS.get(int(code), {
        "condition": "Unknown", "icon": "🌤️", "risk": "Moderate", "operations": "Standard monitoring"
    })
    
    rows.append({
        "date": date,
        "location": location,
        "latitude": lat,
        "longitude": lon,
        "temperature_max_c": t_max,
        "temperature_min_c": t_min,
        "precipitation_mm": precip,
        "max_wind_kmh": wind,
        "weather_code": int(code),
        "condition": weather_meta["condition"],
        "icon": weather_meta["icon"],
        "operational_risk": weather_meta["risk"],
        "operational_impact": weather_meta["operations"]
    })

# Write to data/port_weather_forecast.csv
csv_path = "data/port_weather_forecast.csv"
fieldnames = ["date", "location", "latitude", "longitude", "temperature_max_c", "temperature_min_c", "precipitation_mm", "max_wind_kmh", "weather_code"]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r[k] for k in fieldnames})
print(f"Saved CSV with {len(rows)} rows to {csv_path}")

# Write to data/port_weather_forecast.json and static/data/port_weather_forecast.json
# Structure: organized both flat list and by port
by_port = {}
for r in rows:
    loc = r["location"]
    if loc not in by_port:
        by_port[loc] = {
            "location": loc,
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "forecast_days": []
        }
    by_port[loc]["forecast_days"].append(r)

# Summary statistics per port
for loc, data in by_port.items():
    days = data["forecast_days"]
    max_t = max(d["temperature_max_c"] for d in days)
    min_t = min(d["temperature_min_c"] for d in days)
    max_wind = max(d["max_wind_kmh"] for d in days)
    total_rain = round(sum(d["precipitation_mm"] for d in days), 1)
    rainy_days = sum(1 for d in days if d["precipitation_mm"] > 0)
    high_wind_days = sum(1 for d in days if d["max_wind_kmh"] >= 24)
    data["summary"] = {
        "horizon_days": len(days),
        "start_date": days[0]["date"],
        "end_date": days[-1]["date"],
        "max_temperature_c": max_t,
        "min_temperature_c": min_t,
        "peak_wind_kmh": max_wind,
        "total_precipitation_mm": total_rain,
        "rainy_days_count": rainy_days,
        "high_wind_days_count": high_wind_days,
        "weather_risk_level": "High" if total_rain > 60 or high_wind_days >= 8 else "Moderate"
    }

output_payload = {
    "status": "success",
    "meta": {
        "title": "East Coast Maritime Port Weather & Metocean Forecast",
        "time_range": f"{rows[0]['date']} to {rows[-1]['date']}",
        "ports_count": len(by_port),
        "total_records": len(rows),
        "ports": list(by_port.keys())
    },
    "by_port": by_port,
    "records": rows
}

for json_path in ["data/port_weather_forecast.json", "static/data/port_weather_forecast.json"]:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)
    print(f"Saved JSON to {json_path}")
