import requests
from pyquery import PyQuery as pq
import pymongo
import re


city_info = {'重庆':['cq',{'整租':[1,100], '合租':[2,62]}],'成都':['cd',{'整租':[1,100], '合租':[2,100]}]}
res_list = []
a = 0
b=0
#链接mongodb数据库
client = pymongo.MongoClient(host='localhost')
db = client['zufang']
col = db['rent']

def on_result(result):
    if result:
        save_to_mongo(result)

def save_to_mongo(result):
        if col.insert_one(result):
            print('存储到mongoDB成功',result)
# 抓取成渝双城链家租房信息，所有url，并返回response
for city,city_info in city_info.items():
    for rent_type,n in city_info[1].items():
        for i in range(n[1]):
            a += 1
            type_url = 'https://{}.lianjia.com/zufang/pg{}/rt20060000000{}/#contentList'.format(city_info[0],i+1,n[0],)
           # print(a,type_url)
            response = requests.get(type_url).text
            dc1 = pq(response)
            for each in dc1('a.twoline').items():
                b +=1
                url_detail= 'https://cq.lianjia.com{}'.format(each.attr.href)
             #   print(b,url_detail)
                def get_html(url_detail):  #获取html
                    i = 0
                    while i < 3:
                        try:
                            rent_detail = requests.get(url_detail, timeout=10).text
                            return rent_detail
                        except requests.exceptions.RequestException:
                            i +=1



                # rent_detail = requests.get(url_detail, timeout=10).text
                dc2 = pq(get_html(url_detail))
            #print(dc2)
                # 抓取各字段
                print('正在抓取{}市{}第{}页数据'.format(city,rent_type,i+1))
                result = {
                    'rental':dc2('#aside > div > span').text(),
                    'distric':dc2('p.bread__nav__wrapper.oneline > a:nth-child(2)').text(),
                    'bc':dc2('p.bread__nav__wrapper.oneline > a:nth-child(3)').text(),
                    'community':dc2('.bread__nav--bottom > h1 > a').text(),
                    'size':dc2('#info > ul:nth-child(2) > li:nth-child(2)').text(),
                    'city':dc2('p.bread__nav__wrapper.oneline > a:nth-child(1)').text(),
                    'rent_type':dc2('#aside > ul > li:nth-child(1)').text(),
                    'house_type':dc2('#aside > ul:nth-child(3) > li:nth-child(2)').text(),
                    'longitude':re.findall(r"longitude: '(.*)',", url_detail),
                    'latitude':re.findall(r"latitude: '(.*)'", url_detail)
                }
                on_result(result)











