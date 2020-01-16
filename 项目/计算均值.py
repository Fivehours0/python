import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 暂定需要修改参数：path  filename  MAXVALUE  dealList  dealStr

### 降低数据的采样频率 ###
### data: 输入的数据，数据格式为:index为业务处理时间，value为采集项值。如2019-11-30 23:56:35    382.85828
### freq: 新的采样时间间隔
### return: 返回新采样频率的数据，数据格式为DataFrame
def decreaseSampleFreq(data, freq):
    resampleDate = pd.to_datetime(data.index) # 将Index转换为DatetimeIndex格式
    newData = data.copy()
    newData.index = resampleDate
    newData = newData.resample(freq).mean() # 降采样，降低采样频率
    return newData

### 读取业务处理时间有效的数据并按照业务处理时间排序 ###
### df: 表格读入的数据
### return: storeSplitData:数据格式为字典，key为采集项名称，value为dataframe(index为业务处理时间, data为采集项值)           
def dealDataWithDealtime(df):
    split_sort = df.set_index(['采集项名称', '业务处理时间']).sort_index(level=['采集项名称', '业务处理时间'])
    split_sort['采集项值'].replace([999999999.0000001, np.nan], inplace=True)# 将异常值替换为nan

    storeSplitData = {} # 创建一个字典用以保存分割后的数据
    splitDataKeys = split_sort.index.levels[0] # 字典的key，即保存分割数据的名称

    for i in range(splitDataKeys.shape[0]): # 分割数据,保存至字典
        storeSplitData[splitDataKeys[i]] = split_sort.loc[split_sort.index.levels[0][i], '采集项值']
    return storeSplitData

# 文件夹路径
path = 'K:/1-14时滞计算/pkl/' 
# 文件名
filename = ['西昌2#高炉采集数据表_高炉本体(炉缸2).pkl', '西昌2#高炉采集数据表_高炉本体(炉缸3).pkl', '西昌2#高炉采集数据表_高炉本体(炉缸4).pkl']
MAXVALUE = 999999999.0 # 将该值替换为nan


# 读入表中的数据保存于该字典中，并将所有采集项按照字典形式保存。key为采集项名称，value为Series格式(index为业务处理时间，value为采集项值)
allData = {}
for i in range(len(filename)):
    df = pd.read_pickle(path+filename[i]) # 读取数据
    df.index = range(df.shape[0]) # 重设index
    storeSplitData = dealDataWithDealtime(df) # 将df格式转化为字典格式
    allData.update(storeSplitData) # 保存于allData中(update为字典合并)

# 需要处理的项存入dealList列表中。如果所有项都要处理，则将字典allData的key作为dealList即可
dealStr = "炉缸温度14 炉缸温度15 炉缸温度16 炉缸温度17	炉缸温度171	炉缸温度18 炉缸温度19	炉缸温度192 炉缸温度21 炉缸温度24 炉缸温度26 炉缸温度33	\
        炉缸温度34 炉缸温度4 炉缸温度41	炉缸温度42	炉缸温度43 炉缸温度47 炉缸温度50 炉缸温度53	炉缸温度54	炉缸温度6	炉缸温度7 炉缸温度9 炉底温度18 \
        炉底温度19 炉缸温度101 炉缸温度103 炉缸温度108	炉缸温度109	炉缸温度110 炉缸温度115	炉缸温度116	炉缸温度117 炉缸温度119	炉缸温度120	\
        炉缸温度122 炉缸温度152 炉缸温度154 炉缸温度56	炉缸温度57	炉缸温度58 炉缸温度61 炉缸温度64 炉缸温度66	炉缸温度67	炉缸温度68	\
        炉缸温度69	炉缸温度70	炉缸温度71 炉缸温度73 炉缸温度75 炉缸温度124	炉缸温度125 炉缸温度129	炉缸温度130 炉缸温度135	炉缸温度136\
        炉缸温度137	炉缸温度138 炉缸温度140	炉缸温度141	炉缸温度142 炉缸温度148	炉缸温度149	炉缸温度150 炉缸温度81 炉缸温度87 炉缸温度90\
        炉缸温度91	炉缸温度92 炉缸温度146	炉缸温度156	炉缸温度157 炉缸温度163	炉缸温度164	炉缸温度165 炉缸温度174	炉缸温度175	\
        炉缸温度176	炉缸温度177 炉缸温度186	炉缸温度187 炉缸温度189 炉缸温度193 炉缸温度195	炉缸温度196	炉缸温度197	炉缸温度198	\
        炉缸温度199	炉缸温度200	炉缸温度201"
dealList = dealStr.split()

for value in dealList:
    allData[value].name = value 
    allData[value] = allData[value].astype('float64') # allData[value]的type本来为obj（无法使用resample函数），将其转化为float64
    allData[value].replace([MAXVALUE, np.nan], inplace=True) # 将异常值替换为nan
    allData[value] = decreaseSampleFreq(allData[value], '5Min') # 重采样   

storeAfterDealData = allData[dealList[0]] # 为便于进行merge操作，先将第一项赋值给storeAfterDealData
for value in dealList[1:]:
    storeAfterDealData = pd.merge(storeAfterDealData, allData[value], how='outer', left_index=True, right_index=True)

result = storeAfterDealData.mean(axis=1) # 求平均
result.plot()
plt.show()
