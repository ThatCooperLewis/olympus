# **Big Stuff** 

## Multiple accounts/models
- We need a way to run multiple predictors & mock orders
- Then we can test different models at the same time
- Probably will involve different SQL tables, shell script to source the right env vars

## Google Sheets integration
- Add automated system for logging long-term _full_data

## Make services better
- Increase reboot frequency (twice daily)
  - Consider rebooting all servers regularly
  - NAS reboot? 5AM PST?
  - Maybe a new task schedule can reboot WSL & rerun the SSH/service scripts?
- git pull upon service startup
- What would it take to run automated PR testing? Via jenkins locally?

# **Small Stuff**

## Next steps
- Move GDrive to separate service (so we can stop it form crashing other things if there's a session timeout)
- Add different trade thresholds for USD and BTC 
- Make service for Delphi on NAS
  - Add postgres monitoring for prediction db
- Define SQL schemas for docker instance
- Find good postgres program for windows

## Backlog
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