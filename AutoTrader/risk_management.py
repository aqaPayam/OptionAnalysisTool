import time
import json
import os


def risk_managing_thread(api, config, stop_event):
    """
    Risk Managing Thread:

    Pre-Loop (run once):
      - Reads "risk_files/all_markets_isin.json", a JSON list of ISIN strings (e.g.,
        ["IRO9ZOBI4731", "IRO9ZOBI4732", ...]).
      - Groups these ISINs by their first 8 characters into master_groups.

    Main Loop (runs every second):
      1. Reinitialize master_records for every ISIN with default values:
             {"ISIN": isin, "BUY_VOLUME": 0, "SELL_VOLUME": 0, "AVERAGE_PRICE": 0, "DELTA": None}
      2. Retrieve portfolio data via api.portfo_analyse(). For each row whose ISIN is in master_records:
             - Update BUY_VOLUME, SELL_VOLUME, and AVERAGE_PRICE.
             - Read the corresponding "risk_files/<ISIN>_delta.json" file (which contains a number)
               to update DELTA.
      3. For each group (by ISIN prefix):
             - If any record in the group has DELTA == None, set the group’s averaged_delta to 0.
             - Otherwise, compute the weighted average delta as:

                   avg_delta = sum(delta * (|BUY_VOLUME| + |SELL_VOLUME|) * AVERAGE_PRICE) /
                               sum((|BUY_VOLUME| + |SELL_VOLUME|) * AVERAGE_PRICE)

               Then, if -config.risk_param <= avg_delta <= config.risk_param,
               set averaged_delta to 0 (neutral).
      4. For each master ISIN, update its "risk_files/<ISIN>_TRADE_DIRECTION.json" file with the computed averaged_delta.
      5. Wait 1 second and repeat until stop_event is set.
    """
    risk_folder = "risk_files"
    master_file = os.path.join(risk_folder, "all_markets_isin.json")
    try:
        with open(master_file, "r") as f:
            master_isins = json.load(f)
    except Exception as e:
        print(f"Error reading {master_file}: {e}")
        return

    # Group master ISINs by first 8 characters.
    master_groups = {}
    for isin in master_isins:
        group_key = isin[:8]
        master_groups.setdefault(group_key, []).append(isin)

    while not stop_event.is_set():
        # (1) Initialize master_records with default values.
        master_records = {}
        for isin in master_isins:
            master_records[isin] = {
                "ISIN": isin,
                "BUY_VOLUME": 0,
                "SELL_VOLUME": 0,
                "AVERAGE_PRICE": 0,
                "DELTA": None
            }

        # (2) Retrieve portfolio data and update master_records.
        portfolio_df = api.portfo_analyse()
        for idx, row in portfolio_df.iterrows():
            isin = row.get("ISIN", "")
            if isin not in master_records:
                continue
            buy_volume = row.get("BUY_VOLUME", 0)
            sell_volume = row.get("SELL_VOLUME", 0)
            average_price = row.get("AVERAGE_PRICE", 0)
            delta_filename = os.path.join(risk_folder, f"{isin}_delta.json")
            try:
                with open(delta_filename, "r") as f:
                    delta_value = json.load(f)
            except Exception as e:
                print(f"Error reading {delta_filename}: {e}")
                delta_value = None

            master_records[isin]["BUY_VOLUME"] = buy_volume
            master_records[isin]["SELL_VOLUME"] = sell_volume
            master_records[isin]["AVERAGE_PRICE"] = average_price
            master_records[isin]["DELTA"] = delta_value
            print(f"Updated {isin}: delta = {delta_value}")

        # (3) Compute averaged_delta for each group.
        group_avg_delta = {}
        for group_key, isin_list in master_groups.items():
            group_records = [master_records[isin] for isin in isin_list]
            # If any record in the group lacks a valid delta, set averaged_delta to 0.
            if any(rec["DELTA"] is None for rec in group_records):
                avg_delta = 0.0
                print(f"Group {group_key}: Missing delta; setting averaged_delta to 0.")
            else:
                numerator = 0.0
                denominator = 0.0
                for rec in group_records:
                    volume = abs(rec["BUY_VOLUME"]) + abs(rec["SELL_VOLUME"])
                    avg_price = rec["AVERAGE_PRICE"]
                    delta = rec["DELTA"]
                    numerator += delta * volume * avg_price
                    denominator += volume * avg_price
                if denominator == 0:
                    avg_delta = 0.0
                    print(f"Group {group_key}: Zero denominator; setting averaged_delta to 0.")
                else:
                    avg_delta = numerator / denominator
                    print(f"Group {group_key}: Computed averaged_delta = {avg_delta:.4f}")
                    # If the computed average is within the risk neutral range, set it to 0.
                    if -config.risk_param <= avg_delta <= config.risk_param:
                        avg_delta = 0.0
            group_avg_delta[group_key] = avg_delta

        # (4) Update each ISIN's TRADE_DIRECTION file with the averaged_delta.
        for group_key, isin_list in master_groups.items():
            avg_delta = group_avg_delta.get(group_key, 0.0)
            for isin in isin_list:
                trade_filename = os.path.join(risk_folder, f"{isin}_TRADE_DIRECTION.json")
                try:
                    if os.path.exists(trade_filename):
                        with open(trade_filename, "r") as f:
                            trade_data = json.load(f)
                    else:
                        trade_data = {}
                except Exception as e:
                    print(f"Error reading {trade_filename}: {e}")
                    trade_data = {}
                # Save the computed averaged_delta (a float) into the file.
                trade_data["averaged_delta"] = avg_delta
                try:
                    with open(trade_filename, "w") as f:
                        json.dump(trade_data, f)
                    print(f"Updated {trade_filename} with averaged_delta: {avg_delta}")
                except Exception as e:
                    print(f"Error writing {trade_filename}: {e}")

        time.sleep(1)
