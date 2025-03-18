import time
import json
import os
from config import get_config


def config_sync_thread(stop_event):
    config = get_config()
    risk_folder = "risk_files"
    trade_file = os.path.join(risk_folder, f"{config.OPTION_TICKER}_TRADE_DIRECTION.json")
    delta_file = os.path.join(risk_folder, f"{config.OPTION_TICKER}_delta.json")

    while not stop_event.is_set():
        try:
            if os.path.exists(trade_file):
                with open(trade_file, "r") as f:
                    data = json.load(f)
                    config.TRADE_DIRECTION = data
                    # print(f"Config updated: TRADE_DIRECTION = {config.TRADE_DIRECTION}")
            else:
                print(f"Trade file {trade_file} not found.")
        except Exception as e:
            print(f"Error reading {trade_file}: {e}")

        try:
            with open(delta_file, "w") as f:
                json.dump(config.CURRENT_DELTA, f)
            # print(f"Wrote config.CURRENT_DELTA ({config.CURRENT_DELTA}) to {delta_file}")
        except Exception as e:
            print(f"Error writing {delta_file}: {e}")

        time.sleep(1)
