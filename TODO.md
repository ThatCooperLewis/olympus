# Hermes trader
1. Resolve buy percentage issue in create_order
2. Inject mock hermes into a mock zeus class

# Athena
1. Alert if watchdog_loop attempt count goes too high
# Prometheus
1. Test cases for Predict() and any other classes used in non-training production

# Other
1. Make a config file that contains all random global vars
2. Do something else with credentials.json 
3. Improve discord logs - Use separate ones for scraper, order listener, predictor, etc


# Hermes listener Server Instance

- SQL table for incoming orders
- All info into separate keys
- can even include data blobs from previous objects (prediction history, etc)
- rasppi will watch db and change order_status key to different states (QUEUED, PROCESSING, COMPLETED)
- add timestamp column

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