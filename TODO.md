# Up next
1. Test reliability of websocket scraper, and implement on RaspPi
2. Finishing touches on scraper controller

# Data intake
1. Lambda script for Crosstower fetching? EC2?

# Olympus watchdog
1. Multithreaded handler
    a. Prediction thread
    b. Scraping thread, updating live feed
    c. trading thread (maybe, or just put it in A)

# Delphi predictor
1. write get_current_data function
2. test with model, add print statements along the way

# Hermes trader
1. Make it

# Non-essential tasks
1. Finish wrapping crosstower API methods (account management, etc)
3. Implement argparse with helper descriptions in filter.py and/or separate into distinct files
2. Fix header detection for filter.py reduction method