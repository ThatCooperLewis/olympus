# NEXT STEPS

Small cleanup, improvements & bugfixing

1. Resolve buy percentage issue in hermes create_order
5. Define SQL schemas for docker instance
4. Make postgres docker container for unit tests
6. Fix status update logs. Fix "tickers in last hour" query
 
Big next steps

1. Setup a system for comparing prediction vs actual price. This may involve adding new rows to order listener i.e. predicted price, current price
        May be helpful to just compare against closest timestamp in the ticker table
2. Create a new SQL table for *Mock* Crosstower orders - buy/sell amount, current price, balances of each account, etc
        Modify mock_crosstower to interact with this SQL table & report updates to discord
        This should probably run alongside the hermes listener... but need to figure out safest way to run a mock instance without hardcoding it into the primary hermes code
        Maybe a separate service manager? mock_services_manager.py?
3. Setup Delphi on NAS

Backlog

1. Delphi was behaving weirdly in Zeus, but the delays in prediction may be resolved once it's running on its own machine
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