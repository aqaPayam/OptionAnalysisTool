#!pip install persiantools
# !pip install finpy_tse
# !pip install py_vollib
# !pip install jdatetime

import numpy as np
import pandas as pd
import datetime
import jdatetime
import requests
from tqdm import tqdm
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.implied_volatility import implied_volatility
import persiantools
import finpy_tse as tse
import warnings

def process_and_save_underlying_and_option_data(underlying_stock, option_stock, start_date, end_date):
    def editing_data(df):
        df_edt = df.reset_index()
        df_edt = df_edt[df_edt["Depth"] == 1]
        df_edt = df_edt.reset_index()
        df_edt = df_edt[["J-Date", "Time", "Sell_Vol", "Sell_Price", "Buy_Price", "Buy_Vol"]]
        df_edt["J-Date"] = df_edt["J-Date"].astype(str)
        df_edt["Time"] = df_edt["Time"].astype(str)
        return df_edt

    def generate_daily_data(date, data, time_list):
        day_detail = pd.Series([np.array([np.nan] * 4)] * len(time_list), index=time_list)
        row = [np.nan] * 4
        today_data = data[data["J-Date"] == date]
        today_data.index = list(today_data["Time"])
        changed_times = list(today_data.index)
        temp_row = row
        changed_times_iter = iter(changed_times)
        next_match = next(changed_times_iter, None)
        first_time_list_time = time_list[0] if isinstance(time_list[0], datetime.time) else datetime.datetime.strptime(time_list[0], "%H:%M:%S").time()
        while next_match:
            next_match_time = datetime.datetime.strptime(next_match, "%H:%M:%S").time() if isinstance(next_match, str) else next_match
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

    def preparing_structure(data, dates, time_list):
        data["J-Date"] = data["J-Date"].astype(str)
        data["Time"] = data["Time"].astype(str)
        column = []
        for i in dates:
            column.append(generate_daily_data(i, data, time_list))
        df = pd.concat(column, axis=1)
        df.columns = dates
        return df

    start_time = datetime.time(9, 15, 0)
    end_time = datetime.time(12, 30, 0)
    delta = datetime.timedelta(seconds=1)
    time_list = []
    current = start_time
    while current <= end_time:
        time_list.append(current)
        current = (datetime.datetime.combine(datetime.date.min, current) + delta).time()

    def process_single_stock(stock_name, market_type):
        from tqdm import tqdm

        while True:
            print("Start downloading data:")
            data = tse.Get_IntradayOB_History(
                stock=stock_name,
                start_date=start_date,
                end_date=end_date,
                jalali_date=True,
                combined_datatime=False,
                show_progress=True
            )
            print("Downloading data finished.")
            data = editing_data(data)
            datapirim = preparing_structure(data, list(data["J-Date"].unique()), time_list)
            all_null_data = True
            for date in tqdm(datapirim.columns, desc=f"Processing {market_type} Data", total=datapirim.shape[1]):
                for time, underlying_data in datapirim[date].items():
                    if not (np.isnan(underlying_data[1]) and np.isnan(underlying_data[2])):
                        all_null_data = False
                        break
                if not all_null_data:
                    break
            if all_null_data:
                print(f"Everything null for {market_type} ({stock_name}). Retrying data retrieval...")
            else:
                break
        file_name = f"{market_type}_{stock_name}_{start_date}_{end_date}.pkl"
        datapirim.to_pickle(file_name)
        print(f"Data saved as {file_name}!")
        return datapirim

    underlying_data = process_single_stock(underlying_stock, "Underlying Market")
    option_data = process_single_stock(option_stock, "Options Market")
    return underlying_data, option_data




def calculate_time_to_expiration(current_date, expiration_jalali_date):
    """
    Calculate the time to expiration (T) in years based on the current date and the expiration date.

    Parameters:
    - current_date: The date of the current data point (Jalali format).
    - expiration_jalali_date: The final expiration date (Jalali format).

    Returns:
    - T: The time to expiration in years.
    """
    # Convert the Jalali expiration date to Gregorian
    expiration_jalali = jdatetime.datetime.strptime(expiration_jalali_date, '%Y-%m-%d')
    expiration_gregorian = expiration_jalali.togregorian()

    # Convert the current date from Jalali to Gregorian
    current_jalali_date = jdatetime.datetime.strptime(str(current_date), '%Y-%m-%d')
    current_gregorian_date = current_jalali_date.togregorian()

    # Calculate the difference in days and convert to years
    days_to_expiration = (expiration_gregorian - current_gregorian_date).days
    T = days_to_expiration / 365  # Convert days to years
    return T


