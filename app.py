import os
import logging
import threading
from flask import Flask, request, jsonify
from utils import verify_signature
from check import handle_check
from ping import handle_ping

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_interaction():
    # Verify the request
    try:
        verify_signature(request)
    except ValueError as e:
        logging.error(f"Verification failed: {e}")
        return jsonify({"error": "Invalid request signature"}), 401

    # Parse the JSON payload
    data = request.json
    logging.info(f"Received interaction: {data}")

    # Handle PING (Discord's interaction endpoint validation)
    if data.get("type") == 1:
        return handle_ping()

    # Handle slash commands
    if data.get("type") == 2:
        command_name = data["data"]["name"]
        interaction_token = data["token"]
        user_id = data["member"]["user"]["id"]

        # Handle /ping command
        if command_name == "ping":
            threading.Thread(target=handle_ping, args=(interaction_token,)).start()
            return jsonify({"type": 5})  # Acknowledge the command

        # Handle /check command
        elif command_name == "check":
            threading.Thread(target=handle_check, args=(interaction_token, user_id)).start()
            return jsonify({"type": 5})  # Acknowledge the command

    # Default response for unknown commands
    return jsonify({"error": "Unknown command"}), 400

@app.route("/healthz", methods=["GET", "HEAD"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
