'''
Suppresses logs from tensorflow.
Import this before TF
'''
import os
# Hide tensorflow info logs (but keep warnings/errors)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'