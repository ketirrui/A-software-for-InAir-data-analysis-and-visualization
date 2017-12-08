# -*- coding: utf-8 -*- 
'''
Created on 2017. 10. 24.

@author: 재원
'''
# 1. The result of the analysis of collected indoor data for all users
# 1. 전체 사용자의 실내 공기 데이터 분석 
# 2017/9/6~ 현재까지 데이터 분석 결과 보여

from Air.inAirPreProcessing import *
from Air.correlation import *
from statsmodels.sandbox.regression.kernridgeregress_class import plt_closeall

def total_inAirGraph(specs, data_total, storage):
#1. 
    title = '1-1. InAir Data Bar Graph of All User by specs'
    tag='SERIAL'
    filename=os.path.abspath(os.path.join(storage, title+'.png'))
    groupData, groupMean, groupDescribe = groupbyTag(tag, specs, data_total)
    gtoupMeanT = groupMean.T
    plt = plotBarGraph(gtoupMeanT)
    plt.savefig(filename)
    
    #1-2
    title = '1-2. InAir Data dot Graph of All User by spec'
    filename=os.path.abspath(os.path.join(storage, title+'.png'))
    plt = plotGroup(specs, groupMean, groupMean.index)
    plt.savefig(filename+'.png')
    
    
    # 2. 
    title = '2. TimeSeries Data by Serial'
    tag= ['SERIAL', 'date']
    groupData, groupMean, groupDescribe = groupbyTag(tag, specs, data_total)
    groupMean = data_scale(groupMean)
    print(groupMean)
    
    f, a =plt.subplots(4,1, figsize= (15,25))
    f.subplots_adjust(hspace=0.3, wspace=1)
    f.tight_layout()
    for i, id_name in enumerate(groupMean.index.levels[0]): 
        groupMean.xs(id_name).plot(ax=a[i], title=id_name, style=mark)
    filename=os.path.abspath(os.path.join(storage, title+'.png'))
    plt.savefig(filename)
    
    
    # 3-6
    tags =['date', 'dayofweek', 'dayoff', 'timesection']
    number = 3
    for tag in tags:
        title = str(number) + '. Comparison of data flow according to '+tag
        filename=os.path.abspath(os.path.join(storage, title+'.png'))
        groupData, plt = plotSerialDatabySpec(tag, data_total, specs)
        plt.savefig(filename)
        groupData.mean()
        number = number+1
    
    #7.   
    title= '7. Correlation Matrix presented by SNS'
    filename=os.path.abspath(os.path.join(storage, title+'.png'))
    plt = snsPlot(data_total)
    plt.savefig(filename)
    
    #8. ??????
    """
    title ='8, Correlation Matrix of scaled In Air Data'
    
    feature_N = inAir.scaled_airData_idx.columns.size
    filename = storage +title +'.png'
    draw_Correlation(feature_N, inAir.airData_idx, filename)
    inAir.scaled_airData_idx.corr()
    """
####### Initialization ###########################################################    
inair = getFirstData('ALL')
data_total = inair.airData
specs = inair.specs
####### Get Data_total End ####################################################### 

start_time = data_total.index.min()
end_time = data_total.index.max()
dir_path = os.path.dirname(os.path.realpath(__file__)) 
storage = os.path.abspath(os.path.join(dir_path, 'inAirGraph','Total')) #"inAirGraph/Total/"
total_inAirGraph(specs, data_total, storage)
description = "Total Data number is "+ str(len(data_total)) +'[ from ' +start_time.strftime('%Y-%m-%d') +' to '+ end_time.strftime('%Y-%m-%d') +']'
print(description)