def flatten_market_data_with_volatility(underlying_market_df, options_market_df, strike_price, risk_free_rate,
                                        expiration_jalali_date, call_put):
    """
    Flatten 2D DataFrames (underlying and options market data), calculate average prices, and compute implied volatility.

    Parameters:
    - underlying_market_df: DataFrame with underlying asset market data where each cell contains [Sell_Vol, Sell_Price, Buy_Price, Buy_Vol].
    - options_market_df: DataFrame with call option market data where each cell contains [Sell_Vol, Sell_Price, Buy_Price, Buy_Vol].
    - strike_price: Strike price of the option.
    - risk_free_rate: Risk-free interest rate.
    - expiration_jalali_date: Expiration date in Jalali calendar (as a string).

    Returns:
    - flattened_series: A 1D pandas Series with MultiIndex (date, time), containing [avg_price_underlying, avg_price_option, implied_volatility].
    """

    flattened_data = []
    index_tuples = []

    # Define counters
    null_counter = 0
    skip_by_time_counter = 0
    try_except_counter = 0

    # Define the valid time range between 9:00 and 12:30
    valid_time_start = pd.to_datetime("09:15:00").time()
    valid_time_end = pd.to_datetime("12:30:00").time()

    for date in tqdm(underlying_market_df.columns, desc="Processing Market Data", total=underlying_market_df.shape[1]):
        for time, underlying_data in underlying_market_df[date].items():
            time_str = time.strftime("%H:%M:%S")
            current_time = pd.to_datetime(time_str, format="%H:%M:%S").time()

            # Skip rows where the time is outside the range 9:00 - 12:30
            if not (valid_time_start <= current_time <= valid_time_end):
                skip_by_time_counter += 1
                continue  # Skip to the next iteration if time is not valid

            option_data = options_market_df.loc[time, date]

            # Ensure valid rows in both the underlying and options market data
            if isinstance(underlying_data, (list, np.ndarray)) and isinstance(option_data, (list, np.ndarray)):
                avg_price_underlying = (underlying_data[1] + underlying_data[2]) / 2  # (Sell_Price + Buy_Price) / 2
                avg_price_option = (option_data[1] + option_data[2]) / 2  # (Sell_Price + Buy_Price) / 2

                # Check for null values in avg_price_underlying and avg_price_option
                if pd.isnull(avg_price_underlying) or pd.isnull(avg_price_option):
                    null_counter += 1  # Increment null counter if either average price is null or NaN
                    continue  # Skip if either average price is null or NaN

                # Calculate time to expiration dynamically for each date
                T = calculate_time_to_expiration(date, expiration_jalali_date)

                try:
                    implied_vol = implied_volatility(avg_price_option, avg_price_underlying, strike_price, T,
                                                     risk_free_rate, call_put)
                except:
                    implied_vol = np.nan
                    try_except_counter += 1  # Increment try-except counter when an error occurs

                # Append the average prices and implied volatility to the flattened data
                flattened_data.append([avg_price_underlying, avg_price_option, implied_vol])
                index_tuples.append((date, time_str))

    # Print the counters
    print(f"Rows with null values: {null_counter}")
    print(f"Rows skipped by time: {skip_by_time_counter}")
    print(f"Errors caught in try-except: {try_except_counter}")
    if len(flattened_data) == 0:
        raise ValueError(
                f"The processed data contains only null values. Please check the input data.   TSMSE = GOH")

    flattened_series = pd.Series(flattened_data, index=pd.MultiIndex.from_tuples(index_tuples, names=["Date", "Time"]))

    return flattened_series


