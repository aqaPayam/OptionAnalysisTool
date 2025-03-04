# trading_api.py

import json
import time

import pandas as pd
import requests
from typing import Optional, List
from config import get_config


class TradingAPI:
    """
    Class to interact with the trading API.
    """

    def __init__(self):
        config = get_config()
        self.base_url = config.BASE_URL
        self.market_url = config.MARKET_URL
        self.headers = config.HEADERS
        self.max_retries = config.MAX_RETRIES
        self.option_ticker = config.OPTION_TICKER
        self.mdapi_url = config.MDAPI_URL  # Assign the Market Data API URL

    def _make_request(self, method: str, url: str, data: Optional[dict] = None) -> Optional[dict]:
        config = get_config()
        """
        Makes an HTTP request with retries on failure.

        Args:
            method (str): HTTP method ('GET' or 'POST').
            url (str): The API endpoint URL.
            data (Optional[dict]): The payload for POST requests.

        Returns:
            Optional[dict]: The JSON response if successful, else None.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                if method.upper() == 'POST':
                    response = requests.post(url, headers=self.headers, data=json.dumps(data))
                elif method.upper() == 'GET':
                    response = requests.get(url, headers=self.headers)
                else:
                    print(f"ERROR: Unsupported HTTP method: {method}")
                    return None

                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"WARNING: Attempt {attempt} failed for {url}: {e}")
                time.sleep(config.SLEEP_INTERVAL)
        print(f"ERROR: Max retries reached for {url}.")
        return None

    def fetch_order_book(self, ticker: str) -> Optional[List[float]]:
        """
        Retrieves the current order book for a specific ticker.

        Args:
            ticker (str): The ISIN ticker symbol.

        Returns:
            Optional[List[float]]: A list containing [sell_volume, sell_price, buy_price, buy_volume].
        """
        url = f"{self.market_url}/Queue/BestLimitWithSize?isin={ticker}"

        response = self._make_request('GET', url)

        if response:
            try:
                buy = response.get('buy', [])
                sell = response.get('sell', [])

                # Handle cases where either buy or sell is empty
                if buy and sell:
                    buy_data = buy[0]
                    sell_data = sell[0]
                    return [sell_data['v'], sell_data['p'], buy_data['p'], buy_data['v']]
                elif sell:
                    sell_data = sell[0]
                    return [sell_data['v'], sell_data['p'], sell_data['p'], sell_data['v']]
                elif buy:
                    buy_data = buy[0]
                    return [buy_data['v'], buy_data['p'], buy_data['p'], buy_data['v']]
                else:
                    print(f"WARNING: No buy or sell data available for ticker {ticker}.")
            except (KeyError, IndexError) as e:
                print(f"ERROR: Error extracting order book data for {ticker}: {e}")
        return None

    def place_order(self, ticker: str, price: float, quantity: int, side: str) -> Optional[dict]:
        """
        Sends a new order to the trading API.

        Args:
            ticker (str): The ISIN ticker symbol.
            price (float): The price at which to place the order.
            quantity (int): The volume of the order.
            side (str): 'buy' or 'sell'.

        Returns:
            Optional[dict]: The API response if successful, else None.
        """
        url = f"{self.base_url}/orders/NewOrder"
        data = {
            "validity": 1,  # Assuming 'validity' is 'Day' order
            "validityDate": None,
            "price": price,
            "volume": quantity,
            "side": 1 if side.lower() == 'buy' else 2,
            "isin": ticker,
            "accountType": 1  # Adjust account type if necessary
        }
        response = self._make_request('POST', url, data)
        if response:
            print(f"INFO: Placed {side} order for {ticker} at price {price} and volume {quantity}.")
        else:
            print(f"ERROR: Failed to place {side} order for {ticker}.")
        return response

    def modify_order(self, price: float, order_id: int, volume: int, ticker: str, side: str) -> Optional[dict]:
        """
        Modifies an existing order.

        Args:
            price (float): The new price for the order.
            order_id (int): The serial number of the order to modify.
            volume (int): The new volume for the order.
            ticker (str): The ISIN ticker symbol.
            side (str): 'buy' or 'sell'.

        Returns:
            Optional[dict]: The API response if successful, else None.
        """
        url = f"{self.base_url}/orders/EditOrder"
        data = {
            "validity": 1,  # Assuming 'validity' is 'Day' order
            "validityDate": None,
            "price": price,
            "volume": volume,
            "side": 1 if side.lower() == 'buy' else 2,
            "isin": ticker,
            "accountType": 1,  # Adjust account type if necessary
            "serialNumber": order_id
        }
        response = self._make_request('POST', url, data)
        if response:
            print(f"INFO: Modified {side} order {order_id} for {ticker} to price {price} and volume {volume}.")
        else:
            print(f"ERROR: Failed to modify {side} order {order_id} for {ticker}.")
        return response

    def fetch_open_orders(self) -> Optional[List[dict]]:
        """
        Retrieves all open orders and returns only the necessary fields.

        Returns:
            Optional[List[dict]]: A list of processed open orders if successful, else None.
        """
        url = f"{self.base_url}/orders/GetOpenOrders"
        response = self._make_request('GET', url)
        if response:
            try:
                # Process each order in the response
                processed_orders = []
                for order in response:
                    processed_order = {
                        'isin': order.get('isin'),
                        'orderSide': int(order.get('orderSide', 0)),
                        'remainedVolume': int(order.get('remainedVolume', 0)),
                        'price': float(order.get('price', 0.0)),
                        'serialNumber': int(order.get('serialNumber', 0)),
                    }
                    processed_orders.append(processed_order)
                return processed_orders
            except Exception as e:
                print(f"ERROR: Error processing open orders: {e}")
                return None
        else:
            return None

    def buy(self, ticker: str, price: float, quantity: int) -> None:
        """
        Places or modifies a buy order for the specified ticker.

        Args:
            ticker (str): The ISIN ticker symbol.
            price (float): The desired price for the buy order.
            quantity (int): The desired quantity for the buy order.
        """
        open_orders = self.fetch_open_orders()
        if not open_orders:
            # No open orders, place a new buy order
            self.place_order(ticker, price, quantity, 'buy')
            return

        # Check if there is an existing buy order for the ticker
        buy_orders = [
            order for order in open_orders
            if order['orderSide'] == 1 and order['isin'] == ticker
        ]

        if not buy_orders:
            # No existing buy order for the ticker, place a new one
            self.place_order(ticker, price, quantity, 'buy')
            return

        # Modify the existing buy order
        for order in buy_orders:
            current_price = order['price']
            current_quantity = order['remainedVolume']
            serial_number = order['serialNumber']

            if price != current_price or quantity != current_quantity:
                # Modify the order to the desired price and quantity
                self.modify_order(price, serial_number, quantity, ticker, 'buy')
            else:
                # Order already at desired price and quantity, no action needed
                print(f"INFO: Buy order for {ticker} already at desired price and quantity.")
            return  # Assuming only one buy order per ticker

    def sell(self, ticker: str, price: float, quantity: int) -> None:
        """
        Places or modifies a sell order for the specified ticker.

        Args:
            ticker (str): The ISIN ticker symbol.
            price (float): The desired price for the sell order.
            quantity (int): The desired quantity for the sell order.
        """
        open_orders = self.fetch_open_orders()
        if not open_orders:
            # No open orders, place a new sell order
            self.place_order(ticker, price, quantity, 'sell')
            return

        # Check if there is an existing sell order for the ticker
        sell_orders = [
            order for order in open_orders
            if order['orderSide'] == 2 and order['isin'] == ticker
        ]

        if not sell_orders:
            # No existing sell order for the ticker, place a new one
            self.place_order(ticker, price, quantity, 'sell')
            return

        # Modify the existing sell order
        for order in sell_orders:
            current_price = order['price']
            current_quantity = order['remainedVolume']
            serial_number = order['serialNumber']

            if price != current_price or quantity != current_quantity:
                # Modify the order to the desired price and quantity
                self.modify_order(price, serial_number, quantity, ticker, 'sell')
            else:
                # Order already at desired price and quantity, no action needed
                print(f"INFO: Sell order for {ticker} already at desired price and quantity.")
            return  # Assuming only one sell order per ticker

    def cancel_orders(self, serial_numbers: List[int]) -> Optional[dict]:
        """
        Cancels orders given their serial numbers.

        Args:
            serial_numbers (List[int]): A list of serial numbers representing the orders to cancel.

        Returns:
            Optional[dict]: The API response if successful, else None.
        """
        url = f"{self.base_url}/orders/CancelOrders"
        data = {
            "serialNumbers": serial_numbers
        }
        response = self._make_request('POST', url, data)
        if response:
            print(f"INFO: Cancelled orders with serial numbers: {serial_numbers}")
        else:
            print(f"ERROR: Failed to cancel orders with serial numbers: {serial_numbers}")
        return response

    def get_net_worth_balance(self) -> Optional[tuple[float, float]]:
        """
        Retrieves the netWorthBalance, optionMarginBlockAmount, buyVolume, and sellVolume
        for the configured OPTION_TICKER.

        Returns:
            Optional[tuple[float, float]]: The computed net worth and volume if conditions are met, else None.
        """
        url = f"{self.base_url}/positions/options/Portfolio"
        response = self._make_request('GET', url)

        if response:
            try:
                #print("INFO: Retrieved portfolio positions successfully.")
                for position in response:
                    if position.get('isin') == self.option_ticker:
                        net_worth_balance = int(position.get('netWorthBalance', 0))
                        option_margin_block_amount = int(position.get('optionMarginBlockAmount', 0))
                        buy_volume = float(position.get('buyVolume', 0.0))
                        sell_volume = float(position.get('sellVolume', 0.0))

                        # Calculate volume based on buyVolume and sellVolume
                        if sell_volume == 0:
                            volume = buy_volume
                        elif buy_volume == 0:
                            volume = -sell_volume
                        else:
                            volume = buy_volume - sell_volume

                        if option_margin_block_amount == 0 and net_worth_balance > 0:
                            #print(f"INFO: netWorthBalance for {self.option_ticker} is {net_worth_balance}")
                            return net_worth_balance, volume

                        elif option_margin_block_amount != 0 and net_worth_balance < 0:
                            adjusted_net_worth = -option_margin_block_amount
                            #print(f"INFO: Adjusted net worth for {self.option_ticker} is {adjusted_net_worth}")
                            return adjusted_net_worth, volume

                        else:
                            print("ERROR: Conditions not met for calculating net worth.")
                            return 0, volume

                print(f"WARNING: No position found for ISIN {self.option_ticker}.")
            except (KeyError, TypeError) as e:
                print(f"ERROR: Error processing portfolio positions: {e}")
        else:
            print("ERROR: Failed to retrieve portfolio positions.")

        return 0, 0.0

    def get_option_details_from_mdpapi(self, option_id: str) -> Optional[dict]:
        """
        Fetches details of a specific trading option from mdpapi.pikadbazar.ir.

        Args:
            option_id (str): The ID of the option.

        Returns:
            Optional[dict]: The response JSON if successful, else None.
        """
        url = f"https://mdpapi.pikadbazar.ir/api/v1/optionDetail/{option_id}/same"

        return self._make_request("GET", url)

    def get_portfolio_options_df(self):
        """
        Sends a GET request to the Portfolio endpoint, processes the response,
        and returns a DataFrame with the following columns:
            - OPTION_NAME: from "symbol"
            - OPTION_TICKER: from "isin"
            - EXPIRATION_DATE: from "physicalSettlementDateJalali" (fallback to cashSettlementDateJalali if needed)
            - STRIKE_PRICE: from "strikePrice"
            - CALL_PUT: determined from the first letter of the symbol
                        (if it starts with 'ض' then it's call, if it starts with 'ط' then it's put)

        Returns:
            pd.DataFrame: DataFrame with the processed portfolio option data.
        """
        url = f"{self.base_url}/positions/options/Portfolio"
        response = self._make_request('GET', url)

        if not response:
            print("No response received from portfolio options API.")
            return None

        processed_data = []
        for item in response:
            option_ticker = item.get("isin", "")
            option_name = item.get("symbol", "")
            # Use physicalSettlementDateJalali if available; otherwise try cashSettlementDateJalali.
            expiration_date = item.get("physicalSettlementDateJalali", item.get("cashSettlementDateJalali", ""))
            strike_price = item.get("strikePrice", 0)

            # Determine CALL_PUT based on the starting letter of the symbol:
            # If symbol starts with 'ض' then it's a call, if it starts with 'ط' then it's a put.
            if option_name.startswith("ض"):
                call_put = "c"
            elif option_name.startswith("ط"):
                call_put = "p"
            else:
                call_put = ""

            processed_data.append({
                "OPTION_NAME": option_name,
                "OPTION_TICKER": option_ticker,
                "EXPIRATION_DATE": expiration_date,
                "STRIKE_PRICE": strike_price,
                "CALL_PUT": call_put
            })

        return pd.DataFrame(processed_data)
