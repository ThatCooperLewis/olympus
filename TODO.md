# **Big Stuff** 

## Multiple accounts/models
- We need a way to run multiple predictors & mock orders
- Then we can test different models at the same time
- Probably will involve different SQL tables, shell script to source the right env vars

## Google Sheets integration
- Add automated system for logging long-term _full_data


# **Small Stuff**

## Next steps
- Make the CI/CD a task on NAS scheduler
- MockAPI/insertOrder probably doesn't work anymore, since tests were updated. Now hermes uses the "insertOrder" directly in the method, which I don't think will work well if mocking
- Move GDrive to separate service (so we can stop it form crashing other things if there's a session timeout)
- Add different trade thresholds for USD and BTC 
- Define SQL schemas for docker instance

## Backlog
- Global services manager that imports the cuda services only if predict arg is given
  - It can listen for messages for spinning up new instaces/rebooting
  - Get them from discord?
- CSV modes are deprecated. Tests wont work with them anymore. Remove all trace
- We should eventually make test cases for Prometheus and its Predict() method
- Master branch autodeployment in service clusters
  - Only redeploy if changes have been pushed
  - Check git status in python code
  - Probably will have to be a separate service entirely
- Make postgres docker container for unit tests
- Services assume server user is `cooper`. Change that? Add disclaimer? IDK.

# Local IP list
Move this to private file when you change to permanent network, dumbass

        192.168.0.20    pi-postgres     Postgres Server     Raspi 4B    8GB
        192.168.0.23    pi-monitor      DB Monitor          OrangePi    1GB
        192.168.0.24    pi-hermes       Hermes              Raspi 4B    2GB
        192.168.0.21    pi-athena       Athena Scraper      Raspi 3B    1GB
