# Hermes trader
1. Resolve buy percentage issue in create_order
2. Inject mock hermes into a mock zeus class

# Athena
1. Alert if watchdog_loop attempt count goes too high
# Prometheus
1. Test cases for Predict() and any other classes used in non-training production

# Other
1. Make the config use nice capitalized classes for each category
2. Do something else with credentials.json 
4. Test cases for scraper/listener files?

# Docker
1. Should we containerize this shit? Apparently there's a cuda docker?
2. If so, we can create temporary postgres databases. This would let us enforce proper SQL schema files
    - Maybe separate docker .run files for testing, pi scrapers, cuda container
# Mock
1. Introduce Logger to mock classes, replace print statements

Hermes followup

- After prediction time ends, compare prediction against reality via margin/accuracy
- Use to validate success rate over time
- Can do it retroactively/rarely, if it can compare against closest timestamp in big table
- 

    UPDATE 2/21

    Delphi is formatting CSV properly!
    ...but something is stopping/slowing the predictor from running
    when some other thread is aborted, Delphi quickly populates the predictions.
    Need to see what's holding it up. Maybe multiproccess it, since no other threads are touching that file?




1. RaspPi 4 8GB - Postgres Server
2. RaspPi 4 2GB - Hermes Order Maker
3. OrangePi - DB Monitor
4. RaspPi 3 - Athena Scraper 
5. Windows NAS as WSL - Prediction Engine

maybe have main branch be "autodeploying"? alias on servers have the service reboot after a git pull?


IP list
192.168.0.20    pi-postgres     Postgres Server     Raspi 4B    8GB
192.168.0.23    pi-monitor      DB Monitor          OrangePi    1GB
192.168.0.24    pi-hermes       Hermes              Raspi 4B    2GB
192.168.0.21    pi-athena       Athena Scraper      Raspi 3B    1GB