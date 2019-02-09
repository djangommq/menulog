import os
import csv
from mongodb_utils import *
from menulog import VERSION,rawPath

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

if __name__ == '__main__':
    # 获取mongo链接
    mdb=get_db()
    # 创建表名
    tablename = VERSION + 'menulog'
    # 获取数据
    data_list=mdb.all_items(tablename)
    print('数据已拿出')
    filename=rawPath+'menulog.csv'
    with open(filename,'w',encoding='utf-8',newline='')as f:
          writer=csv.DictWriter(f,fieldnames=rawHead)
          if not os.path.getsize(filename):
              writer.writeheader()
          for data in data_list:
              writer.writerow(data)
