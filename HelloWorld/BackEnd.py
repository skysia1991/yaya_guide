#coding:utf-8
#Designed for the Back-end
#The main purpose is to compute

import pandas as pd
from Model import model
from collections import defaultdict

class UserGuide_BE():
    def __init__(self):
        """
        The variables are listed below:
        df_train
        df_test
        param
        """
        self.df_train = pd.read_csv('static/train.csv', encoding='u8')
        self.df_test = pd.read_csv('static/test.csv', encoding='u8')
        self.param = dict()
        return

    def GetHeader(self):
        cols = list(self.df_train.columns)
        return cols
    
    def GetFeatureHeader(self, ID, Label):
        header = self.GetHeader()
        feature_header = [elm for elm in header if elm!=ID and elm!=Label]
        return feature_header
    
    def GetSamples(self, ID, Label):
        result = list()
        for col in self.GetHeader():
            if (col != ID) and (col != Label):
                #row = defaultdict(str())
                row = dict()
                row['header_line'] = str(col)
                sample = self.df_train[col].dropna()
                row['first_line'] = sample.iloc[0]
                row['second_line'] = sample.iloc[5]
                col_type = self.df_train[col].dtype
                if (col_type == 'int64') or (col_type == 'float64'):
                    row['default_value'] =  'Number'
                else:
                    row['default_value'] = 'String'
                row['if_change'] = True
                result.append(row)
        return result

    def GetDataPreviewSamples(self):
        cols = list(self.df_train.columns)
        samples = self.df_train[:10].to_dict()
        return cols, samples

    def AddParam(self, key, value):
        #if (key in self.param):
        #    raise Exception("Are you really want to change this setting?")
        #else:
        self.param[key] = value

    def GetParam(self, key):
        if (key in self.param):
            return self.param[key]
        else:
            raise Exception("You need to assign the value first!")

    def CheckFile(self):
        """
        This function is to check the validness of train_file and test_file. If the files have the correct format, the function will return True,else return False
        """
        raise Exception('need to be implemented')
    
    def TriggerModel(self):
        MlModel = model()
        Predicts = MlModel.run(self.df_train, self.df_test, self.param)
        if self.param['Problem'] == '分类':
            self.PredictResults = [str(x) for x in Predicts]
        if self.param['Problem'] == '回归':
            self.PredictResults = [float(x) for x in Predicts]
        return

    def GetPredictResults(self):
        return self.PredictResults

    def WritePredictResults(self):
        output = pd.DataFrame(self.PredictResults, columns=[self.param['Label']])
        if (self.param['ID'] == 'None'):
            output['Id'] = [str(x) for x in range(len(output))]
        else:
            output['Id'] = self.df_test[self.param['ID']]
        output[['Id', self.param['Label']]].to_csv('static/predict_file', index=False, encoding='u8')