def calculate_estimated_volatility(call_series, total_points_in_window):
    """
    Calculate the estimated volatility for each row in call_series, based on the average of implied volatility
    for the previous 10 days (3.5 hours/day, 3600 seconds/hour = 126,000 seconds).

    Parameters:
    - call_series: A pandas Series containing [avg_price_underlying, avg_price_option, implied_vol] with MultiIndex (date, time).

    Returns:
    - extended_series: A pandas Series containing [avg_price_underlying, avg_price_option, implied_vol, estimated_vol]
      for each row, aligned with the input Series.
    """

    # Initialize an empty list to store extended data (with estimated volatility)
    extended_data = []

    # Maintain a rolling window for implied_vol
    rolling_implied_vols = []
    rolling_sum = 0  # To efficiently calculate the average

    # Total number of points to look back (126,000 seconds / time step interval)

    # Loop through each row in the call_series with tqdm for progress tracking
    for (index, row_data) in tqdm(call_series.items(), total=len(call_series), desc="Calculating Estimated Volatility"):
        # Extract avg_price_underlying, avg_price_option, and implied_vol from row_data
        avg_price_underlying = row_data[0]
        avg_price_option = row_data[1]
        implied_vol = row_data[2]

        # If we have a valid implied volatility (not NaN)
        if not pd.isnull(implied_vol):
            # Add the implied volatility to the rolling list
            rolling_implied_vols.append(implied_vol)
            rolling_sum += implied_vol

            # If rolling window exceeds the required window size, remove the oldest element
            if len(rolling_implied_vols) > total_points_in_window:
                rolling_sum -= rolling_implied_vols.pop(0)  # Remove the oldest implied_vol from the rolling window

            # Calculate the estimated volatility as the average of the rolling implied vols
            estimated_vol = rolling_sum / len(rolling_implied_vols)
        else:
            # If implied_vol is NaN, set estimated volatility as NaN
            estimated_vol = np.nan

        # Append the original data along with the calculated estimated volatility
        extended_data.append([avg_price_underlying, avg_price_option, implied_vol, estimated_vol])

    # Create a new pandas Series with the same index as the input series
    extended_series = pd.Series(extended_data, index=call_series.index)

    return extended_series


def calculate_black_scholes_price(call_series, strike_price, risk_free_rate, expiration_jalali_date, call_put):
    """
    Calculate Black-Scholes price based on estimated volatility for each row in the call_series.

    Parameters:
    - call_series: A pandas Series containing [avg_price_underlying, avg_price_option, implied_vol, estimated_vol] with MultiIndex (date, time).
    - strike_price: The strike price of the option.
    - risk_free_rate: The risk-free interest rate.
    - expiration_jalali_date: Expiration date in Jalali format.

    Returns:
    - extended_series: A pandas Series containing [avg_price_underlying, avg_price_option, black_scholes_price, implied_vol, estimated_vol]
      for each row, aligned with the input Series.
    """

    extended_data = []

    # Loop through each row in the call_series
    for (index, row_data) in tqdm(call_series.items(), total=len(call_series), desc="Calculating Black-Scholes Price"):
        avg_price_underlying = row_data[0]  # Underlying asset price
        avg_price_option = row_data[1]  # Option market price
        implied_vol = row_data[2]  # Implied volatility
        estimated_vol = row_data[3]  # Estimated volatility

        # Skip the row if any critical values are NaN
        if pd.isnull(avg_price_underlying) or pd.isnull(estimated_vol):
            black_scholes_price = np.nan
        else:
            # Calculate time to expiration dynamically for each row
            T = calculate_time_to_expiration(index[0], expiration_jalali_date)

            # Ensure T is positive and estimated_vol is valid
            if T > 0 and estimated_vol > 0:
                # Calculate Black-Scholes price using the estimated volatility
                black_scholes_price = black_scholes(call_put, avg_price_underlying, strike_price, T, risk_free_rate,
                                                    estimated_vol)
            else:
                black_scholes_price = np.nan

        # Append the original data along with the calculated Black-Scholes price
        extended_data.append([avg_price_underlying, avg_price_option, black_scholes_price, implied_vol, estimated_vol])

    # Create a new pandas Series with the same index as the input series
    extended_series = pd.Series(extended_data, index=call_series.index)

    return extended_series


