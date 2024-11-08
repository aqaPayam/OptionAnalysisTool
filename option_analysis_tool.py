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
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import argparse

def process_and_save_underlying_and_option_data(underlying_stock, option_stock, start_date, end_date):
    save_folder="data_files"
    os.makedirs(save_folder, exist_ok=True)
    
    def editing_data(df):
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
        file_name = os.path.join(save_folder, f"{market_type}_{stock_name}_{start_date}_{end_date}.pkl")
        
        # Check if file already exists
        if os.path.exists(file_name):
            print(f"File {file_name} already exists. Loading data from file.")
            datapirim = pd.read_pickle(file_name)
            return datapirim
        
        # If file doesn't exist, proceed with downloading and processing
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
        datapirim.to_pickle(file_name)

        csv_file_name = os.path.join(save_folder, f"{market_type}_{stock_name}_{start_date}_{end_date}.csv")
        datapirim.to_csv(csv_file_name)
        print(f"Data saved as {file_name} and CSV saved as {csv_file_name}!")
        
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
    key_error_counter = 0

    # Define the valid time range between 9:00 and 12:30
    valid_time_start = pd.to_datetime("09:15:00").time()
    valid_time_end = pd.to_datetime("12:30:00").time()

    for date in tqdm(underlying_market_df.columns, desc="Processing Market Data", total=underlying_market_df.shape[1]):
        try:
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

                    if avg_price_option == 0 :
                        avg_price_option = None

                    if avg_price_underlying == 0 :
                        avg_price_underlying = None

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
        except KeyError:
            key_error_counter += 1
            print(f"Day {date} skipped due to KeyError in option data.")
            continue  # Skip the entire date if KeyError occurs

    # Print the counters
    print(f"Rows with null values: {null_counter}")
    print(f"Rows skipped by time: {skip_by_time_counter}")
    print(f"Errors caught in try-except of implied volatility calculator: {try_except_counter}")
    print(f"KeyErrors caught when accessing option data: {key_error_counter}")

    if len(flattened_data) == 0:
        raise ValueError(
                f"The processed data contains only null values. Please check the input data.   TSMSE = GOH")

    flattened_series = pd.Series(flattened_data, index=pd.MultiIndex.from_tuples(index_tuples, names=["Date", "Time"]))

    return flattened_series

def calculate_simple_moving_average(rolling_vols, total_points_in_window):
    """
    Calculate the simple moving average (SMA) of implied volatility using only past values in the rolling window.

    Parameters:
    - rolling_vols: List of recent implied_vol values within the window.

    Returns:
    - sma_estimated_vol: The calculated simple moving average based on the rolling window.
    """
    # Calculate SMA only if there are past values
    if len(rolling_vols) > 0:
        sma_estimated_vol = sum(rolling_vols) / len(rolling_vols)
    else:
        sma_estimated_vol = np.nan  # No past data available

    return sma_estimated_vol

def calculate_exponential_moving_average(previous_ema, implied_vol, alpha):
    """
    Update the exponential moving average (EMA) using only past values (previous EMA) for implied volatility.

    Parameters:
    - previous_ema: The last EMA value calculated, based on past values only.
    - implied_vol: The current implied_vol to incorporate.
    - alpha: Smoothing factor for EMA calculation.

    Returns:
    - ema_estimated_vol: Updated EMA value.
    """
    if np.isnan(previous_ema) and not pd.isnull(implied_vol):
        # Initialize EMA with the first observed value in the series if no prior EMA exists
        ema_estimated_vol = implied_vol
    elif not pd.isnull(implied_vol):
        # Calculate EMA using only the previous EMA (no use of current `vol_t` for estimation)
        ema_estimated_vol = alpha * implied_vol + (1 - alpha) * previous_ema
    else:
        # If `implied_vol` is NaN, the previous EMA remains unchanged
        ema_estimated_vol = previous_ema

    return ema_estimated_vol

