import logging
from utils import send_followup_response, fetch_sma_and_volatility, fetch_treasury_rate

def handle_check(interaction_token, user_id):
    try:
        last_close, sma_220, volatility = fetch_sma_and_volatility()
        treasury_rate = fetch_treasury_rate()

        embed = {
            "embeds": [
                {
                    "title": "Market Financial Evaluation Assistant (MFEA)",
                    "description": f"<@{user_id}>, here is the latest market data:",
                    "fields": [
                        {"name": "SPX Last Close", "value": f"{last_close}", "inline": True},
                        {"name": "SMA 220", "value": f"{sma_220}", "inline": True},
                        {"name": "Volatility (Annualized)", "value": f"{volatility}%", "inline": True},
                        {"name": "3M Treasury Rate", "value": f"{treasury_rate}%", "inline": True}
                    ],
                    "color": 5814783
                }
            ]
        }

        # Determine strategy
        if last_close > sma_220:
            if volatility < 14:
                strategy = "Risk ON - 100% UPRO or 3x (100% SPY)"
            elif volatility < 24:
                strategy = "Risk MID - 100% SSO or 2x (100% SPY)"
            else:
                if treasury_rate and treasury_rate < 4:
                    strategy = "Risk ALT - 25% UPRO + 75% ZROZ or 1.5x (50% SPY + 50% ZROZ)"
                else:
                    strategy = "Risk OFF - 100% SPY or 1x (100% SPY)"
        else:
            if treasury_rate and treasury_rate < 4:
                strategy = "Risk ALT - 25% UPRO + 75% ZROZ or 1.5x (50% SPY + 50% ZROZ)"
            else:
                strategy = "Risk OFF - 100% SPY or 1x (100% SPY)"

        embed["embeds"][0]["fields"].append({"name": "Investment Strategy", "value": strategy, "inline": False})
        send_followup_response(interaction_token, embed)
    except Exception as e:
        logging.error(f"Error in /check: {e}")
        send_followup_response(interaction_token, {"content": f"<@{user_id}>, an error occurred: {e}"})
