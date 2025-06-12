import pickle
import os

with open('2.txt', 'rb') as f:
    book = pickle.load(f)
    print(book)