def calculate_estimated_volatility(call_series, smoothing_param):
    """
    Calculate the estimated volatility for each row in call_series, using either SMA or EMA based on the parameters.
    Only past data is used to estimate the volatility at each point.

    Parameters:
    - call_series: A pandas Series containing [avg_price_underlying, avg_price_option, implied_vol] with MultiIndex (date, time).
    - smoothing_param: A single parameter used to determine either the EMA alpha or SMA window size.
      - If smoothing_param is a float between 0 and 1 (0 < smoothing_param <= 1), it is interpreted as EMA alpha.
      - If smoothing_param is an integer greater than 1, it is interpreted as the total_points_in_window for SMA.

    Returns:
    - extended_series: A pandas Series containing [avg_price_underlying, avg_price_option, implied_vol, estimated_vol]
      for each row, aligned with the input Series.
    """
    # Determine the parameters based on the smoothing_param input
    if  0 < smoothing_param <= 1:
        alpha = smoothing_param
        total_points_in_window = None  # Not used when EMA is chosen
        
    elif smoothing_param > 1:
        alpha = None
        total_points_in_window = smoothing_param
    else:
        raise ValueError("smoothing_param must be a float (0 < smoothing_param <= 1) for EMA or an integer > 1 for SMA.")

    # Initialize an empty list to store extended data (with estimated volatility)
    extended_data = []

    # Initialize parameters for the two methods
    rolling_vols = []
    ema_estimated_vol = np.nan  # Used only if alpha is provided

    # Loop through each row in the call_series
    for index, row_data in tqdm(call_series.items(), total=len(call_series), desc="Calculating Estimated Volatility"):
        avg_price_underlying = row_data[0]
        avg_price_option = row_data[1]
        implied_vol = row_data[2]

        # Determine the method based on whether alpha is provided
        if alpha is not None:
            # Use EMA if alpha is specified, based on past EMA value and past implied_vols only
            estimated_vol = ema_estimated_vol
            ema_estimated_vol = calculate_exponential_moving_average(ema_estimated_vol, implied_vol, alpha)
        else:
            # Use SMA otherwise, calculated based on past rolling values only
            estimated_vol = calculate_simple_moving_average(rolling_vols, total_points_in_window)
            if not pd.isnull(implied_vol):
                rolling_vols.append(implied_vol)
                if len(rolling_vols) > total_points_in_window:
                    rolling_vols.pop(0)  # Maintain the window size

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
                try :
                    black_scholes_price = black_scholes(call_put, avg_price_underlying, strike_price, T, risk_free_rate,
                                                        estimated_vol)
                except :
                    print("error in calculating black schole price with this (skipped) : ",call_put, avg_price_underlying, strike_price, T, risk_free_rate, estimated_vol )
                    black_scholes_price = np.nan

            else:
                black_scholes_price = np.nan

        # Append the original data along with the calculated Black-Scholes price
        extended_data.append([avg_price_underlying, avg_price_option, black_scholes_price, implied_vol, estimated_vol])

    # Create a new pandas Series with the same index as the input series
    extended_series = pd.Series(extended_data, index=call_series.index)

    return extended_series

