"""
处理请求失败的餐厅
"""
import os
import csv
import time
import random
from menulog import fail_rest_header,getInfo,saveData,saveLog

def fail_rest(rest_name_list):
    fail_rest_path = os.path.join(os.path.dirname(__file__), 'fail_data/fail_rest_load.csv')
    with open(fail_rest_path, 'w', encoding='utf-8', newline='')as f:
      writer = csv.DictWriter(f, fieldnames=fail_rest_header)
      writer.writeheader()
      for rest in rest_name_list:
          writer.writerow(rest)


def suc_rest(city_name, area_name, rest_name):
    rest_info = {
      'city_name': city_name,
      'area_name': area_name,
      'rest_name': rest_name
    }
    fail_rest_path = os.path.join(os.path.dirname(__file__), 'fail_data/suc_rest_load.csv')
    with open(fail_rest_path, 'a', encoding='utf-8', newline='')as f:
      writer = csv.DictWriter(f, fieldnames=fail_rest_header)
      if not os.path.getsize(fail_rest_path):
        writer.writeheader()
      writer.writerow(rest_info)


if __name__ == '__main__':
    rest_name_list=[]
    fail_rest_path = os.path.join(os.path.dirname(__file__), 'fail_data/fail_rest.csv')
    with open(fail_rest_path, 'r', encoding='utf-8', newline='')as f:
        reader=csv.DictReader(f,fieldnames=fail_rest_header)
        for r in reader:
            if reader.line_num==1:
                continue
            else:
                 rest_name_list.append(dict(r))

    while len(rest_name_list)!=0:
        row=rest_name_list.pop(0)
        wait_time=random.randint(3,7)
        try:
            res = getInfo(row['rest_name'], row['area_name'], row['city_name'],'https://www.menulog.com.au' + row['rest_name'])
            saveData(res, row['area_name'])
        except:
            # try:
            #   print('%s请求错误,%s秒后再次请求' % (row['rest_name'], str(wait_time)))
            #   time.sleep(wait_time)
            #   res = getInfo(row['rest_name'], row['area_name'], row['city_name'],'https://www.menulog.com.au' + row['rest_name'])
            #   saveData(res, row['area_name'])
            # except:
            rest_name_list.append(row)
            saveLog('%s返回为空' % (row['rest_name']))
        print(len(rest_name_list))
        fail_rest(rest_name_list)
        time.sleep(wait_time)