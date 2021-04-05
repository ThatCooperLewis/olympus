# Data intake

2. Fix header detection for reduction method
3. Implement argparse with helper descriptions
4. Finish up and document/parse new split_csv func
# Training

2. Setup randomizer for training params
    halfway done, just need to refactor & iterate
3. Automate testing random params & finding best predictor, continually "re-centering" based on best model's params
5. Make sure the same predictions are made when loading a model from file

# Analysis

1. Coinbase Pro API scraping
2. Multithreaded handler
    a. Prediction thread
    b. Scraping thread, updating live feed
    c. trading thread (maybe, or just put it in A)
    d. re-training thread (maybe)