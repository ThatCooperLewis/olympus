# Hermes trader
1. Resolve buy percentage issue in create_order
2. Inject mock hermes into a mock zeus class

# Prometheus
1. Test cases for Predict() and any other classes used in non-training production
# Postgres
3. Look into making a secondary SQL table formatted to the correct timestamp interval. Do interval check every addition? Cronjob?


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