def generate_option_signals(option_series, window_size):
    """
    Generate buy/sell/hold signals along with statistics such as price difference, rolling mean,
    standard deviation, and Z-score from the given option data series.

    Parameters:
    option_series (pd.Series): A Series where each entry contains a list of option data.
                               [avg_price_underlying, avg_price_option, black_scholes_price, implied_vol, estimated_vol]
    window_size (int): Number of previous data points to consider for calculating rolling mean and std dev.


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
    price_difference =  option_price - black_scholes_price

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
        else:
            # Calculate Z-score (how many standard deviations current_diff is from the mean)
            z_score = (current_diff - mean_diff) / std_diff

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
            'z_score': z_score  # Statistic showing how far the price difference is from the mean
        })

    # Use tqdm to monitor progress while applying the function to each item
    for index, row_data in tqdm(option_series.items(), total=len(option_series), desc="Calculating Option Signals"):
        compute_signal_and_stats(index)

    # Convert the list of results to a DataFrame
    result_df = pd.DataFrame(results, index=option_series.index)

    # Count the occurrences where z_score is under -1 and over +1
    under_negative_one_count = (result_df['z_score'] < -1).sum()
    over_positive_one_count = (result_df['z_score'] > 1).sum()

    print(f"Number of 'z_score' values under -1: {under_negative_one_count}")
    print(f"Number of 'z_score' values over +1: {over_positive_one_count}")


    return result_df

def perform_trade_analysis(data, z_values, save_path="results/", option_stock_name="", start_date="", end_date="", window_size=0):
    """
    Perform trade analysis with buy-sell pairs based on multiple z-score thresholds,
    saving plots and DataFrames for each z-score threshold.
    
    Parameters:
    - data: pd.DataFrame with MultiIndex (Date, Time) and columns including 'avg_price_option' and 'z_score'.
    - z_values: list of float values for different z-score thresholds to test.
    - save_path: str, directory path to save the plots and DataFrames.
    - option_stock_name: str, the name of the option stock for file naming.
    - start_date: str, the analysis start date for file naming.
    - end_date: str, the analysis end date for file naming.
    - window_size: int, the window size used in the analysis for file naming.
    
    Returns:
    - None (prints analysis results, saves distribution plots and DataFrames)
    """
    
    os.makedirs(save_path, exist_ok=True)  # Ensure the save path exists

    def generate_buy_sell_pairs(data, z_threshold, window_size):
        buy_sell_pairs_list = []
        current_buy = None

        # Define the columns for the DataFrame in case of an empty return
        columns = ['buy_date', 'buy_time', 'buy_price', 'sell_date', 'sell_time', 'sell_price', 'profit_loss', 'profitability_percentage']

        # Loop through each row in the data with tqdm progress bar
        for idx, row in tqdm(data.iterrows(), total=len(data), desc=f"Processing Buy-Sell Pairs for Z={z_threshold}, Window Size={window_size}"):
            date, time = idx

            if row['z_score'] < -z_threshold and current_buy is None:
                current_buy = {'buy_date': date, 'buy_time': time, 'buy_price': row['avg_price_option']}
                
            elif row['z_score'] > z_threshold and current_buy is not None:
                sell_info = {'sell_date': date, 'sell_time': time, 'sell_price': row['avg_price_option']}
                profit_loss = sell_info['sell_price'] - current_buy['buy_price']
                
                # Calculate profitability percentage
                profitability_percentage = ((sell_info['sell_price'] - current_buy['buy_price']) / current_buy['buy_price']) * 100
                
                buy_sell_pairs_list.append({
                    'buy_date': current_buy['buy_date'], 'buy_time': current_buy['buy_time'], 
                    'buy_price': current_buy['buy_price'], 'sell_date': sell_info['sell_date'], 
                    'sell_time': sell_info['sell_time'], 'sell_price': sell_info['sell_price'], 
                    'profit_loss': profit_loss, 'profitability_percentage': profitability_percentage
                })
                current_buy = None

        # Return DataFrame, whether populated or empty
        return pd.DataFrame(buy_sell_pairs_list, columns=columns)

    
    # Analyze trades for each z threshold in z_values
    for z_threshold in z_values:
        print(f"\nAnalyzing for Z-Threshold: {z_threshold}, Window Size: {window_size}")
        
        # Generate buy-sell pairs for the current z_threshold
        buy_sell_pairs = generate_buy_sell_pairs(data, z_threshold, window_size)
        
        # Check if buy_sell_pairs DataFrame is empty
        if buy_sell_pairs.empty:
            print(f"No trades generated for Z-Threshold: {z_threshold}, Window Size: {window_size}. Skipping analysis and saving.")
            continue  # Skip to the next z_threshold if there are no trades
        
        # Calculate trade statistics
        total_trades = len(buy_sell_pairs)
        profitable_trades = buy_sell_pairs[buy_sell_pairs['profit_loss'] > 0]
        num_profitable_trades = len(profitable_trades)
        percentage_profitable = (num_profitable_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Print analysis results
        print(f"Total Trades for Z-Threshold: {z_threshold}, Window Size: {window_size}: {total_trades}")
        print(f"Profitable Trades for Z-Threshold: {z_threshold}, Window Size: {window_size}: {num_profitable_trades}")
        print(f"Percentage of Profitable Trades for Z-Threshold: {z_threshold}, Window Size: {window_size}: {percentage_profitable:.2f}%")
        
        # Save the buy-sell pairs DataFrame as a pickle file
        df_filename = f"{save_path}buy_sell_pairs_window_{window_size}_z_{z_threshold}.pkl"
        buy_sell_pairs.to_pickle(df_filename)


        csv_filename = f"{save_path}buy_sell_pairs_window_{window_size}_z_{z_threshold}.csv"
        buy_sell_pairs.to_csv(csv_filename)

        print(f"Data saved to {df_filename} (pickle) and {csv_filename} (CSV) for Z-Threshold: {z_threshold}, Window Size: {window_size}")


        
        # Plot and save the distribution of profit/loss percentage
        plt.figure(figsize=(12, 7))
        sns.histplot(buy_sell_pairs['profitability_percentage'], bins=50, kde=True, edgecolor='black')  # Smaller bins, in percentage
        plt.title(f"Profitability Distribution (as %) for {option_stock_name}\nWindow Size = {window_size}, Z-Threshold = {z_threshold}")
        plt.xlabel("Profit/Loss (%)")
        plt.ylabel("Frequency")
        plt.axvline(0, color='red', linestyle='dashed', linewidth=1, label="Break-Even")
        plt.legend()

        # Annotate the total number of trades on the plot
        plt.annotate(f'Total Trades: {total_trades}', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, 
                     bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        # Save the plot
        plot_filename = f"{save_path}profit_loss_distribution_window_{window_size}_z_{z_threshold}.png"
        plt.savefig(plot_filename)
        print(f"Plot saved to {plot_filename} for Z-Threshold: {z_threshold}, Window Size: {window_size}") 
        plt.close()  # Close the plot to free up memory 

def run_option_analysis(underlying_stock_name = "", option_stock_name= "", call_put="c", start_date= "", end_date= "",
                        strike_price= "", risk_free_rate=0.30, expiration_jalali_date= "",
                        window_sizes_for_normal=[
                            int(2 * 3.5 * 3600),
                            int(1 * 3.5 * 3600),
                            int(2 * 3600),
                            int(1 * 3600),
                            600
                        ],
                        alphas_or_window_size_for_volatility_estimation=[0.9, 0.7, 0.5, 0.2, 0.1, 0.05],
                        z_values=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5]):
    """
    This function encapsulates the process of analyzing option market data and generating trading signals
    based on Black-Scholes price and estimated volatility for different window sizes and alpha values.

    Parameters:
        - underlying_stock (str): The ticker or symbol for the underlying stock
        - option_stock (str): The ticker or symbol for the option
        - start_date (str): The start date for fetching market data
        - end_date (str): The end date for fetching market data
        - strike_price (float): The option strike price
        - risk_free_rate (float): The risk-free interest rate
        - expiration_jalali_date (str): The expiration date in Jalali calendar format ('YYYY-MM-DD')
        - window_sizes_for_normal_disat (list of int): A list of window sizes for calculating normal distribution parameters
        - alphas_or_window_size_for_volatility_estimation (list of float or int): List of alpha values or window sizes for volatility estimation
        - z_values (list of float): List of z-score thresholds for performing trade analysis.

    Returns:
        - results (dict): A dictionary where each key is a tuple (normal_window_size, alpha/window_size for volatility) 
                          and each value is a DataFrame of option signals.
    """
    
    results = {}

    # Define the main save path based on option stock name, start date, and end date
    main_save_path = f"results/{option_stock_name}_{start_date}_to_{end_date}/"
    os.makedirs(main_save_path, exist_ok=True)

    # Step 1: Process and save underlying and option data
    underlying_stock, option_stock = process_and_save_underlying_and_option_data(
        underlying_stock=underlying_stock_name, option_stock=option_stock_name, start_date=start_date, end_date=end_date
    )

    # Step 2: Flatten market data with calculated implied volatility
    call_series = flatten_market_data_with_volatility(
        underlying_market_df=underlying_stock, options_market_df=option_stock,
        strike_price=strike_price, risk_free_rate=risk_free_rate, expiration_jalali_date=expiration_jalali_date,
        call_put=call_put
    )

    for normal_window_size in window_sizes_for_normal:
        for alpha_or_vol_window_size in alphas_or_window_size_for_volatility_estimation:

            print(f"Running analysis for normal window size: {normal_window_size} and volatility parameter: {alphas_or_window_size_for_volatility_estimation}")

            # Step 3: Calculate estimated volatility over the specified window size or alpha value
            series_with_volatility = calculate_estimated_volatility(
                call_series, smoothing_param=alpha_or_vol_window_size
            )

            # Step 4: Calculate Black-Scholes prices for the option
            final_series = calculate_black_scholes_price(
                call_series=series_with_volatility, strike_price=strike_price,
                risk_free_rate=risk_free_rate, expiration_jalali_date=expiration_jalali_date, call_put=call_put
            )

            # Step 5: Generate option signals based on calculated Black-Scholes prices
            result = generate_option_signals(option_series=final_series, window_size=normal_window_size)

            # Save the result with a unique filename for each normal_window_size and alpha_or_vol_window_size in the "signals" folder
            filename = f"{main_save_path}option_signals_normal_window_{normal_window_size}_volatility_param_{alpha_or_vol_window_size}.pkl"
            result.to_pickle(filename)

            csv_filename = f"{main_save_path}option_signals_normal_window_{normal_window_size}_volatility_param_{alpha_or_vol_window_size}.csv"
            result.to_csv(csv_filename)
            print(f"Results saved to {filename} (pickle) and {csv_filename} (CSV)")

            # Store the result in the dictionary with a tuple key (normal_window_size, alpha_or_vol_window_size)
            results[(normal_window_size, alpha_or_vol_window_size)] = result
            print(f"Finished analysis for {option_stock_name} with normal window size {normal_window_size} and volatility parameter {alpha_or_vol_window_size}")

            # Step 6: Perform trade analysis for each combination using perform_trade_analysis function
            perform_trade_analysis(result, z_values, save_path=main_save_path,
                                   option_stock_name=option_stock_name, start_date=start_date, end_date=end_date, window_size=normal_window_size)

    return results

def run_selected_analysis(option_number):
    if option_number == 0:
        for i in range(1, 10):
            print(f"Running analysis for option {i}...")
            run_selected_analysis(i)
    elif option_number == 1:
        run_option_analysis(
            underlying_stock_name="خودرو",
            option_stock_name="ضخود8034",
            start_date="1403-05-15",
            end_date="1403-07-25",
            strike_price=2400,
            expiration_jalali_date='1403-08-02'
        )
    elif option_number == 2:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم7025",
            start_date="1403-05-13",
            end_date="1403-07-23",
            strike_price=16000,
            expiration_jalali_date='1403-07-25'
        )
    elif option_number == 3:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم3006",
            start_date="1402-11-10",
            end_date="1403-03-21",
            strike_price=20000,
            expiration_jalali_date='1403-03-23'
        )
    elif option_number == 4:
        run_option_analysis(
            underlying_stock_name="خودرو",
            option_stock_name="ضخود3084",
            start_date="1403-01-28",
            end_date="1403-02-30",
            strike_price=3000,
            expiration_jalali_date='1403-03-09'
        )
    elif option_number == 5:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم1224",
            start_date="1402-07-24",
            end_date="1402-12-23",
            strike_price=20000,
            expiration_jalali_date='1402-12-23'
        )
    elif option_number == 6:
        run_option_analysis(
            underlying_stock_name="خودرو",
            option_stock_name="ضخود1218",
            start_date="1402-09-22",
            end_date="1402-11-15",
            strike_price=2600,
            expiration_jalali_date='1402-12-02'
        )
    elif option_number == 7:
        run_option_analysis(
            underlying_stock_name="شستا",
            option_stock_name="ضستا2026",
            start_date="1402-10-30",
            end_date="1403-02-02",
            strike_price=1200,
            expiration_jalali_date='1403-02-12'
        )
    elif option_number == 8:
        run_option_analysis(
            underlying_stock_name="خساپا",
            option_stock_name="ضسپا2006",
            start_date="1402-12-05",
            end_date="1403-02-19",
            strike_price=2600,
            expiration_jalali_date='1403-02-26'
        )
    elif option_number == 9:
        run_option_analysis(
            underlying_stock_name="اهرم",
            option_stock_name="ضهرم1219",
            start_date='1402-06-01',
            end_date='1402-09-15',
            strike_price=13000,
            expiration_jalali_date='1402-12-23'
        )
    else:
        print("Invalid option number. Please enter a number from 0 to 9.")

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    
    parser = argparse.ArgumentParser(description="Run selected analysis based on option number.")
    parser.add_argument("-number", type=int, choices=range(0, 10), help="Option number to run (0-9)")
    args = parser.parse_args()

    if args.number is not None:
        run_selected_analysis(args.number)
    else:
        print("Please provide an option number using -n flag (0-9).")
