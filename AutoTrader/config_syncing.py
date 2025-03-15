import time
import json
import os
from config import get_config


def config_sync_thread(stop_event):
    # First call get_config() to initialize config.
    config = get_config()

    risk_folder = "risk_files"
    trade_file = os.path.join(risk_folder, f"{config.ISIN}_TRADE_DIRECTION.json")
    delta_file = os.path.join(risk_folder, f"{config.ISIN}_delta.json")

    while not stop_event.is_set():
        # Read trade direction from the file and update config.TRADE_DIRECTION.
        try:
            if os.path.exists(trade_file):
                with open(trade_file, "r") as f:
                    data = json.load(f)
                    config.TRADE_DIRECTION = data.get("trade_direction", 0)
                    print(f"Config updated: TRADE_DIRECTION = {config.TRADE_DIRECTION}")
            else:
                print(f"Trade file {trade_file} not found.")
        except Exception as e:
            print(f"Error reading {trade_file}: {e}")

        # Write the current delta from config.CURRENT_DELTA to the file.
        try:
            with open(delta_file, "w") as f:
                json.dump(config.CURRENT_DELTA, f)
            print(f"Wrote config.CURRENT_DELTA ({config.CURRENT_DELTA}) to {delta_file}")
        except Exception as e:
            print(f"Error writing {delta_file}: {e}")

        time.sleep(1)
