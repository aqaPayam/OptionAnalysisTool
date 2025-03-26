import time
import json
import os


def risk_managing_thread(api, stop_event):
    risk_folder = "risk_files"
    master_file = os.path.join(risk_folder, "all_markets_isin.json")
    try:
        with open(master_file, "r") as f:
            master_isins = json.load(f)
    except Exception:
        return
    master_groups = {}
    for isin in master_isins:
        group_key = isin[4:8]
        master_groups.setdefault(group_key, []).append(isin)
    while not stop_event.is_set():
        master_records = {}
        for isin in master_isins:
            master_records[isin] = {
                "ISIN": isin,
                "NET": 0,
                "DELTA": None
            }
        try:
            portfolio_df = api.portfo_analyse()
        except Exception:
            portfolio_df = None
        if portfolio_df is not None:
            for idx, row in portfolio_df.iterrows():
                isin = row.get("ISIN", "")
                if isin not in master_records:
                    continue
                master_records[isin]["NET"] = row.get("NET", 0)

        for isin in master_isins:
            delta_filename = os.path.join(risk_folder, f"{isin}_delta.json")
            try:
                with open(delta_filename, "r") as f:
                    delta_value = json.load(f)
                master_records[isin]["DELTA"] = delta_value
            except Exception:
                master_records[isin]["DELTA"] = None

        group_avg_delta = {}
        for group_key, isin_list in master_groups.items():
            group_records = [master_records[isin] for isin in isin_list]
            valid_records = [rec for rec in group_records if rec["DELTA"] is not None]
            if not valid_records:
                avg_delta = 0.0
            else:
                numerator = 0.0
                denominator = api.calculate_total_balance()
                for rec in valid_records:
                    numerator += rec["DELTA"] * rec["NET"]
                avg_delta = 0.0 if denominator == 0 else numerator / denominator

            group_avg_delta[group_key] = avg_delta

        for group_key, isin_list in master_groups.items():
            avg_delta = group_avg_delta.get(group_key, 0.0)
            for isin in isin_list:
                trade_filename = os.path.join(risk_folder, f"{isin}_TRADE_DIRECTION.json")
                try:
                    with open(trade_filename, "w") as f:
                        json.dump(avg_delta, f)
                except Exception:
                    pass
        time.sleep(1)
