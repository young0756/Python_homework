import requests
from bs4 import BeautifulSoup
import pandas as pd
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import glob
import os.path
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
#数据爬取
def get_datas(url):
    #获取网页代码
    response = requests.get(url)
    #用bs解析数据
    soup = BeautifulSoup(response.content, 'lxml')
    #找到所有tr
    tr_list = soup.find_all('tr')
    #定义三个列表
    dates, conditions, temp = [], [], []
    #数据清理
    for data in tr_list[1:]:
        data_sub = data.text.split()
        dates.append(data_sub[0])
        conditions.append(''.join(data_sub[1:3]))
        temp.append(''.join(data_sub[3:6]))
    #转换成dataframe类型
    data_list = pd.DataFrame()
    data_list['日期'] = dates
    data_list['昼夜天气状况'] = conditions
    data_list['昼夜温度'] = temp
    return data_list
#用函数获取二三四月的数据
data_2_month = get_datas("http://www.tianqihoubao.com/lishi/qingdao/month/202302.html")
data_3_month = get_datas('http://www.tianqihoubao.com/lishi/qingdao/month/202303.html')
data_4_month = get_datas('http://www.tianqihoubao.com/lishi/qingdao/month/202304.html')
#总数居
data = pd.concat([data_2_month, data_3_month, data_4_month]).reset_index(drop=True)
#print(data)
#数据保存
data.to_csv('qingdao.csv',encoding='gbk')
#数据处理
a=data['昼夜温度']
b=data['昼夜天气状况']
data['日间气温']=a.str.split('/',expand=True)[1]
data['夜间气温']=a.str.split('/',expand=True)[0]
''''
print(data.head(5))
将温度符号去掉并且转换成int类型
'''
data['日间气温']=data['日间气温'].map(lambda x:int(x.replace('℃','')))
data['夜间气温']=data['夜间气温'].map(lambda x:int(x.replace('℃','')))
#定义三个series
dates=data['日期']
days=data['日间气温']
nights=data['夜间气温']
#绘制折线图
fig1=plt.figure(figsize=(13,6),dpi=200)
plt.xlable='日期'
plt.ylable='温度'
plt.title='青岛市近三月昼夜气温折线图'
#绘制一条折线
plt.plot(dates,
         days,
         color='red',
         alpha=0.7
         )
#绘制另一条折线
plt.plot(dates,
         nights,
         color='blue',
         alpha=0.3
         )
#将折线中间填充颜色
plt.fill_between(dates,
                 days,
                 nights,
                 color='blue',
                 alpha=0.3
                 )
#改编x轴刻度
plt.xticks(dates[::10])
fig1.savefig('折线图.jpg')
#绘制词云
wc=WordCloud(
    font_path='msyh.ttc',
    width=250,
    height=200,
    background_color='white'
             )
#将serise转换成list
list1=b.str.split('/',expand=False).tolist()
list1=np.asarray(list1)
ans1=list1.flatten()
ans1=ans1.tolist()
#绘制图片
wc.generate(' '.join(ans1))
wc.repeat=True
wc.to_file('词云.jpg')
#绘制柱状图
c=data['日间气温']
d=data['夜间气温']
#将数据类型转换成字符串
list2=c.astype(str)
list2=np.asarray(list2)
ans2=list2.flatten()
ans2=ans2.tolist()
ans2=[int(i) for i in ans2]
list3=d.astype(str)
list3=np.asarray(list3)
ans3=list3.flatten()
ans3=ans3.tolist()
ans3=[int(i) for i in ans3]
fig2 = plt.figure(
    figsize=(13,6),
    dpi=200
)
ax = fig2.add_axes([0.1,0.3,0.8,0.6])
width=0.35
ticks=np.arange(len(dates[::10]))
#绘制
ax.bar(ticks,
       ans2[::10],
       width,
       color = "red",
       label='日间气温'
       )
ax.bar(ticks+width,
       ans3[::10],
       width,
       color = "blue",
       align="center",
       label='夜间气温'
       )
ax.set_ylabel('气温')
ax.set_title('青岛市昼夜温度柱状图')
ax.set_xticks(ticks+width/2)
ax.set_xticklabels(dates[::10])
ax.legend(loc='best')
fig2.savefig('柱状图.jpg')
'''
通过print了解数据
查看结果
print(dates[::10])
print(ans2[::10])
print(ans3[::10])
print(ans1)
'''
#饼图
#统计天气状况出现次数
zhuangkuang=data['昼夜天气状况'].value_counts()
''''
print(zhuangkuang)
选取出现次数大于三的数据
'''
zhuangkuang=zhuangkuang[zhuangkuang.values>3]
fig3=plt.figure(
    dpi=200
)
plt.axes(
    aspect='equal'
)
#绘制
plt.pie(
    x=zhuangkuang.values,
    labels=zhuangkuang.index,
    autopct="%.2f%%",
    radius=1
)
plt.title='昼夜天气状况表'
#保存图片
fig3.savefig('饼图.jpg')
''''
散点图用到plot
画出两张
散点图
'''
fig4=plt.figure(
    figsize=(13,6),
    dpi=200
)
plt.plot(
    dates[::10],
    days[::10],
    'r.'
)
fig4.savefig('日散点图.jpg')
#画出两个散点图
#日夜的散点图更好比较
fig5=plt.figure(
    figsize=(13,6),
    dpi=200
)
plt.plot(
    dates[::10],
    nights[::10],
    'bo'
)
fig5.savefig('夜散点图.jpg')
''''
接下来进行图片拼接
用到pillow库
图片拼接
'''
def convertjpg(jpgfile,width=600,height=400):
    img=Image.open(jpgfile)#打开图片
    try:
        new_img=img.resize((width,height))
        new_img.save(os.path.join(os.path.basename(jpgfile)))
    except Exception as e:
        print(e)
convertjpg('饼图.jpg')
convertjpg('柱状图.jpg')
convertjpg('折线图.jpg')
convertjpg('词云.jpg')
convertjpg('日散点图.jpg')
convertjpg('夜散点图.jpg')
# 打开四张图片
image1=Image.open('饼图.jpg')
image2=Image.open('柱状图.jpg')
image3=Image.open('折线图.jpg')
image4=Image.open('词云.jpg')
image5=Image.open('日散点图.jpg')
image6=Image.open('夜散点图.jpg')
# 获取每张图片的宽高
width, height = image4.size
# 创建一张新的2*2大图，图片大小为每张图片的2倍
new_image = Image.new('RGB', (width*3, height*2))
new_image.paste(image3, (0, 0))
new_image.paste(image2, (width, 0))
new_image.paste(image1, (0, height))
new_image.paste(image4, (width, height))
new_image.paste(image5, (width*2, 0))
new_image.paste(image6, (width*2, height))
# 保存新图
new_image.save('青岛天气分析总图.jpg')
plt.show()


