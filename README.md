
# Option Analysis Tool

This project provides a Python tool for analyzing options and generating trading signals based on the Black-Scholes pricing model and volatility calculations. It processes options data, calculates implied and estimated volatilities, and generates trading signals using statistical analysis.

## Features

- Downloads and processes underlying stock and option data.
- Computes implied volatility and estimated volatility for options.
- Calculates Black-Scholes price dynamically based on estimated volatility.
- Generates buy/sell/hold signals using a Z-score based approach.

## Mathematical Background

### 1. Black-Scholes Model

The **Black-Scholes formula** is a widely used model for calculating the theoretical price of options. For a European call option, the Black-Scholes price \( C \) is given by:

\(
C = S_0 \cdot N(d_1) - K \cdot e^{-r \cdot T} \cdot N(d_2)
\)

where:

- \( S_0 \): Current price of the underlying asset
- \( K \): Strike price of the option
- \( r \): Risk-free interest rate
- \( T \): Time to expiration in years
- \( N(d) \): Cumulative distribution function of the standard normal distribution

and

\(
d_1 = rac{\ln(S_0 / K) + (r + \sigma^2 / 2) \cdot T}{\sigma \sqrt{T}}, \quad d_2 = d_1 - \sigma \sqrt{T}
\)

In the formula, \( \sigma \) is the volatility of the underlying asset, which we estimate using implied and historical volatilities.

### 2. Implied Volatility

**Implied volatility** is the market’s forecast of a likely movement in the underlying asset’s price. It is derived from the market price of an option and is obtained by iteratively adjusting \( \sigma \) in the Black-Scholes formula until the theoretical price matches the market price.

### 3. Estimated Volatility

Estimated volatility is calculated using a rolling average of implied volatilities over a specified window. This rolling volatility provides a historical context to the fluctuations in the option price, assisting in predicting future price behavior.

### 4. Z-score for Signal Generation

To determine trading signals, the tool uses the **Z-score**. The Z-score measures the deviation of the option price from its mean relative to its standard deviation, calculated as:

\(
Z = rac{(P_{	ext{BS}} - P_{	ext{Option}}) - \mu_{	ext{diff}}}{\sigma_{	ext{diff}}}
\)

where:

- \( P_{	ext{BS}} \): Black-Scholes calculated price
- \( P_{	ext{Option}} \): Observed option price in the market
- \( \mu_{	ext{diff}} \): Rolling mean of the price difference between \( P_{	ext{BS}} \) and \( P_{	ext{Option}} \)
- \( \sigma_{	ext{diff}} \): Rolling standard deviation of the price difference

#### Signal Generation

Based on the Z-score, signals are generated as follows:

- **Sell**: If \( Z > 	ext{z_threshold} \), the option is overvalued.
- **Buy**: If \( Z < -	ext{z_threshold} \), the option is undervalued.
- **Hold**: If \( |Z| \leq 	ext{z_threshold} \), the option is fairly priced.

## Prerequisites

Install the required packages:

```bash
pip install persiantools finpy_tse py_vollib jdatetime numpy pandas tqdm
```

## Usage

### 1. Running the Script

The main function, `run_option_analysis`, performs the entire process from downloading data to signal generation. You can adjust the parameters based on your desired option symbols, dates, and risk-free rate.

### Example

In the script, several example calls to `run_option_analysis` demonstrate the tool’s usage for different options and dates:

```python
run_option_analysis(
    underlying_stock_name="خودرو",
    option_stock_name="ضخود8034",
    call_put="c",
    start_date="1403-05-15",
    end_date="1403-07-25",
    strike_price=2400,
    risk_free_rate=0.3,
    expiration_jalali_date='1403-08-02'
)
```

### Parameters

- **underlying_stock_name**: Ticker symbol for the underlying stock.
- **option_stock_name**: Ticker symbol for the option.
- **call_put**: Specify "c" for a call option or "p" for a put option.
- **start_date, end_date**: Jalali calendar start and end dates for the analysis.
- **strike_price**: Strike price of the option.
- **risk_free_rate**: Annual risk-free interest rate.
- **expiration_jalali_date**: Expiration date in Jalali calendar.

## Output

The analysis results, including trading signals, are saved as a pickle file with the format:

```
option_signals_{option_stock_name}_{start_date}_to_{end_date}.pkl
```

This file contains:
- Average underlying and option prices
- Black-Scholes price
- Implied and estimated volatility
- Buy/Sell/Hold signals with Z-scores

## License

This project is open-source and available for use and modification under the MIT License.
