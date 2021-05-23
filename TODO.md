# Up next
1. Test reliability of websocket scraper, and implement on RaspPi
2. Finishing touches on scraper controller

# Data intake
1. Lambda script for Crosstower fetching

# Analysis
1. Multithreaded handler
    a. Prediction thread
    b. Scraping thread, updating live feed
    c. trading thread (maybe, or just put it in A)
    d. re-training thread (maybe)

# Non-essential tasks
1. Finish wrapping crosstower API methods (account management, etc)
3. Implement argparse with helper descriptions in filter.py
2. Fix header detection for filter.py reduction method