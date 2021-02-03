import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# This file is so I can learn/remember how the input data is structured

def log(label, obj):
    print(label, '\n', type(obj))
    if type(obj) is np.ndarray:
        print(obj.shape)
    print("========")
    print(obj)
    print("========")
    print()

# test.csv (one column, 'nums' is header)
# dates do not matter
''' 
nums
0
1
2
3
4
null
5
6
7
8
9
10
'''


df = pd.read_csv('test.csv')
# log('original df', df)
# <class 'pandas.core.frame.DataFrame'>
# ========
#     nums
# 0    0.0
# 1    1.0
# 2    2.0
# 3    3.0
# 4    4.0
# 5    NaN
# 6    5.0
# 7    6.0
# 8    7.0
# 9    8.0
# 10   9.0
# 11  10.0
# ========


reshape = df.nums.values.reshape(-1, 1)
# log('reshaped df', reshape)
# <class 'numpy.ndarray'>
# (12, 1)
# ========
# [[ 0.]
#  [ 1.]
#  [ 2.]
#  [ 3.]
#  [ 4.]
#  [nan]
#  [ 5.]
#  [ 6.]
#  [ 7.]
#  [ 8.]
#  [ 9.]
#  [10.]]
# ========

nonnull = reshape[~np.isnan(reshape)]
# log('nonnull', nonnull)
# <class 'numpy.ndarray'>
# (11,)
# ========
# [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9. 10.]
# ========

reshape_scaled = nonnull.reshape(-1 ,1)
# log('reshaped scaled np', reshape_scaled)
# <class 'numpy.ndarray'>
# (11, 1)
# ========
# [[ 0.]
#  [ 1.]
#  [ 2.]
#  [ 3.]
#  [ 4.]
#  [ 5.]
#  [ 6.]
#  [ 7.]
#  [ 8.]
#  [ 9.]
#  [10.]]
# ========


def to_sequences(data, seq_len):
    d = []
    for index in range(len(data) - seq_len):
        d.append(data[index: index + seq_len])
    return np.array(d)

sequenced = to_sequences(reshape_scaled, 5)
# log('sequenced', sequenced)
# <class 'numpy.ndarray'>
# (6, 5, 1)
# ========
# [[[0.]
#   [1.]
#   [2.]
#   [3.]
#   [4.]]

#  [[1.]
#   [2.]
#   [3.]
#   [4.]
#   [5.]]

#  [[2.]
#   [3.]
#   [4.]
#   [5.]
#   [6.]]

#  [[3.]
#   [4.]
#   [5.]
#   [6.]
#   [7.]]

#  [[4.]
#   [5.]
#   [6.]
#   [7.]
#   [8.]]

#  [[5.]
#   [6.]
#   [7.]
#   [8.]
#   [9.]]]
# ========


# Shape here is 
#(6, 5, 1)
# 6 sequences in total, 
# 5 values per sequence, 
# 1 set of sequences (always 1)

num_to_train = int(.80* sequenced.shape[0])

xtrain = sequenced[:num_to_train, :-1, :]
# <class 'numpy.ndarray'>
# (4, 4, 1)
# ========
# [[[0.]
#   [1.]
#   [2.]
#   [3.]]

#  [[1.]
#   [2.]
#   [3.]
#   [4.]]

#  [[2.]
#   [3.]
#   [4.]
#   [5.]]

#  [[3.]
#   [4.]
#   [5.]
#   [6.]]]
# ========


ytrain = sequenced[:num_to_train, -1, :]
# <class 'numpy.ndarray'>
# (4, 1)
# ========
# [[4.]
#  [5.]
#  [6.]
#  [7.]]
# ========


xtest = sequenced[num_to_train:, :-1, :]
# <class 'numpy.ndarray'>
# (2, 4, 1)
# ========
# [[[4.]
#   [5.]
#   [6.]
#   [7.]]

#  [[5.]
#   [6.]
#   [7.]
#   [8.]]]
# ========


ytest = sequenced[num_to_train:, -1, :]
# <class 'numpy.ndarray'>
# (2, 1)
# ========
# [[8.]
#  [9.]]
# ========

# log('X Training', xtrain)
# log('Y Training', ytrain)
# log('X Test', xtest)
# log('Y Test', ytest)

xtrain = sequenced[:, :-1, :]
# log('xtrain no split', xtrain)
# (6, 4, 1)
# ========
# [[[0.]
#   [1.]
#   [2.]
#   [3.]]

#  [[1.]
#   [2.]
#   [3.]
#   [4.]]

#  [[2.]
#   [3.]
#   [4.]
#   [5.]]

#  [[3.]
#   [4.]
#   [5.]
#   [6.]]

#  [[4.]
#   [5.]
#   [6.]
#   [7.]]

#  [[5.]
#   [6.]
#   [7.]
#   [8.]]]
# ========


ytrain = sequenced[:, -1, :]
# log('ytrain no split', ytrain)
# (6, 1)
# ========
# [[4.]
#  [5.]
#  [6.]
#  [7.]
#  [8.]
#  [9.]]
# ========

# TODO: Figure out how to make a ndarray of a sequence of the last seq_len rows of data
# then use the last value as the prediction
# THen update array with that prediction
# BOOM you know the future