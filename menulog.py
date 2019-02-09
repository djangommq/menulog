# -*- coding: utf-8 -*-
import csv
import datetime
import os
import time
import requests
import sys
import json
import traceback
from bs4 import BeautifulSoup
import importlib
from mongodb_utils import *

import random

importlib.reload(sys)

# 数据爬取的时间
VERSION = '20181210'

# 获取数据库链接对象
client_mongo=get_db()

date = datetime.datetime.now().strftime("%Y-%m-%d")
file_path = os.path.dirname(os.path.split(os.path.realpath(__file__))[0]) + '/crawlerOutput/' + date + '/'
web_name = 'menulog/'
rawPath = file_path + web_name
logFile = file_path + 'log/' + web_name + 'log.csv'
rawIds = []
rawHead = [
    "shopId",
    "shopLogoImageUrl",
    "shopName",
    "addressName",
    "blockCode",
    "evaluationPoint",
    "commentCount",
    "shopStatus",
    "isOpen",
    "shopSts",
    "waitTime",
    "minOrderCondition",
    "charge",
    "minOrderPrice",
    "minOrderPriceParam",
    "categoryListCount",
    "dispPayCardFlg",
    "dispPayAmazonFlg",
    "dispLinePayFlg",
    "dispMadonnaPayFlg",
    "amenity",
    "chainNm",
    "chainId",
    "chainCd",
    "shopPrefAddress",
    "dispBusTime",
    "dispHoliday",
    "shopInformation",
    "phoneNo",
    "shopAddress",
    "attention",
]

location_headers=[
        'city_name',
        'location'
    ]

fail_rest_header=[
    'city_name',
    'area_name',
    'rest_name'
]

def getData(url, data):
    domain = 'https://www.menulog.com.au'
    url = '%s%s' % (domain, url)
    header = {
        'Host': 'www.menulog.com.au',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh,zh-CN;q=0.9',
        # 'Cookie': 'visid_incap_1145229=fsc+U0tnTtaTAZhKtUzUx0MckVoAAAAAQUIPAAAAAAD/iVTu3cb+3WYA1x2yKrx9; _okbk=vi3%3Dinactive%2C; PHPSESSID=9eutaf3vcm38mltdlq1u6cv8t2; nlbi_1145229=u8gLVoqYPWD14RNpnknvswAAAABQL+OmTGtWUmVt6bvjupJy; optimizelyEndUserId=oeu1519460311982r0.44511373714786573; _ga=GA1.3.597880966.1519460313; _gid=GA1.3.633770370.1519460313; je-srv-cw=production; nlbi_1145229_1387431=ZUtwHzdt9iWX7dtWnknvswAAAAB1Khfp8sUIORg9nnlYKUQ5; je-feature_bucket=89992b2794124bfd9ab7b98c51ae249e; __RequestVerificationToken=JrRpzbxf412KJhQekNoMBXXLaWkauU19VR0FfvDhTg5mkFDXD_NXe1vUUIlp9D7fD6bJ_UPVGjssM6nm3tig-wiCbvQ1; incap_ses_883_1145229=Pv8mE+pauwmcVECUBQxBDC5AkVoAAAAASLVOGl1uSo1a7ofb9z9irw==; _sp_ses.13d8=*; _dc_gtm_UA-698294-38=1; _gat_UA-698294-38=1; _gali=homepage-search-fullAddress; _sp_id.13d8=dbb11148-3543-48e1-bef5-41399dcd9d54.1519460313.2.1519468655.1519460500.ac8ba611-631b-4d9b-931d-02e8cadaa8b1; je-last_latitude_used=-34.9284989; je-last_longitude_used=138.6007456; je-last_street_used=; je-last_houseNo_used=; je-location=5000; je-last_city_used=é¿å¾·è±å¾·; je-last_sublocality_used=; je-last_state_used=SA',
    }
    proxies = {
        "http": "http://127.0.0.1:1080",
        "https": "http://127.0.0.1:1080",
    }
    # with requests.get(url, headers=header) as res:
    #     try:
    #         return res.json(),res.status_code
    #     except:
    #         return res.content,res.status_code
    try:
        response= requests.request("GET", url, headers=header,timeout=3)
        return response.text,response.status_code
        # request = Request(url,headers =header )
        # response=urlopen(request)
        # return response.read(),response.getcode()
    except TimeoutError as e:
        print(url+'请求超时')
        saveLog(url+'请求超时')
        return '','error'
    except Exception as e:
        saveLog(url+'发生其它错误:'+str(e.args))
        return '', 'error'


def getList(locationTerm):
    url = '/area/%s/' % (locationTerm)
    data = {}
    res,status_code = getData(url, data)
    if status_code != 200:
        saveLog('https://www.menulog.com.au'+url+'请求错误,'+'返回码为:'+str(status_code))
    soup = BeautifulSoup(res)
    lists = soup.find_all('a', class_='mediaElement')

    url = {}
    for info in lists:
        url[info['data-test-restaurant-id']] = info['href']
    return url


def getInfo(shopName,area_name,city_name,url):
    saveLog('爬%s的数据' % (shopName))
    data = {}
    res,status_code = getData(shopName, data)
    soup = BeautifulSoup(res)
    try:
        offer = soup.find('p', class_='offer').string
    except:
        offer = ''

    try:
        raw_data = {
            'title': soup.find('h1', class_='infoTextBlock-item-title').string,
            'text': soup.find('p', class_='infoTextBlock-item-text').string,
            'ratingValue': soup.find('meta', attrs={'itemprop': 'ratingValue'})['content'],
            'itemreviewed': soup.find('meta', attrs={'itemprop': 'itemreviewed'})['content'],
            'ratingCount': soup.find('meta', attrs={'itemprop': 'ratingCount'})['content'],
            'bestRating': soup.find('meta', attrs={'itemprop': 'bestRating'})['content'],
            'worstRating': soup.find('meta', attrs={'itemprop': 'worstRating'})['content'],
            'phone': soup.find('input', id='Phone')['value'],
            'offer': offer,
            'address': soup.find('div', id='google-map')['data-location'],
            'city_name': city_name,
            'area_name':area_name,
            'rest_url':url
        }
    except:
        return False
    return raw_data


