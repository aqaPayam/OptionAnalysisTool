@echo off
chcp 65001
start cmd /k "python main.py --mode run --underlying_name ""خودرو"" --underlying_ticker ""IRO1IKCO0001"" --option_name ""طخود0137"" --option_ticker ""IROFIKCO9N41"" --expiration_date ""2025-03-26"" --strike_price 3250.0 --call_put p --can_trade_in_same_direction"