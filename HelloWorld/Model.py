#coding:utf-8
#Designed for the simple-version of MLStudio

import pandas as pd
from sklearn.feature_extraction import DictVectorizer as DV
import xgboost as xgb
from scipy.sparse import hstack, csr_matrix
from Transformer import CatTrans

import os.path
from sklearn.datasets import dump_svmlight_file

class model():
    def __init__(self):
        #Store the mapping of the DataType and the corresponding columns
        self.col_list = dict()
        self.xgb_param = dict()
        self.dict_label_to_num = dict()
        self.dict_num_to_label = dict()

    def ClassifyFeatures(self, param):
        for key, value in param['DataType'].iteritems():
            if value in self.col_list:
                self.col_list[value].append(key)
            else:
                self.col_list[value] = list()
                self.col_list[value].append(key)

    def NumTransformer(self, df_train, df_test):
        
        if '数值型' not in self.col_list:
            return csr_matrix((len(df_train), 0)), csr_matrix((len(df_test), 0))
        
        #Do nothing
        cols_to_retain = self.col_list['数值型']

        return csr_matrix(df_train[cols_to_retain].values), csr_matrix(df_test[cols_to_retain].values)
    
    def CategoryTransformer(self, df_train, df_test):

        if '离散型' not in self.col_list:
            return csr_matrix((len(df_train), 0)), csr_matrix((len(df_test), 0))
        
        cols_to_retain = self.col_list['离散型']
        #Filter some Category
        for col in cols_to_retain:
            df_train[col], df_test[col] = CatTrans(df_train[col].astype('string'), df_test[col].astype('string'), 100)

        #Do the One-hot-encoding
        dict_train = df_train[cols_to_retain].to_dict(orient='records')
        dict_test = df_test[cols_to_retain].to_dict(orient='records')
        vectorizer = DV( sparse = True )
        vec_train = vectorizer.fit_transform( dict_train )
        vec_test = vectorizer.transform( dict_test ) 
        
        #convert_train = pd.DataFrame(vec_train, columns=vectorizer.feature_names_)
        #convert_test = pd.DataFrame(vec_test, columns=vectorizer.feature_names_)

        return vec_train, vec_test

    def DateTransformer(self, df_train, df_test):

        #Do the simple transformer to get the year, month, day, hour, minite from the Dates
        convert_train = pd.DataFrame()
        convert_test = pd.DataFrame()

        if '时间型' not in self.col_list:
            return csr_matrix((len(df_train), 0)), csr_matrix((len(df_test), 0))

        for col in self.col_list['时间型']:
            new_s = pd.to_datetime(df_train[col])
            convert_train[col+'_year'] = new_s.map(lambda x: x.year)
            convert_train[col+'_month'] = new_s.map(lambda x: x.month)
            convert_train[col+'_day'] = new_s.map(lambda x: x.day)
            convert_train[col+'_hour'] = new_s.map(lambda x: x.hour)
            convert_train[col+'_minute'] = new_s.map(lambda x: x.minute)

            new_s = pd.to_datetime(df_test[col])
            convert_test[col+'_year'] = new_s.map(lambda x: x.year)
            convert_test[col+'_month'] = new_s.map(lambda x: x.month)
            convert_test[col+'_day'] = new_s.map(lambda x: x.day)
            convert_test[col+'_hour'] = new_s.map(lambda x: x.hour)
            convert_test[col+'_minute'] = new_s.map(lambda x: x.minute)
        
        return csr_matrix(convert_train.values),  csr_matrix(convert_test.values)

    def OtherTransformer(self, df_train, df_test):
        raise Exception("need to implement")

    def LabelTransformer(self, df_train, param):
        if (param['Problem'] == '回归'):
            return df_train[param['Label']].as_matrix()
        
        if (param['Problem'] == '分类'):
            label = df_train[param['Label']]
            label_set = label.unique()

            #construct the mapping
            for i, elm in enumerate(label_set):
                self.dict_label_to_num[elm] = i
                self.dict_num_to_label[i] = elm
        
            return label.map(lambda x: self.dict_label_to_num[x])

    def SetXgbParam(self, param):
        obj_dict = {'分类': "multi:softmax", \
                '回归': "reg:linear", \
                }
        num_class_dict = {'分类': len(self.dict_label_to_num), \
                '回归': 0, \
                        }
        metric_dict = {'分类': 'mlogloss', \
                '回归' : 'rmse'}

        if (param['Problem'] == '回归'):
            self.xgb_param = {'max_depth':7, 'eta':0.1, 'silent':1, 'nthread':28, \
                'objective':obj_dict[param['Problem']],\
                        'eval_metric': metric_dict[param['Problem']]}
        else:
            self.xgb_param = {'max_depth':7, 'eta':0.1, 'silent':1, 'nthread':28, \
                'objective':obj_dict[param['Problem']],
                'num_class': num_class_dict[param['Problem']], \
                        'eval_metric': metric_dict[param['Problem']]}
        return

    def _sparse_matrix_add(self, x, y):
        if (x.nnz == 0):
            return y
        else:
            if (y.nnz == 0):
                return x
            else:
                return hstack([x, y])

    def run(self, df_train, df_test, param):
        self.ClassifyFeatures(param)
        
        x_train = csr_matrix((len(df_train), 0))
        x_test = csr_matrix((len(df_test), 0))

        num_train, num_test = self.NumTransformer(df_train, df_test)
        x_train = self._sparse_matrix_add(x_train, num_train)
        x_test = self._sparse_matrix_add(x_test, num_test)
        print "num done"

        cat_train, cat_test = self.CategoryTransformer(df_train, df_test)
        x_train = self._sparse_matrix_add(x_train, cat_train)
        x_test = self._sparse_matrix_add(x_test, cat_test)
        print "cat done"

        date_train, date_test = self.DateTransformer(df_train, df_test)
        x_train = self._sparse_matrix_add(x_train, date_train)
        x_test = self._sparse_matrix_add(x_test, date_test)
        print "date done"

        label = self.LabelTransformer(df_train, param)

        #Dump train, test to train.libsvm, test.libsvm
        train_libsvm = open(os.path.dirname(__file__) + '/../static/train.libsvm', 'w+b')
        test_libsvm = open(os.path.dirname(__file__) + '/../static/test.libsvm', 'w+b')
        dump_svmlight_file(x_train, label, f=train_libsvm)
        dump_svmlight_file(x_test, y = [0 for i in range(x_test.shape[0])], f=test_libsvm)
        train_libsvm.close()
        test_libsvm.close()

        #Load file
        dtrain = xgb.DMatrix(x_train, label=label)
        dtest = xgb.DMatrix(x_test)

        #Set Param
        self.SetXgbParam(param)
        num_round = 50
        evallist = [(dtrain, 'train')]

        #train model
        bst = xgb.train(self.xgb_param, dtrain, num_round, evals=evallist)

        #make prediction
        preds = bst.predict(dtest, output_margin=False)
        
        if (param['Problem'] == '分类'):
            preds = [self.dict_num_to_label[x] for x in preds]

        return preds
