# Hermes trader
1. Resolve buy percentage issue in create_order
2. Inject mock hermes into a mock zeus class

# Athena
1. Alert if watchdog_loop attempt count goes too high
# Prometheus
1. Test cases for Predict() and any other classes used in non-training production

# Other
0. Make the scraper files use the zeus run() setup
1. Make the config use nice capitalized classes for each category
2. Do something else with credentials.json 
3. Improve discord logs - Use separate ones for scraper, order listener, predictor, etc
4. Test cases for scraper files?

# Docker
1. Should we containerize this shit? Apparently there's a cuda docker?
2. If so, we can create temporary postgres databases. This would let us enforce proper SQL schema files


Hermes followup

- After prediction time ends, compare prediction against reality via margin/accuracy
- Use to validate success rate over time
- Can do it retroactively/rarely, if it can compare against closest timestamp in big table
- 

    UPDATE 2/21

    Delphi is formatting CSV properly!
    ...but something is stopping the predictor from running
    when some other thread is aborted, Delphi quickly populates the predictions.
    Need to see what's holding it up. Maybe multiproccess it, since no other threads are touching that file?