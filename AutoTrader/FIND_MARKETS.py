import os
import datetime
import pandas as pd
import requests
import jdatetime
from trading_api import TradingAPI

MIN_REMAINING_DAYS = 14  # Minimum required days before expiration
MIN_VOLUME_LIMIT = 40000  # Minimum volume required


def fetch_ins_code(option_ticker):
    url = f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentOptionByInstrumentID/{option_ticker}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("instrumentOption", {}).get("insCode")
    except Exception as e:
        print(f"Error fetching insCode for {option_ticker}: {e}")
        return None


def fetch_closing_volume(ins_code):
    url = f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        closing_list = data.get("closingPriceDaily", [])
        if closing_list:
            first_entry = closing_list[0]
            return first_entry.get("qTotTran5J")
        return None
    except Exception as e:
        print(f"Error fetching closing volume for insCode {ins_code}: {e}")
        return None


def process_option_data(response_data):
    # Remove the first object from the response
    response_data = response_data[1:]
    processed_data = []
    for item in response_data:
        # Expecting title format: "<option type>-<strike price>-<expiration date>"
        title_parts = item["title"].split("-")
        if len(title_parts) == 3:
            option_ticker = item["isin"]
            option_name = item["symbol"]
            strike_price = int(title_parts[1])
            expiration_date = title_parts[2]
            # Determine CALL_PUT based on the first part of the title
            call_put = "p" if "اختیارف" in title_parts[0] else "c" if "اختیارخ" in title_parts[0] else None
            # Fetch insCode and volume
            ins_code = fetch_ins_code(option_ticker)
            volume = fetch_closing_volume(ins_code) if ins_code else None
            processed_data.append({
                "OPTION_TICKER": option_ticker,
                "OPTION_NAME": option_name,
                "STRIKE_PRICE": strike_price,
                "EXPIRATION_DATE": expiration_date,
                "CALL_PUT": call_put,
                "insCode": ins_code,
                "VOLUME": volume
            })
    return pd.DataFrame(processed_data)


def get_remaining_days(expiration_str):
    try:
        j_date = jdatetime.datetime.strptime(expiration_str, "%Y/%m/%d")
        g_date = j_date.togregorian()
        today = datetime.date.today()
        remaining = (g_date.date() - today).days
        return remaining
    except Exception as e:
        print(f"Error computing remaining days for {expiration_str}: {e}")
        return None


def convert_jalali_to_gregorian(jalali_date_str):
    try:
        j_date = jdatetime.datetime.strptime(jalali_date_str, "%Y/%m/%d")
        g_date = j_date.togregorian()
        return g_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error converting {jalali_date_str}: {e}")
        return jalali_date_str


# Helper function to determine underlying info from OPTION_NAME prefix
def get_underlying_info(option_name):
    underlying_mapping = {
        "خودرو": {"prefixes": ["ضخود", "طخود"], "ticker": "IRO1IKCO0001"},  # update ticker accordingly
        "اهرم": {"prefixes": ["ضهرم", "طهرم"], "ticker": "IRT1AHRM0001"},  # update ticker accordingly
        "خساپا": {"prefixes": ["ضسپا", "طسپا"], "ticker": "IRO1SIPA0001"},  # update ticker accordingly
        "شستا": {"prefixes": ["ضستا", "طستا"], "ticker": "IRO1TAMN0001"}  # update ticker accordingly
    }
    for underlying, info in underlying_mapping.items():
        for prefix in info["prefixes"]:
            if option_name.startswith(prefix):
                return underlying, info["ticker"]
    return None, None


