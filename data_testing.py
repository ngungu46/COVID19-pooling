# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 22:34:45 2021

@author: ASUS
"""


import pickle 

fin = 'D:\MATH 89S coding\COVID19-pooling\data\groupsizes.pkl'

data_dict = pickle.load(open(fin, 'rb'), encoding='latin1')

word_list = list(data_dict.keys())

print(word_list)

embedding_list = [data_dict[word] for word in word_list]

# print(embedding_list)


embedding_list2 = data_dict['e_num_tests ']

print(embedding_list2)