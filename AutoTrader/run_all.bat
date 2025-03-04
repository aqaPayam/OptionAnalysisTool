@echo off
chcp 65001
start cmd /k "python main.py --mode run --underlying_name ""خودرو"" --underlying_ticker ""IRO1IKCO0001"" --option_name ""ضخود2055"" --option_ticker ""IRO9IKCO8O21"" --expiration_date ""1404-02-03"" --strike_price 3000.0 --call_put c --can_trade_in_same_direction"