if __name__ == "__main__":
    trading_api = TradingAPI()

    # Dictionary mapping underlying markets to their respective MDAPI option IDs.
    # Update these IDs with the correct ones.
    market_option_ids = {
        "خودرو": "IRO9IKCO8Q21",  # "title": "اختیارخ خودرو-5500-1404/03/07","symbol": "ضخود3099",
        "اهرم": "IRO9AHRM4111",  # "title": "اختیارخ اهرم-42000-1404/03/28","symbol": "ضهرم3021",
        "خساپا": "IRO9SIPA2401",  # "title": "اختیارخ خساپا-2200-1404/03/28","symbol": "ضسپا3038",
        "شستا": "IROFTAMN1921"  # "title": "اختیارف شستا-1700-1404/03/13","symbol": "طستا3032",
    }

    # Ask the user for each underlying market if they want to fetch its MDAPI data
    mdapi_dfs = []
    for market, option_id in market_option_ids.items():
        user_input = input(f"Do you want to fetch MDAPI data for {market}? (y/n): ")
        if user_input.strip().lower() in ['y', 'yes']:
            print(f"Fetching MDAPI data for {market} using option_id {option_id}...")
            option_details = trading_api.get_option_details_from_mdpapi(option_id)
            if option_details:
                df_mdapi = process_option_data(option_details)
                # Add underlying info for clarity (here we use the market name, and you can derive ticker from the prefix)
                df_mdapi["UNDERLYING_NAME"] = market
                # If available, use the first row's option name to derive the ticker; otherwise leave as None.
                underlying_ticker = df_mdapi["OPTION_NAME"].iloc[0] if not df_mdapi.empty else ""
                df_mdapi["UNDERLYING_TICKER"] = get_underlying_info(underlying_ticker)[1]
                df_mdapi["REMAINING_DAYS"] = df_mdapi["EXPIRATION_DATE"].apply(get_remaining_days)
                mdapi_dfs.append(df_mdapi)
            else:
                print(f"No MDAPI data available for {market}.")
        else:
            print(f"Skipping MDAPI data for {market}.")

    # Combine all MDAPI data if any was fetched; otherwise, create an empty DataFrame.
    if mdapi_dfs:
        df_all = pd.concat(mdapi_dfs, ignore_index=True)
    else:
        df_all = pd.DataFrame()

    # Filter MDAPI data based on volume and remaining days criteria
    df_filtered = df_all[
        (df_all["VOLUME"] > MIN_VOLUME_LIMIT) &
        (df_all["REMAINING_DAYS"] > MIN_REMAINING_DAYS)
        ] if not df_all.empty else pd.DataFrame()

    # Retrieve Portfolio Options Data (common for all underlying markets)
    df_portfolio = trading_api.get_portfolio_options_df()

    # Process "Today Running" Data:
    # For MDAPI data that meets criteria, set CAN_TRADE_IN_SAME_DIRECTION = True.
    if not df_filtered.empty:
        df_today_running_filtered = df_filtered[
            ["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT", "UNDERLYING_NAME",
             "UNDERLYING_TICKER"]
        ].copy()
        df_today_running_filtered["CAN_TRADE_IN_SAME_DIRECTION"] = True
    else:
        df_today_running_filtered = pd.DataFrame(
            columns=["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT", "UNDERLYING_NAME",
                     "UNDERLYING_TICKER", "CAN_TRADE_IN_SAME_DIRECTION"])

    # For portfolio data, select rows not already in the filtered MDAPI data and set CAN_TRADE_IN_SAME_DIRECTION = False.
    if df_portfolio is not None and not df_portfolio.empty:
        filtered_tickers = set(df_filtered["OPTION_TICKER"]) if not df_filtered.empty else set()
        df_today_running_portfolio = df_portfolio[~df_portfolio["OPTION_TICKER"].isin(filtered_tickers)].copy()
        df_today_running_portfolio = df_today_running_portfolio[
            ["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT"]
        ]
        # Derive underlying info for portfolio options based on the OPTION_NAME prefix
        underlying_info = df_today_running_portfolio["OPTION_NAME"].apply(get_underlying_info)
        df_today_running_portfolio["UNDERLYING_NAME"] = underlying_info.apply(lambda x: x[0])
        df_today_running_portfolio["UNDERLYING_TICKER"] = underlying_info.apply(lambda x: x[1])
        df_today_running_portfolio["CAN_TRADE_IN_SAME_DIRECTION"] = False
    else:
        df_today_running_portfolio = pd.DataFrame(
            columns=["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT", "UNDERLYING_NAME",
                     "UNDERLYING_TICKER", "CAN_TRADE_IN_SAME_DIRECTION"])

    # Combine the filtered MDAPI data and portfolio data
    df_today_running = pd.concat([df_today_running_filtered, df_today_running_portfolio], ignore_index=True)

    # Reorder columns
    df_today_running = df_today_running[
        ["UNDERLYING_NAME", "UNDERLYING_TICKER", "OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE",
         "CALL_PUT", "CAN_TRADE_IN_SAME_DIRECTION"]
    ]

    # Save Excel Files to Folder "market database folder"
    output_folder = "market database folder"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    today_str = datetime.date.today().strftime("%Y%m%d")
    df_all_file = os.path.join(output_folder, f"all_option_data_{today_str}.xlsx")
    df_filtered_file = os.path.join(output_folder, f"filtered_option_data_{today_str}.xlsx")
    df_portfolio_file = os.path.join(output_folder, f"portfolio_options_{today_str}.xlsx")
    df_today_running_file = os.path.join(output_folder, f"today_running_{today_str}.xlsx")

    if not df_all.empty:
        df_all.to_excel(df_all_file, index=False)
        print(f"All option data saved to {df_all_file}")
    else:
        print("No MDAPI option data available.")

    if not df_filtered.empty:
        df_filtered.to_excel(df_filtered_file, index=False)
        print(f"Filtered option data saved to {df_filtered_file}")
    else:
        print("No filtered option data available.")

    if df_portfolio is not None and not df_portfolio.empty:
        df_portfolio.to_excel(df_portfolio_file, index=False)
        print(f"Portfolio options data saved to {df_portfolio_file}")
    else:
        print("No portfolio options data available.")

    if not df_today_running.empty:
        df_today_running.to_excel(df_today_running_file, index=False)
        print(f"Today running data saved to {df_today_running_file}")
    else:
        print("No today running data available.")

    # Create Command Lines and Generate run_all.bat in the Root Directory
    command_lines = []
    command_lines.append("@echo off")
    command_lines.append("chcp 65001")
    for idx, row in df_today_running.iterrows():
        underlying_name = row["UNDERLYING_NAME"]
        underlying_ticker = row["UNDERLYING_TICKER"]
        option_name = row["OPTION_NAME"]
        option_ticker = row["OPTION_TICKER"]
        expiration_date_jalali = row["EXPIRATION_DATE"]
        expiration_date = expiration_date_jalali.replace("/", "-")
        strike_price = row["STRIKE_PRICE"]
        call_put_arg = row["CALL_PUT"]
        flag = " --can_trade_in_same_direction" if row["CAN_TRADE_IN_SAME_DIRECTION"] else ""
        cmd = (f'start cmd /k "python main.py --mode run '
               f'--underlying_name ""{underlying_name}"" '
               f'--underlying_ticker ""{underlying_ticker}"" '
               f'--option_name ""{option_name}"" '
               f'--option_ticker ""{option_ticker}"" '
               f'--expiration_date ""{expiration_date}"" '
               f'--strike_price {strike_price} '
               f'--call_put {call_put_arg}{flag}"')
        command_lines.append(cmd)

    bat_file = "run_all.bat"
    with open(bat_file, "w", encoding="utf-8") as f:
        for line in command_lines:
            f.write(line + "\n")
    print(f"Batch file saved to {bat_file}")

    # Optionally print DataFrames for debugging
    print("All MDAPI Option Data:")
    print(df_all)
    print("\nFiltered Option Data:")
    print(df_filtered)
    print("\nPortfolio Options Data:")
    print(df_portfolio)
    print("\nToday Running Data:")
    print(df_today_running)

    import json
    import shutil

    risk_folder = "risk_files"
    # Create the folder if it doesn't exist; otherwise, remove all files inside it.
    if not os.path.exists(risk_folder):
        os.makedirs(risk_folder)
    else:
        # Remove all files (and subdirectories, if any) in the folder
        for filename in os.listdir(risk_folder):
            file_path = os.path.join(risk_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # remove file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # remove directory recursively
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    # Combine unique option tickers from MDAPI and portfolio data
    all_tickers = set()
    if not df_today_running.empty:
        all_tickers.update(df_today_running["OPTION_TICKER"].tolist())

    all_tickers_list = list(all_tickers)

    json_path = os.path.join(risk_folder, "all_markets_isin.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_tickers_list, f, ensure_ascii=False, indent=4)

    print(f"All markets ISIN JSON file saved to {json_path}")
