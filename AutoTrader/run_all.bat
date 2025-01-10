@echo off

:: Run for ahrom
start cmd /k "python main.py --mode zahrom1110"

:: Run for khodro
start cmd /k "python main.py --mode zahrom1111"

:: Run for shasta
start cmd /k "python main.py --mode tahrom1111"

start cmd /k "python main.py --mode tahrom1112"
