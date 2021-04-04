# Data intake

2. Fix header detection for reduction method
3. Implement argparse with helper descriptions

# Training

1. Setup directory of auto-populated model, results, and training params
2. Setup randomizer for training params
3. Automate testing random params & finding best predictor, continually "re-centering" based on best model's params
4. Create separate training class

# Analysis

1. Coinbase Pro API scraping
2. Multithreaded handler
    a. Prediction thread
    b. Scraping thread, updating live feed
    c. trading thread (maybe, or just put it in A)
    d. re-training thread (maybe)