def generate_option_signals(option_series, window_size, z_threshold):
    """
    Generate buy/sell/hold signals along with statistics such as price difference, rolling mean,
    standard deviation, and Z-score from the given option data series.

    Parameters:
    option_series (pd.Series): A Series where each entry contains a list of option data.
                               [avg_price_underlying, avg_price_option, black_scholes_price, implied_vol, estimated_vol]
    window_size (int): Number of previous data points to consider for calculating rolling mean and std dev.
    z_threshold (float): Number of standard deviations from the mean to trigger buy/sell signals.


    Returns:
    pd.DataFrame: DataFrame containing avg_price_underlying, avg_price_option, black_scholes_price, implied_vol,
                  estimated_vol, price difference, rolling mean, rolling std dev, buy/sell signal, and Z-score,
                  with a multi-index structure.
    """

    # Extract individual data components from each entry in option_series
    underlying_price = option_series.apply(lambda x: x[0])
    option_price = option_series.apply(lambda x: x[1])
    black_scholes_price = option_series.apply(lambda x: x[2])
    implied_volatility = option_series.apply(lambda x: x[3])
    estimated_volatility = option_series.apply(lambda x: x[4])

    # Calculate the price difference between Black-Scholes price and the actual option price
    price_difference = black_scholes_price - option_price

    # Compute rolling mean and standard deviation of the price difference
    rolling_mean_diff = price_difference.rolling(window=window_size).mean()
    rolling_std_diff = price_difference.rolling(window=window_size).std()

    # Store results in a list of dictionaries to convert to a DataFrame later
    results = []

    # Function to compute signal and statistics for each index
    def compute_signal_and_stats(index):
        current_diff = price_difference.loc[index]
        mean_diff = rolling_mean_diff.loc[index] if not pd.isna(rolling_mean_diff.loc[index]) else np.nan
        std_diff = rolling_std_diff.loc[index] if not pd.isna(rolling_std_diff.loc[index]) else np.nan

        if pd.isna(mean_diff) or pd.isna(std_diff) or std_diff == 0:
            z_score = np.nan
            signal = 'Hold'
        else:
            # Calculate Z-score (how many standard deviations current_diff is from the mean)
            z_score = (current_diff - mean_diff) / std_diff

            if z_score > z_threshold:
                signal = 'Sell'  # Option is overvalued for Call
            elif z_score < -z_threshold:
                signal = 'Buy'  # Option is undervalued for Call
            else:
                signal = 'Hold'

        # Store each row as a dictionary (to be converted to DataFrame later)
        results.append({
            'avg_price_underlying': underlying_price.loc[index],
            'avg_price_option': option_price.loc[index],
            'black_scholes_price': black_scholes_price.loc[index],
            'implied_vol': implied_volatility.loc[index],
            'estimated_vol': estimated_volatility.loc[index],
            'price_difference': current_diff,
            'rolling_mean_diff': mean_diff,
            'rolling_std_diff': std_diff,
            'signal': signal,
            'z_score': z_score  # Statistic showing how far the price difference is from the mean
        })

    # Use tqdm to monitor progress while applying the function to each item
    for index, row_data in tqdm(option_series.items(), total=len(option_series), desc="Calculating Option Signals"):
        compute_signal_and_stats(index)

    # Convert the list of results to a DataFrame
    result_df = pd.DataFrame(results, index=option_series.index)

    # Count and print the number of 'Buy' and 'Sell' signals
    sell_count = result_df['signal'].value_counts().get('Sell', 0)
    buy_count = result_df['signal'].value_counts().get('Buy', 0)

    print(f"Number of 'Sell' signals: {sell_count}")
    print(f"Number of 'Buy' signals: {buy_count}")

    return result_df


