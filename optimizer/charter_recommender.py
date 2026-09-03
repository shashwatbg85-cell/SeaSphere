"""
Vessel Charter Strategy & Optimal Laycan Window Recommender.
Evaluates:
- Spot Voyage Charter vs Time Charter (TC) vs Contract of Affreightment (COA)
- Market entry timing (Urgent Buy vs Patient Wait)
- Optimal 5-day Laycan (loading window) within procurement planning horizon
- Financial savings quantification.
"""

from datetime import datetime, timedelta

class CharterRecommender:
    def __init__(self):
        pass

    def recommend_charter_strategy(self, forecast_result, cargo_tonnage=150000, max_lead_days=45):
        """
        Determines the optimal market entry window, contract structure, and laycan window.
        """
        current_spot = forecast_result["current_spot_rate"]
        horizons = forecast_result["horizons"]
        daily_traj = forecast_result["daily_trajectory"]
        as_of = datetime.strptime(forecast_result["as_of_date"], "%Y-%m-%d")
        
        # Filter trajectory up to max_lead_days
        eligible_days = [d for d in daily_traj if d["day"] <= max_lead_days]
        
        # Find day with minimum predicted rate (P50)
        min_traj_day = min(eligible_days, key=lambda x: x["p50"])
        min_rate = min_traj_day["p50"]
        optimal_day_offset = min_traj_day["day"]
        
        # Calculate optimal laycan window (5-day span around optimal day)
        laycan_start = as_of + timedelta(days=max(1, optimal_day_offset - 2))
        laycan_end = laycan_start + timedelta(days=4)
        
        rate_difference = current_spot - min_rate
        pct_savings = (rate_difference / current_spot) * 100
        total_freight_savings = round(rate_difference * cargo_tonnage, 2)
        
        # Determine Market Entry Timing
        # Look at short-term 7d and 15d trend
        p7_change = horizons[0]["change_pct"] if len(horizons) > 0 else 0
        p15_change = horizons[1]["change_pct"] if len(horizons) > 1 else 0
        
        if p7_change > 3.5 or p15_change > 5.0:
            market_action = "BOOK SPOT IMMEDIATELY"
            timing_urgency = "HIGH (Escalating Market)"
            timing_advice = (
                f"Ocean freight is in an upward momentum (+{max(p7_change, p15_change):.1f}% expected over next 15 days). "
                f"Enter the market within 48 to 72 hours to fix tonnage before spot fixtures tighten."
            )
            optimal_laycan_str = f"{as_of.strftime('%d %b')} – {(as_of + timedelta(days=7)).strftime('%d %b %Y')}"
            projected_charter_rate = current_spot
            potential_savings = 0.0
        elif p15_change < -3.0 or rate_difference > 0.40:
            market_action = "HOLD / DELAY FIXTURE"
            timing_urgency = "PATIENT (Softening Curve)"
            timing_advice = (
                f"Forecasting model detects softening freight pressure. A cost trough of ${min_rate:.2f}/MT "
                f"is projected around Day +{optimal_day_offset} ({(as_of + timedelta(days=optimal_day_offset)).strftime('%d %b %Y')}). "
                f"Delaying tender fixture could yield up to ${total_freight_savings:,.0f} in ocean freight savings."
            )
            optimal_laycan_str = f"{laycan_start.strftime('%d %b')} – {laycan_end.strftime('%d %b %Y')}"
            projected_charter_rate = min_rate
            potential_savings = max(0.0, total_freight_savings)
        else:
            market_action = "EXECUTE SCHEDULED TENDER"
            timing_urgency = "NORMAL (Range-Bound Market)"
            timing_advice = (
                "Freight rates are trading within a narrow range (±2.5%). "
                "Execute standard charter tender aligned with steel plant inventory buffer and rail rake availability."
            )
            optimal_laycan_str = f"{laycan_start.strftime('%d %b')} – {laycan_end.strftime('%d %b %Y')}"
            projected_charter_rate = min_rate
            potential_savings = max(0.0, total_freight_savings)

        # Determine Contract Type (Spot vs Time Charter vs COA)
        # Factor in annual cargo volume and market volatility
        volatility_high = abs(p15_change) > 8.0
        contract_options = []
        
        # Option 1: Spot Voyage Charter
        contract_options.append({
            "contract_type": "Spot Voyage Charter",
            "suitability": "Highly Recommended" if not volatility_high else "Conditional",
            "rate_usd_ton": round(projected_charter_rate, 2),
            "total_estimated_cost": round(projected_charter_rate * cargo_tonnage, 2),
            "pros": "Zero long-term commitment; full flexibility to capture market dips.",
            "cons": "Exposed to sudden short-term demurrage or bunker price spikes."
        })
        
        # Option 2: Short-Term Time Charter (e.g. 3-6 months period)
        daily_tc_rate = projected_charter_rate * 175000 / 30.0 * 0.92  # Approximate daily TC equivalent
        contract_options.append({
            "contract_type": "Short-Term Time Charter (3-6 Months)",
            "suitability": "Recommended for High Volume (>300k MT/quarter)",
            "rate_usd_ton": round(projected_charter_rate * 0.94, 2),
            "total_estimated_cost": round(projected_charter_rate * 0.94 * cargo_tonnage, 2),
            "pros": "Locks in ship availability; insulates against sudden Capesize shortages.",
            "cons": "Demurrage and bunker fuel price risks remain fully on charterer."
        })
        
        # Option 3: Contract of Affreightment (COA - 12 Months Long-term)
        contract_options.append({
            "contract_type": "Contract of Affreightment (COA)",
            "suitability": "Strategic Baseline for Core PSU Quotas",
            "rate_usd_ton": round(current_spot * 0.96, 2),
            "total_estimated_cost": round(current_spot * 0.96 * cargo_tonnage, 2),
            "pros": "Guarantees liftings across multiple months with pre-negotiated freight collars.",
            "cons": "Cannot capitalize if global freight crashes."
        })

        return {
            "market_action": market_action,
            "timing_urgency": timing_urgency,
            "timing_advice": timing_advice,
            "optimal_laycan_window": optimal_laycan_str,
            "optimal_laycan_days_offset": optimal_day_offset,
            "current_spot_rate": round(current_spot, 2),
            "projected_fixture_rate": round(projected_charter_rate, 2),
            "expected_rate_change_pct": round(pct_savings, 2),
            "potential_freight_savings_usd": round(potential_savings, 2),
            "contract_structures": contract_options
        }
