# NEXT STEPS

Small cleanup, improvements & bugfixing

1. Resolve buy percentage issue in hermes create_order
2. Make service for Delphi on main PC
3. Turn of rainbow LEDs in computer
5. Define SQL schemas for docker instance
4. Make postgres docker container for unit tests
 
Next steps

1. Update status bot to compare current account value vs. initial balance (factoring in current BTC price)

# **Big picture** 

## Multiple accounts/models
We need a way to run multiple predictors & mock orders
Then we can test different models at the same time
Probably will involve different SQL tables, shell script to source the right env vars

## Google Sheets integration
Two things:
1. Regular polling of Crosstower balances/total value, BTC price, general status, maybe compare static value using deposit info?
2. Take rows of data & send to Sheets
        - Have a chart where the Source data column is constantly rotated, so the chart isn't growing infinitely
        - Have a long-term chart that uses daily account value, or maybe a special SQL query that segments it well


Backlog
1. Hermes __submit_order() is not handling buy/sell flips properly and I'm not sure why (UPDATE 4/17/2022: I think this is working now. Still not sure why.)
2. We should eventually make test cases for Prometheus and its Predict() method
3. Master branch autodeployment in service clusters
        Only redeploy if changes have been pushed
        Check git status in python code
        Probably will have to be a separate service entirely

IP list
192.168.0.20    pi-postgres     Postgres Server     Raspi 4B    8GB
192.168.0.23    pi-monitor      DB Monitor          OrangePi    1GB
192.168.0.24    pi-hermes       Hermes              Raspi 4B    2GB
192.168.0.21    pi-athena       Athena Scraper      Raspi 3B    1GB