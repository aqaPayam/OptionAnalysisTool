@echo off

:: Run for ahrom
start cmd /k "title Running ahrom && set APP_MODE=ahrom && python main.py"

:: Run for khodro
start cmd /k "title Running khodro && set APP_MODE=khodro && python main.py"

:: Run for shasta
start cmd /k "title Running shasta && set APP_MODE=shasta && python main.py"
