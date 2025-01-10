@echo off

:: Run for ahrom
start cmd /k "python main.py --mode a"

:: Run for khodro
start cmd /k "python main.py --mode b"

:: Run for shasta
start cmd /k "python main.py --mode c"

start cmd /k "python main.py --mode d"