def run_option_analysis(underlying_stock_name="", option_stock_name="", call_put="c", start_date="", end_date="",
                        strike_price=13000,
                        risk_free_rate=0.30, expiration_jalali_date='1402-12-23',
                        window_size_volatility=int(10 * 3.5 * 3600), window_size_normal=int(10 * 3.5 * 3600),
                        z_threshold_normal=1.5):
    """
    This function encapsulates the process of analyzing option market data and generating trading signals
    based on Black-Scholes price and estimated volatility.

    Parameters:
        - underlying_stock (str): The ticker or symbol for the underlying stock
        - option_stock (str): The ticker or symbol for the option
        - start_date (str): The start date for fetching market data
        - end_date (str): The end date for fetching market data
        - strike_price (float): The option strike price
        - risk_free_rate (float): The risk-free interest rate
        - expiration_jalali_date (str): The expiration date in Jalali calendar format ('YYYY-MM-DD')
        - window_size_volatility (int): The window size for calculating volatility
        - window_size_normal (int): The window size for calculating option signals
        - z_threshold_normal (float): The Z-threshold for generating signals

    Returns:
        - result (DataFrame): A DataFrame containing the final option signals
    """
    
    # Step 1: Process and save underlying and option data
    underlying_stock, option_stock = process_and_save_underlying_and_option_data(
        underlying_stock=underlying_stock_name, option_stock=option_stock_name, start_date=start_date, end_date=end_date
    )

    #underlying_stock = pd.read_pickle("ahrom1.pickle")
    #option_stock = pd.read_pickle("zahrom1.pickle")

    # Step 2: Flatten market data with calculated implied volatility
    call_series = flatten_market_data_with_volatility(
        underlying_market_df=underlying_stock, options_market_df=option_stock,
        strike_price=strike_price, risk_free_rate=risk_free_rate, expiration_jalali_date=expiration_jalali_date,
        call_put=call_put
    )



    # Step 3: Calculate estimated volatility over the specified window size
    series_with_volatility = calculate_estimated_volatility(call_series, total_points_in_window=window_size_volatility)

    # Step 4: Calculate Black-Scholes prices for the option
    final_series = calculate_black_scholes_price(
        call_series=series_with_volatility, strike_price=strike_price,
        risk_free_rate=risk_free_rate, expiration_jalali_date=expiration_jalali_date, call_put=call_put
    )

    # Step 5: Generate option signals based on calculated Black-Scholes prices
    result = generate_option_signals(option_series=final_series, window_size=window_size_normal,
                                     z_threshold=z_threshold_normal)


    filename = f"option_signals_{option_stock_name}_{start_date}_to_{end_date}.pkl"
    result.to_pickle(filename)
    print(f"Results saved to {filename}")

    print(f"finished analys {option_stock_name}")

    return result

import warnings

def run_selected_analysis(option_number):
    if option_number == 1:
        run_option_analysis(
            underlying_stock_name="خودرو",
            option_stock_name="ضخود8034",
            call_put="c",
            start_date="1403-05-15",
            end_date="1403-07-25",
            strike_price=2400,
            risk_free_rate=0.3,
            expiration_jalali_date='1403-08-02',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 2:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم7025",
            call_put="c",
            start_date="1403-05-13",
            end_date="1403-07-23",
            strike_price=16000,
            risk_free_rate=0.3,
            expiration_jalali_date='1403-07-25',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 3:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم3006",
            call_put="c",
            start_date="1402-11-10",
            end_date="1403-03-21",
            strike_price=20000,
            risk_free_rate=0.3,
            expiration_jalali_date='1403-03-23',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 4:
        run_option_analysis(
            underlying_stock_name="خودرو",
            option_stock_name="ضخود3084",
            call_put="c",
            start_date="1403-01-28",
            end_date="1403-02-30",
            strike_price=3000,
            risk_free_rate=0.3,
            expiration_jalali_date='1403-03-09',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 5:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم1224",
            call_put="c",
            start_date="1402-07-24",
            end_date="1402-12-23",
            strike_price=20000,
            risk_free_rate=0.3,
            expiration_jalali_date='1402-12-23',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 6:
        run_option_analysis(
            underlying_stock_name="خودرو",
            option_stock_name="ضخود1218",
            call_put="c",
            start_date="1402-09-22",
            end_date="1402-11-15",
            strike_price=2600,
            risk_free_rate=0.3,
            expiration_jalali_date='1402-12-02',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 7:
        run_option_analysis(
            underlying_stock_name="شستا",
            option_stock_name="ضستا2026",
            call_put="c",
            start_date="1402-10-30",
            end_date="1403-02-02",
            strike_price=1200,
            risk_free_rate=0.3,
            expiration_jalali_date='1403-02-12',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 8:
        run_option_analysis(
            underlying_stock_name="خساپا",
            option_stock_name="ضسپا2006",
            call_put="c",
            start_date="1402-12-05",
            end_date="1403-02-19",
            strike_price=2600,
            risk_free_rate=0.3,
            expiration_jalali_date='1403-02-26',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    elif option_number == 9:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم1219",
            call_put="c",
            start_date='1402-06-01',
            end_date='1402-09-15',
            strike_price=13000,
            risk_free_rate=0.3,
            expiration_jalali_date='1402-12-23',
            window_size_volatility=int(10 * 3.5 * 3600),
            window_size_normal=int(10 * 3.5 * 3600),
            z_threshold_normal=1
        )
    else:
        print("Invalid option number. Please enter a number from 1 to 9.")

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    
    # Example usage:
    option_number = int(input("Enter the option number to run (1-9): "))
    run_selected_analysis(option_number)
