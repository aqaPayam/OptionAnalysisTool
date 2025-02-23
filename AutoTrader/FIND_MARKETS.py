import os
import datetime
import pandas as pd
import requests
import jdatetime
from trading_api import TradingAPI
from config import get_config

# Constants
UNDERLYING_NAME = "خودرو"
UNDERLYING_TICKER = "IRO1IKCO0001"
option_id = "IRO9IKCO8N71"  # Example option ID
MIN_REMAINING_DAYS = 14  # Minimum required days before expiration
MIN_VOLUME_LIMIT = 40000  # Minimum volume required


def fetch_ins_code(option_ticker):
    """
    Fetches the insCode for a given option ticker from the TSETMC API.
    """
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
    """
    Fetches the closing volume (qTotTran5J) for the given insCode from TSETMC.
    Uses the first entry from the closingPriceDaily list.
    """
    url = f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        closing_list = data.get("closingPriceDaily", [])
        if closing_list:
            first_entry = closing_list[0]  #TODO : MEHDI TODO
            return first_entry.get("qTotTran5J")
        return None
    except Exception as e:
        print(f"Error fetching closing volume for insCode {ins_code}: {e}")
        return None


def process_option_data(response_data):
    """
    Processes the API response to extract structured option data,
    fetches the insCode and closing volume for each option,
    and returns a DataFrame.
    """
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
            # Determine CALL_PUT: 'p' for اختیارف (call), 'c' for اختیارخ (put)
            call_put = "p" if "اختیارف" in title_parts[0] else "c" if "اختیارخ" in title_parts[0] else None

            # Fetch insCode and closing volume for this option
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
    """
    Converts a Jalali expiration date (YYYY/MM/DD) to a Gregorian date,
    and returns the number of days remaining from today.
    """
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
    """
    Converts a Jalali date (YYYY/MM/DD) into Gregorian format (YYYY-MM-DD).
    """
    try:
        j_date = jdatetime.datetime.strptime(jalali_date_str, "%Y/%m/%d")
        g_date = j_date.togregorian()
        return g_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error converting {jalali_date_str}: {e}")
        return jalali_date_str


if __name__ == "__main__":
    trading_api = TradingAPI()

    # -----------------------------
    # DataFrame 1 & 2: Option Details from MDAPI
    # -----------------------------
    option_details = trading_api.get_option_details_from_mdpapi(option_id)
    if option_details:
        df_all = process_option_data(option_details)
        # Compute remaining days for each option
        df_all["REMAINING_DAYS"] = df_all["EXPIRATION_DATE"].apply(get_remaining_days)
    else:
        df_all = pd.DataFrame()

    # Filter based on VOLUME and REMAINING_DAYS criteria
    df_filtered = df_all[
        (df_all["VOLUME"] > MIN_VOLUME_LIMIT) &
        (df_all["REMAINING_DAYS"] > MIN_REMAINING_DAYS)
        ] if not df_all.empty else pd.DataFrame()

    # -----------------------------
    # DataFrame 3: Portfolio Options (from TradingAPI)
    # -----------------------------
    df_portfolio = trading_api.get_portfolio_options_df()  # Function from your TradingAPI class

    # -----------------------------
    # DataFrame 4: Today Running (Final Data)
    # -----------------------------
    # For rows from filtered data, set CAN_TRADE_IN_SAME_DIRECTION = True
    if not df_filtered.empty:
        df_today_running_filtered = df_filtered[
            ["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT"]].copy()
        df_today_running_filtered["CAN_TRADE_IN_SAME_DIRECTION"] = True
    else:
        df_today_running_filtered = pd.DataFrame(
            columns=["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT",
                     "CAN_TRADE_IN_SAME_DIRECTION"])

    # For portfolio data, select rows not already in filtered data and set CAN_TRADE_IN_SAME_DIRECTION = False
    if df_portfolio is not None and not df_portfolio.empty:
        filtered_tickers = set(df_filtered["OPTION_TICKER"]) if not df_filtered.empty else set()
        df_today_running_portfolio = df_portfolio[~df_portfolio["OPTION_TICKER"].isin(filtered_tickers)].copy()
        df_today_running_portfolio = df_today_running_portfolio[
            ["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT"]]
        df_today_running_portfolio["CAN_TRADE_IN_SAME_DIRECTION"] = False
    else:
        df_today_running_portfolio = pd.DataFrame(
            columns=["OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE", "CALL_PUT",
                     "CAN_TRADE_IN_SAME_DIRECTION"])

    # Combine filtered and portfolio rows to create the final "today running" DataFrame
    df_today_running = pd.concat([df_today_running_filtered, df_today_running_portfolio], ignore_index=True)
    # Add underlying info as constant columns
    df_today_running["UNDERLYING_NAME"] = UNDERLYING_NAME
    df_today_running["UNDERLYING_TICKER"] = UNDERLYING_TICKER
    # Reorder columns
    df_today_running = df_today_running[
        ["UNDERLYING_NAME", "UNDERLYING_TICKER", "OPTION_NAME", "OPTION_TICKER", "EXPIRATION_DATE", "STRIKE_PRICE",
         "CALL_PUT", "CAN_TRADE_IN_SAME_DIRECTION"]]

    # -----------------------------
    # Save Excel Files to Folder "market database folder"
    # -----------------------------
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
        print("No option data available for df_all.")

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

    # -----------------------------
    # Create Command Lines and Generate run_all.bat in Root Directory
    # -----------------------------
    # Build the command lines using the today running DataFrame.
    command_lines = []
    # Start the batch file with "@echo off"
    command_lines.append("@echo off")
    command_lines.append("chcp 65001")
    for idx, row in df_today_running.iterrows():
        underlying_name = row["UNDERLYING_NAME"]
        underlying_ticker = row["UNDERLYING_TICKER"]
        option_name = row["OPTION_NAME"]
        option_ticker = row["OPTION_TICKER"]
        # Convert Jalali expiration date to Gregorian (YYYY-MM-DD)
        expiration_date_jalali = row["EXPIRATION_DATE"]
        expiration_date = convert_jalali_to_gregorian(expiration_date_jalali)
        strike_price = row["STRIKE_PRICE"]
        call_put_arg = row["CALL_PUT"]  # Use "c" or "p" as-is
        # Include flag if CAN_TRADE_IN_SAME_DIRECTION is True
        flag = " --can_trade_in_same_direction" if row["CAN_TRADE_IN_SAME_DIRECTION"] else ""

        # In Windows CMD, use doubled double quotes for argument values inside the main quoted string.
        cmd = (f'start cmd /k "python main.py --mode run '
               f'--underlying_name ""{underlying_name}"" '
               f'--underlying_ticker ""{underlying_ticker}"" '
               f'--option_name ""{option_name}"" '
               f'--option_ticker ""{option_ticker}"" '
               f'--expiration_date ""{expiration_date}"" '
               f'--strike_price {strike_price} '
               f'--call_put {call_put_arg}{flag}"')
        command_lines.append(cmd)

    bat_file = "run_all.bat"  # Save batch file in root directory
    with open(bat_file, "w", encoding="utf-8") as f:
        for line in command_lines:
            f.write(line + "\n")
    print(f"Batch file saved to {bat_file}")

    # -----------------------------
    # Print DataFrames (Optional)
    # -----------------------------
    print("All Option Data:")
    print(df_all)
    print("\nFiltered Option Data:")
    print(df_filtered)
    print("\nPortfolio Options Data:")
    print(df_portfolio)
    print("\nToday Running Data:")
    print(df_today_running)
