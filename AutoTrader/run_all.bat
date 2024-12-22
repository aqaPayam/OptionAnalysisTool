@echo off

:: Run for ahrom
start cmd /k "python main.py --mode ahrom"

:: Run for khodro
start cmd /k "python main.py --mode khodro"

:: Run for shasta
start cmd /k "python main.py --mode shasta"
