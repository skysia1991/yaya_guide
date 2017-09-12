#coding: utf-8

import pandas as pd

def CatTrans(train, test, n):
    freq = train.value_counts().iloc[:n].index
    new_train = train.map(lambda x: x if (x in freq) else 'unknown')
    new_test = test.map(lambda x: x if (x in freq) else 'unknown')
    return new_train, new_test

if __name__ == '__main__':
    d = pd.read_csv('data/train_file', encoding='u8')
    x, y = CatTrans(d['DayOfWeek'], d['DayOfWeek'], 100)
    print x.value_counts()
    print y.value_counts()
