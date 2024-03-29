from os.path  import basename
import sys
import csv
import pandas as pd
import sklearn
import matplotlib
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import lightgbm as lgb
	
def Create_dirdict(dataframe):
    dict_={}
    for i in range(0,len(dataframe)):
        value = dataframe["Director"][i]
        if value not in dict_ :
            dict_[value]=len(dict_.keys())+1
    return dict_
        
def Create_actdict(dataframe):
    dict_={}
    for i in range(0,len(dataframe)):
        value = dataframe["Actor1"][i]
        if value not in dict_ :
            dict_[value]=len(dict_.keys())+1
    for i in range(0,len(dataframe)):
        value = dataframe["Actor2"][i]
        if value not in dict_ :
            dict_[value]=len(dict_.keys())+1
    return dict_
    
def Create_coundict(dataframe):
    dict_={}
    for i in range(0,len(dataframe)):
        value = dataframe["Country"][i]
        if value not in dict_ :
            dict_[value]=len(dict_.keys())+1
    return dict_

def Process_y(y) :
    return y.map({0:0, 0.5:1, 1:2, 1.5:3, 2:4, 2.5:5, 3:6, 3.5:7, 4:8, 4.5:9, 5:10})


def Process_data(dataframe,remove_ownrate,act_dict,dir_dict,coun_dict):
    if remove_ownrate :
         dataframe = dataframe.drop(['Title',"Own_Rate"],axis=1)
    else :
        dataframe = dataframe.drop(['Title'],axis=1)
        
    dataframe['Genre1'] = dataframe['Genre1'].map({'Action':1,'Adventure':2,'Animation':3,'Comedy':4,'Crime':5,'Documentary':6,'Drama':7,'Family':8,'Fantasy':9,'History':10,'Horror':11,'Music':12,'Mystery':13,'Romance':14,'Science Fiction':15,'Thriller':16,'TV Movie':17,'War':18,'Western':19}).fillna(0)
    dataframe['Genre2'] = dataframe['Genre2'].map({'Action':1,'Adventure':2,'Animation':3,'Comedy':4,'Crime':5,'Documentary':6,'Drama':7,'Family':8,'Fantasy':9,'History':10,'Horror':11,'Music':12,'Mystery':13,'Romance':14,'Science Fiction':15,'Thriller':16,'TV Movie':17,'War':18,'Western':19}).fillna(0).astype('int')
    dataframe['Director'] = dataframe['Director'].map(dir_dict).fillna(0)
    dataframe['Actor1'] = dataframe['Actor1'].map(act_dict).fillna(0)
    dataframe['Actor2'] = dataframe['Actor2'].map(act_dict).fillna(0)
    dataframe['Country'] = dataframe['Country'].map(coun_dict).fillna(0)
    return dataframe

def Precision_test(pred,value):

    compt = 0
    for i in range(0,len(value)):
        if abs(pred[i]-value[i])<=1 :
            compt+=1
    half_star_p = round(compt/len(value)*100,2)
    
    compt = 0
    for i in range(0,len(value)):
        if abs(pred[i]-value[i])<=0.5 :
            compt+=1
    perfect_p = round(compt/len(value)*100,2)
    return [half_star_p, perfect_p]



  
def Train(x,y):
    model= lgb.LGBMClassifier(verbosity=-1)
    model.fit(x,y)
    rf = RandomForestClassifier(n_estimators = 100, max_depth=None, random_state = 1)
    rf.fit(x, y)
    return (rf,model)


def check_movie(data,rf,model,act_dict,dir_dict,coun_dict):
    df = pd.DataFrame([data], columns=["Title","Average_Rating","Director","Number_reviews","Release_Date","Actor1","Actor2","Genre1","Genre2","Country"])
    df = Process_data(df,False,act_dict,dir_dict,coun_dict)
    rf_pred=rf.predict(df)
    mod_pred= model.predict(df)

    return [data.iloc[0],data.iloc[4], (rf_pred[0]+mod_pred[0])/4]




