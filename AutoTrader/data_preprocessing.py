import numpy as np
import pandas as pd
import datetime
import jdatetime
from tqdm import tqdm
from py_vollib.black_scholes.implied_volatility import implied_volatility
import finpy_tse as tse
import os


def process_and_flatten_market_data(
        underlying_stock: str,
        option_stock: str,
        start_date: str,
        end_date: str,
        strike_price: float,
        risk_free_rate: float,
        expiration_jalali_date: str,
        call_put: str,
        save_folder: str = "data_files",
        just_download: bool = False
) -> pd.DataFrame:
    """
    Process, save, and flatten underlying and options market data, and calculate implied volatility.

    Parameters:
    - underlying_stock (str): Name of the underlying stock.
    - option_stock (str): Name of the option stock.
    - start_date (str): Start date in Jalali format ('YYYY-MM-DD').
    - end_date (str): End date in Jalali format ('YYYY-MM-DD').
    - strike_price (float): Strike price of the option.
    - risk_free_rate (float): Risk-free interest rate.
    - expiration_jalali_date (str): Expiration date in Jalali format ('YYYY-MM-DD').
    - call_put (str): Option type ('call' or 'put').
    - save_folder (str, optional): Directory to save data files. Defaults to "data_files".
    - just_download (bool, optional): If True, only download and save data without flattening. Defaults to False.

    Returns:
    - pd.DataFrame: A pandas DataFrame with columns ['Date', 'Time', 'avg_price_underlying', 'avg_price_option', 'implied_vol'].
                    If `just_download` is True, returns an empty DataFrame.
    """

    # Ensure the save directory exists
    os.makedirs(save_folder, exist_ok=True)

    # ----------------- Helper Functions -----------------

    def calculate_time_to_expiration(current_date: str, expiration_jalali_date: str) -> float:
        """
        Calculate the time to expiration (T) in years based on the current date and the expiration date.
        """
        # Convert the Jalali expiration date to Gregorian
        expiration_jalali = jdatetime.datetime.strptime(expiration_jalali_date, '%Y-%m-%d')
        expiration_gregorian = expiration_jalali.togregorian()

        # Convert the current date from Jalali to Gregorian
        current_jalali_date = jdatetime.datetime.strptime(current_date, '%Y-%m-%d')
        current_gregorian_date = current_jalali_date.togregorian()

        # Calculate the difference in days and convert to years
        days_to_expiration = (expiration_gregorian - current_gregorian_date).days
        T = days_to_expiration / 365  # Convert days to years
        return T

    def editing_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Edit and clean the raw data DataFrame.
        """
        df_edt = df.reset_index()
        df_edt = df_edt[df_edt["Depth"] == 1]
        df_edt = df_edt.reset_index(drop=True)
        df_edt = df_edt[["J-Date", "Time", "Sell_Vol", "Sell_Price", "Buy_Price", "Buy_Vol"]]
        df_edt["J-Date"] = df_edt["J-Date"].astype(str)
        df_edt["Time"] = df_edt["Time"].astype(str)

        initial_row_count = df_edt.shape[0]
        df_edt = df_edt.drop_duplicates(subset=["J-Date", "Time"])
        final_row_count = df_edt.shape[0]

        if initial_row_count != final_row_count:
            print(f"Dropped {initial_row_count - final_row_count} duplicate rows.")
        else:
            print("No duplicates were found.")

        return df_edt

    def generate_daily_data(date: str, data: pd.DataFrame, time_list: list) -> pd.Series:
        """
        Generate daily data aligned with the specified time list.
        """
        day_detail = pd.Series([np.array([np.nan] * 4)] * len(time_list), index=time_list)
        row = [np.nan] * 4
        today_data = data[data["J-Date"] == date]
        today_data.index = list(today_data["Time"])
        changed_times = list(today_data.index)
        temp_row = row
        changed_times_iter = iter(changed_times)
        next_match = next(changed_times_iter, None)
        first_time_list_time = time_list[0] if isinstance(time_list[0], datetime.time) else datetime.datetime.strptime(
            time_list[0], "%H:%M:%S").time()
        while next_match:
            next_match_time = datetime.datetime.strptime(next_match, "%H:%M:%S").time() if isinstance(next_match,
                                                                                                      str) else next_match
            if next_match_time >= first_time_list_time:
                break
            next_match = next(changed_times_iter, None)

        for i in time_list:
            if next_match and str(i) == next_match:
                if str(i) in today_data.index:
                    temp_row = np.array(today_data.loc[str(i)])[-4:]
                next_match = next(changed_times_iter, None)
            day_detail.loc[i] = temp_row
        return day_detail

    def preparing_structure(data: pd.DataFrame, dates: list, time_list: list) -> pd.DataFrame:
        """
        Prepare the structured DataFrame from processed data.
        """
        data["J-Date"] = data["J-Date"].astype(str)
        data["Time"] = data["Time"].astype(str)
        column = []
        for i in dates:
            column.append(generate_daily_data(i, data, time_list))
        df = pd.concat(column, axis=1)
        df.columns = dates
        return df

    def process_single_stock(stock_name: str, market_type: str, time_list: list) -> pd.DataFrame:
        """
        Process a single stock's data: download, edit, structure, and save.
        """
        file_name = os.path.join(save_folder, f"{market_type}_{stock_name}_{start_date}_{end_date}.pkl")

        # Check if file already exists
        if os.path.exists(file_name):
            print(f"File {file_name} already exists. Loading data from file.")
            datapirim = pd.read_pickle(file_name)
            return datapirim

        # If file doesn't exist, proceed with downloading and processing
        while True:
            print(f"Start downloading data for {market_type}: {stock_name}")
            data = tse.Get_IntradayOB_History(
                stock=stock_name,
                start_date=start_date,
                end_date=end_date,
                jalali_date=True,
                combined_datatime=False,
                show_progress=True
            )
            print("Downloading data finished.")

            # Process the data
            data = editing_data(data)
            datapirim = preparing_structure(data, list(data["J-Date"].unique()), time_list)

            # Check if all data is null
            all_null_data = True
            for date in tqdm(datapirim.columns, desc=f"Processing {market_type} Data", total=datapirim.shape[1]):
                for time, underlying_data in datapirim[date].items():
                    if not (np.isnan(underlying_data[1]) and np.isnan(underlying_data[2])):
                        all_null_data = False
                        break
                if not all_null_data:
                    break

            # Retry if data is all null
            if all_null_data:
                print(f"Everything null for {market_type} ({stock_name}). Retrying data retrieval...")
            else:
                break

        # Save processed data to file
        # datapirim.to_pickle(file_name)

        # csv_file_name = os.path.join(save_folder, f"{market_type}_{stock_name}_{start_date}_{end_date}.csv")
        # datapirim.to_csv(csv_file_name)
        # print(f"Data saved as {file_name} and CSV saved as {csv_file_name}!")

        return datapirim

    # ----------------- Main Processing -----------------

    # Generate the list of times between 09:15:00 and 12:30:00 with 1-second intervals
    start_time = datetime.time(9, 15, 0)
    end_time = datetime.time(12, 30, 0)
    delta = datetime.timedelta(seconds=1)
    time_list = []
    current = start_time
    while current <= end_time:
        time_list.append(current)
        current = (datetime.datetime.combine(datetime.date.min, current) + delta).time()

    # Step 1: Process and save underlying and option data
    underlying_data = process_single_stock(underlying_stock, "Underlying Market", time_list)
    option_data = process_single_stock(option_stock, "Options Market", time_list)

    # If just_download is True, return an empty DataFrame
    if just_download:
        print("Data downloaded and saved. `just_download` is set to True, so returning an empty DataFrame.")
        return pd.DataFrame(columns=["Date", "Time", "avg_price_underlying", "avg_price_option", "implied_vol"])

    # Step 2: Flatten market data with calculated implied volatility
    flattened_data = {
        "Date": [],
        "Time": [],
        "avg_price_underlying": [],
        "avg_price_option": [],
        "implied_vol": []
    }

    # Define counters for monitoring
    null_counter = 0
    skip_by_time_counter = 0
    try_except_counter = 0
    key_error_counter = 0

    # Define the valid time range between 09:15 and 12:30
    valid_time_start = datetime.time(9, 15, 0)
    valid_time_end = datetime.time(12, 30, 0)

    for date in tqdm(underlying_data.columns, desc="Processing Market Data", total=underlying_data.shape[1]):
        try:
            for time, underlying_entry in underlying_data[date].items():
                # Ensure the index is a datetime.time object
                if isinstance(time, str):
                    try:
                        current_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
                    except ValueError:
                        print(f"Invalid time format: {time}. Skipping.")
                        skip_by_time_counter += 1
                        continue
                elif isinstance(time, datetime.time):
                    current_time = time
                else:
                    print(f"Unexpected time format: {time}. Skipping.")
                    skip_by_time_counter += 1
                    continue

                # Skip rows where the time is outside the valid range
                if not (valid_time_start <= current_time <= valid_time_end):
                    skip_by_time_counter += 1
                    continue

                # Retrieve the corresponding option data
                try:
                    option_entry = option_data.loc[time, date]
                except KeyError:
                    key_error_counter += 1
                    print(f"Option data for {date} at {time} not found. Skipping.")
                    continue

                # Ensure valid rows in both the underlying and options market data
                if isinstance(underlying_entry, (list, np.ndarray)) and isinstance(option_entry, (list, np.ndarray)):
                    # Check for None or zero in the required elements
                    if (underlying_entry[1] is None or underlying_entry[2] is None or
                            option_entry[1] is None or option_entry[2] is None or
                            underlying_entry[1] == 0 or underlying_entry[2] == 0 or
                            option_entry[1] == 0 or option_entry[2] == 0):

                        avg_price_underlying = np.nan
                        avg_price_option = np.nan
                    else:
                        avg_price_underlying = (underlying_entry[1] + underlying_entry[
                            2]) / 2  # (Sell_Price + Buy_Price) / 2
                        avg_price_option = (option_entry[1] + option_entry[2]) / 2  # (Sell_Price + Buy_Price) / 2

                    # Check for null values in average prices
                    if pd.isnull(avg_price_underlying) or pd.isnull(avg_price_option):
                        null_counter += 1
                        continue

                    # Calculate time to expiration
                    T = calculate_time_to_expiration(date, expiration_jalali_date)

                    # Calculate implied volatility
                    try:
                        implied_vol = implied_volatility(
                            avg_price_option,
                            avg_price_underlying,
                            strike_price,
                            T,
                            risk_free_rate,
                            call_put
                        )
                    except Exception as e:
                        implied_vol = np.nan
                        try_except_counter += 1
                        print(f"Implied volatility calculation error on {date} at {time}: {e}")

                    # Append the data
                    flattened_data["Date"].append(date)
                    flattened_data["Time"].append(current_time.strftime("%H:%M:%S"))
                    flattened_data["avg_price_underlying"].append(avg_price_underlying)
                    flattened_data["avg_price_option"].append(avg_price_option)
                    flattened_data["implied_vol"].append(implied_vol)
        except KeyError as e:
            key_error_counter += 1
            print(f"Day {date} skipped due to KeyError: {e}")
            continue

    # Print the counters
    print(f"Rows with null values: {null_counter}")
    print(f"Rows skipped by time: {skip_by_time_counter}")
    print(f"Errors caught in try-except of implied volatility calculator: {try_except_counter}")
    print(f"KeyErrors caught when accessing option data: {key_error_counter}")

    if len(flattened_data["Date"]) == 0:
        raise ValueError(
            f"The processed data contains only null values. Please check the input data. TSMSE = GOH"
        )

    # Create a DataFrame with the desired columns
    flattened_df = pd.DataFrame(flattened_data)

    return flattened_df
