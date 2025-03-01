@echo off
chcp 65001
start cmd /k "python main.py --mode run --underlying_name ""خودرو"" --underlying_ticker ""IRO1IKCO0001"" --option_name ""طخود0136"" --option_ticker ""IROFIKCO9N31"" --expiration_date ""1404-01-06"" --strike_price 3000.0 --call_put p --can_trade_in_same_direction"
