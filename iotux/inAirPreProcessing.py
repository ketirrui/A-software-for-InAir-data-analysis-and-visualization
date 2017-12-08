# -*- coding: utf-8 -*- 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from ggplot import * 
import datetime as dt

import os


timesectionLabel = ['Night','Morning','Afternoon','Evening']
dayofweekLabel = ['Monday', 'Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
unit = ['(ug/m2)', '(ug/m2)', '(ppm)', '(ug/m2)', '(dB)', '(C)', '(%)']
mark = ['c--','m--','ro-', 'k<--','g:', 'bo-','y-' ]
ID_List = {'YR':'15070', 'BD1':'15071', 'JW1':'15072', 'BD2':'15073', 'JW2':'13015', 'ALL':''}

class airData:
    specs=['PM10','PM25','CO2','VOCs','Noise', 'TEMP', 'Humidity']
    
    #airData_idx_summary = pd.DataFrame()
    def __init__(self):
        self.airData = pd.DataFrame()
        self.airData_idx = pd.DataFrame()
        self.scaled_airData_idx = pd.DataFrame()
        self.airDataExceptString_idx = pd.DataFrame()
        self.start_time = dt.datetime(2010, 12, 31, 0, 0)

    def get_airData_Set(self):
        self.airData_idx = self.airDataIndexing(self.airData, self.specs)
        self.scaled_airData_idx = data_scale(self.airData_idx)
        self.airDataExceptString= self.airData.drop(['dayoff','dayofweek', 'timesection', 'date'], 1)

    def getCleanAirData(self, filenames, start_time, end_time ):   
        self.start_time = start_time
        self.end_time = end_time        
        frame = self.makeFrame(filenames)
        frame = self.sortDATETIME(frame)
        frame = frame.ix[self.start_time:self.end_time]
        #frame = frame.reset_index()
        airData = self.setDATETIMEInfo(frame)
        airData = self.recolumn(airData)
        airData = airData.dropna()
        airData[self.specs] = airData[self.specs].astype(float)
        self.airData = airData
        return airData
    
    def sortDATETIME(self, frame):
        frame = frame.set_index('DATETIME')
        frame.index = pd.to_datetime(frame.index, errors='coerce')
        frame = frame.dropna()
        frame = frame.sort_index()
        return frame
    
    def recolumn(self, data):
        data = data.rename(columns ={'VOCS':'VOCs', 'NOISE':'Noise','HUMI':'Humidity'})
        data = data.drop(['CO','HCHO'], 1)
        #data.SERIAL = data.SERIAL.map(id)
        data.SERIAL = data.SERIAL.replace(['V01G1615070','V01G1615071','V01G1615072','V01G1615073'],['YR','BD1','JW','BD2'])
        return data
    
    def setDATETIMEInfo(self, frame):
        frame = frame.assign(date = frame.index.date)
        #frame = frame.assign(time = frame.DATETIME.dt.time)
        #frame.assing['date'] = pd.to_datetime(frame.apply(lambda x: makedatetime(x['DATETIME']), axis=1), errors='coerce')
        frame = frame.assign(dayofweek = frame.index.weekday_name)
        frame = frame.assign(dayoff =  frame.apply(lambda x: self.setdayoff(x['dayofweek']), axis=1))
        #frame['timesection']= frame.apply(lambda x: settimesetction(x['time']), axis=1)
        timesection_value = pd.cut(frame.index.hour, [0,6,12,18,24], labels= timesectionLabel, right=False)
        frame = frame.assign(timesection = timesection_value)
        frame.timesection = frame.timesection.astype(str) #  No Categorical.. Why?
        return frame
    
    def makeFrame(self, filenames):
        frame= pd.DataFrame()
        for filename in filenames:
            temp = pd.read_csv(filename)
            temp.reset_index().dropna(axis=0)
            frame = frame.append(temp)
        frame = frame.drop(frame[frame.DATETIME =='DATETIME'].index) # delete duplicated column names
        frame = frame.reset_index().drop('index', axis=1)
        return frame
    
    def setdayoff(self, dayofweek):
        if dayofweek in ('Saturday', 'Sunday'):
            return 'dayoff'
        else:
            return 'dayon'
        
    def airDataIndexing(self, airData, specs):
        old_index_list = airData.columns.values.tolist
        index_list = list(set(old_index_list())-set(specs))
        print(airData[:3])
        #airData = airData.reset_index(index_list, 1)
        airData = airData.reset_index()
        airData = airData.set_index(index_list, 1)
        airData = airData.apply(pd.to_numeric, errors='coerce')
        return airData

def data_scale(data):
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler().fit(data.values)
    features = scaler . transform(data.values)
    scaled_features = pd.DataFrame(features, index = data.index, columns =data.columns)
    return scaled_features
           
######################### 1. SERIAL Group Mean
def groupbyTag(tag, specs, data):
    grouped = data.groupby(tag)[specs]
    groupMean = grouped.mean()
    groupDescribe = groupMean.describe()
    #describe['PM10']['count']
    #describe.columns
    return grouped, groupMean, groupDescribe

def sortSecIdx(label, groupMean, tag):
    secIdx = pd.Categorical(groupMean.index.levels[1].values, categories = label, ordered = True)
    groupMean.index.set_levels(secIdx, level=tag, inplace = True)
    cols = groupMean.index.names
    groupMean = groupMean.reset_index().sort_values(cols).set_index(cols)
    return groupMean

def set_file(filename, ID):
    ID_List = {'YR':'15070', 'BD1':'15071', 'JW1':'15072', 'BD2':'15073', 'JW2':'13015', 'ALL':'*'}
    File_key= os.path.join(filename, ID_List[ID]+".csv")
    print(File_key)
    filenames = glob.glob(File_key)
    print(filenames)
    return filenames
    
def draw_Correlation(feature_N, data, filename):
    import matplotlib.pyplot as plt
    feature_N = data.columns.size
    fig, axes = plt.subplots(feature_N, feature_N,  figsize=(22, 22) )
    plt.subplots_adjust(left=None, bottom= None, right = None, top = None, wspace = None, hspace =None)
    for i in range(feature_N):
        for j in range(feature_N):
            iName = data.columns[i]
            jName = data.columns[j]
            axes[i, j].scatter(data[iName], data[jName],color='k')
            axes[i,j].set_xlabel(iName, fontsize=10)
            axes[i,j].set_ylabel(jName, fontsize=10)
    #plt.show()
    plt.savefig(filename)


#Air Plot
def plotResampledData(resampled_period, Data):
    Data_resampled = Data.resample(resampled_period).mean()
    Data_resampled = data_scale(Data_resampled)
    Data_resampled = Data_resampled.reset_index()
    Data_lng = pd.melt(Data_resampled, id_vars=['DATETIME'])
    # 우선 Delete
    g = ggplot(aes(x='DATETIME', y='value', colour='variable'), data=Data_lng) +geom_line() +ggtitle('Resamped Air Quality Data by '+resampled_period) #+ stat_smooth(span=0.10)
    return g
    
    
def plotSerialDatabySpec(tag, airData, specs):   
    serialTag =['SERIAL']
    serialTag.append(tag)
    groupData, groupMean, groupDescribe = groupbyTag(serialTag, specs, airData)  
    if tag == 'timesection':
        label=timesectionLabel
        groupMean = sortSecIdx(label, groupMean, tag)
    if tag == 'dayofweek':
        label = dayofweekLabel
        groupMean = sortSecIdx(label, groupMean, tag)

    data = groupMean.unstack(level=0)
    f, a = plt.subplots(len(specs), 1,  figsize=(10, 35))
    #f.tight_layout()
    f.subplots_adjust(hspace=1, wspace=1)
    for i, sepcname in enumerate(specs):
        specdata = data[sepcname]
        specdata.plot(ax=a[i], title=sepcname, style= mark)
    #plt.show()
    return groupData, plt


def plotGroup(specs, groupMean, index):
    index_num = len(index)
    specs_num = len(specs)
    xs = range(index_num)
    fig, axes = plt.subplots(specs_num, figsize=(5,15))# sharex=True
    plt.setp(axes, xticks = xs, xticklabels = index)
    
    for i in range(0, specs_num):
        axes[i].plot(xs, groupMean[groupMean.columns[i]], 'bo')
        axes[i].set_title(groupMean.columns[i])
        axes[i].set_ylabel(unit[i], rotation=0 )
    return plt

def plotBarGraph(groupMean):
    ax = groupMean.plot(kind='bar', figsize=(15, 8), legend=True, fontsize=12)
    ax.set_xlabel("Specs", fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    return plt

def getFirstData(ID):
    
    ####### Get All Transformed InAir Data####################################  
    ID = 'ALL'
    today = dt.datetime.now().replace(microsecond=0)
    end_time= today
    start_time =dt.datetime(2017, 9, 6) 
    dir_path = os.path.dirname(os.path.realpath(__file__)) #file directory - C:\Users\ketiRRUI\workspace\IoTUX2\Air
    filenames = os.path.abspath(os.path.join(dir_path,'..','DATA','airData'))
    print(filenames)
    filenames = set_file(filenames, ID)
    inAir = airData()
    inAir.getCleanAirData(filenames, start_time, end_time)
    inAir.get_airData_Set()
    print("get Total In Air")
    return inAir
