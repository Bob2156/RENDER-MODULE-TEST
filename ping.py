from utils import send_followup_response

def handle_ping(interaction_token=None):
    if interaction_token:
        send_followup_response(interaction_token, {"content": "The bot is awake and ready!"})
    else:
        return {"type": 1}  # Acknowledge PING interaction
