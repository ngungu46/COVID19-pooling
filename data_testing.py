# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 22:34:45 2021

@author: ASUS
"""


import pickle 
import pickle as pkl
import pandas as pd

fin = 'D:\MATH 89S coding\COVID19-pooling\data\groupsizes_0.95.pkl'

data_dict = pickle.load(open(fin, 'rb'), encoding='latin1')

word_list = list(data_dict.keys())

print(word_list)

embedding_list = [data_dict[word] for word in word_list]

# print(embedding_list)


embedding_list2 = data_dict['e_false_positive_rate']

print(embedding_list2)

with open("data/groupsizes_0.95.pkl", "rb") as l:
    f = pkl.load(l)
    
e_num_tests = f['e_num_tests '].flatten()
e_time = f['e_time'].flatten()
e_false_positive_rate = f['e_false_positive_rate'].flatten()
e_num_confirmed_sick_individuals = f['e_num_confirmed_sick_individuals'].flatten()
e_ratio_of_sick_found = f['e_ratio_of_sick_found'].flatten()
sd_num_tests = f['sd_num_tests'].flatten()
sd_time = f['sd_time'].flatten()
sd_false_positive_rate = f['sd_false_positive_rate'].flatten()
sd_ratio_of_sick_found = f['sd_ratio_of_sick_found'].flatten()

data = {
        'e_num_tests ': e_num_tests,
        'e_time': e_time,
        'e_false_positive_rate': e_false_positive_rate,
        'e_num_confirmed_sick_individuals': e_num_confirmed_sick_individuals,
        'e_ratio_of_sick_found': e_ratio_of_sick_found,
        'sd_num_tests': sd_num_tests,
        'sd_time': sd_time,
        'sd_false_positive_rate': sd_false_positive_rate,
        'sd_ratio_of_sick_found': sd_ratio_of_sick_found
    }

path = 'data/groupsizes_0.95_extracted.pkl'
with open(path, 'wb+') as fp:
    pickle.dump(data, fp)
print('saved data as {}'.format(path))


with open("data/groupsizes_0.95_extracted.pkl", "rb") as f:
    object = pkl.load(f)
    
df = pd.DataFrame(object, index = [0])
df.to_csv(r'data/groupsizes_0.95_stats.csv')