def getLocation():
    '''
    重新生成地点列表
    :return:
    '''
    uri = '/takeaway/ajax_suggest_suburb.php'
    for i in range(10):
        data = {
            'cartType': 'delivery',
            'term': i,
        }
        res = getData(uri, data, True)
        res = res[0][1]
        for i in res:
            i = i.replace('<span>', '')
            i = i.replace('</span>', '')
            i = i.replace(' ', '')
            with open('location.txt', 'a') as file:
                file.write('%s\n' % (i))


def saveData(data, areaName):
    rawHead = [
        'title',
        'text',
        'ratingValue',
        'itemreviewed',
        'ratingCount',
        'bestRating',
        'worstRating',
        'phone',
        'offer',
        'address',
        'city_name',
        'area_name',
        'rest_url'
    ]
    for k, v in data.items():
        data[k] = str(v).replace('\n', ' ').replace('\r', ' ')
    isExists = os.path.exists(rawPath)
    if not isExists:
        os.makedirs(rawPath)
    # rawFile = '%s%s.csv' % (rawPath, areaName)
    # with open(rawFile, 'a',encoding='utf-8',newline='') as raw_file:
    #     raw_csv = csv.DictWriter(raw_file, fieldnames=rawHead)
    #     if (not os.path.getsize(rawFile)):
    #         raw_csv.writeheader()
    #     raw_csv.writerow(data)

    # 将数据保存到数据库
    tablename=VERSION+'menulog'
    client_mongo.insert_one(tablename,data,condition=['rest_url'])
    # print(data)


def saveLog(str=''):
    date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logHead = [
        'ruandate',
        'str'
    ]
    logData = {
        'ruandate': date_time,
        'str': str
    }
    print('%s \t %s' % (date_time, str))
    logPath = os.path.split(logFile)
    isExists = os.path.exists(logPath[0])
    if not isExists:
        os.makedirs(logPath[0])
    with open(logFile, 'a',encoding='utf-8',newline='') as log_file:
        log_csv = csv.DictWriter(log_file, fieldnames=logHead)
        if (not os.path.getsize(logFile)):
            log_csv.writeheader()
        log_csv.writerow(logData)

# 错误数据
def fail_rest(city_name,area_name,rest_name):
    rest_info={
        'city_name':city_name,
        'area_name':area_name,
        'rest_name':rest_name
    }
    fail_rest_path=os.path.join(os.path.dirname(__file__),'fail_data/fail_rest.csv')
    with open(fail_rest_path ,'a',encoding='utf-8',newline='')as f:
            writer = csv.DictWriter(f,fieldnames=fail_rest_header)
            if not os.path.getsize(fail_rest_path):
                writer.writeheader()
            writer.writerow(rest_info)


def fail_location(str):
    fail_location_path = os.path.join(os.path.dirname(__file__), 'fail_data/fail_location.txt')
    with open(fail_location_path , 'a', encoding='utf-8')as f:
            f.write(str)
            f.write('\n')


if __name__ == '__main__':
    # 获取已爬取的location列表
    has_location_path = os.path.join(os.path.dirname(__file__), 'input/')
    has_location=has_location_path+'has_location.txt'
    with open(has_location,'r',encoding='utf-8')as f:
        has_location_list=f.readlines()

    with open(os.path.split(os.path.realpath(__file__))[0] + '/input/location.csv', 'r',encoding='utf-8',newline='') as location:
        reader=csv.DictReader(location,fieldnames=location_headers)
        for i in reader:
            if reader.line_num==1:
                continue
            area_name = i['location'].strip()
            if area_name+'\n' not in has_location_list:
                    city_name=i['city_name']
                    saveLog('爬%s的数据' % (area_name))
                    lists = getList(area_name)
                    if len(lists)==0:
                            print('爬%s的数据出现问题,10秒后重新请求' % (area_name))
                            time.sleep(10)
                            lists = getList(area_name)
                            if len(lists)==0:
                                    fail_location(area_name)
                    saveLog('%s一共%s家餐馆' % (area_name,len(lists)))
                    allCnt = 0
                    oldCnt = 0
                    for x in lists:
                        wait_time=random.randint(3,7)
                        allCnt += 1
                        if x in rawIds:
                            rawIds.append(x)
                            oldCnt += 1
                        else:
                            try:
                                res = getInfo(lists[x],area_name,city_name,'https://www.menulog.com.au'+lists[x])
                                saveData(res, area_name)
                            except:
                                try:
                                    print('%s请求错误,%s秒后再次请求'%(lists[x],str(wait_time)))
                                    time.sleep(wait_time)
                                    res = getInfo(lists[x], area_name, city_name,'https://www.menulog.com.au'+lists[x])
                                    saveData(res, area_name)
                                except:
                                    fail_rest(city_name,area_name,lists[x])
                                    saveLog('%s返回为空'%(lists[x]))
                        time.sleep(wait_time)
                    saveLog('旧数据占比%s/%s' % (oldCnt, allCnt))
                    if len(lists)!=0:
                        with open(has_location, 'a', encoding='utf-8')as f:
                                f.write(area_name+'\n')
                    # time.sleep(5)
