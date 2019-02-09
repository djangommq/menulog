import os
import csv
import time
import datetime
import requests
from lxml import etree

class GetLocation():
      def __init__(self):
          self.file_path=os.path.join(os.path.dirname(__file__),'input/')
          self.location_headers=[
                'city_name',
                'location'
          ]


      # 获取响应信息
      def get_response(self,url):
          headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
          }
          response = requests.request("GET", url, headers=headers, timeout=5)
          response.encoding='utf-8'
          return response.text

      # 解析城市信息
      def parse_city(self,city_response):
          e=etree.HTML(city_response)
          city_list=e.xpath('//div[@class="browse-landing-page"]//section[2]/ul/li/a/@href')
          return city_list

      # 解析location数据
      def parse_location(self,area_response):
          e=etree.HTML(area_response)
          area_list=e.xpath('//div[@id="minorRegionAndSuburbs"]/ul/li/a/@href')
          location_list=[]
          for area in area_list:
              location_list.append(area.split('/')[-1])

          return location_list

      # 保存location数据
      def save_data(self,city_name,location_list):
          if not os.path.exists(self.file_path):
                os.makedirs(self.file_path)
          filename=self.file_path+'location.csv'
          if not os.path.exists(filename):
              with open (filename,'w',encoding='utf-8',newline='')as f:
                    writer=csv.DictWriter(f,fieldnames=self.location_headers)
                    writer.writeheader()
          with open(filename, 'a', encoding='utf-8', newline='')as f:
              writer = csv.DictWriter(f, fieldnames=self.location_headers)
              for location in location_list:
                  loca={
                      'city_name':city_name,
                      'location':location
                  }
                  writer.writerow(loca)

      # 日志文件
      def location_log(self,log_str):
          date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          if not os.path.exists(self.file_path):
              os.makedirs(self.file_path)
          log_filename=self.file_path+'location_log.txt'
          with open(log_filename,'a',encoding='utf-8')as f:
              f.write(date_time+'\t'+log_str+'\n')

      # 启动方法
      def run(self):
          url='https://www.menulog.com.au/content/browse/'
          # 发送请求获取含有外卖城市信息响应
          try:
              city_response=self.get_response(url)
              print('请求首页成功')
              self.location_log('请求首页成功')
          except TimeoutError as e:
              city_response=''
              print('首页请求超时')
              self.location_log('首页请求超时')
          except Exception as e:
              city_response=''
              print('首页请求发生其他错误,错误信息为:'+str(e.args))
              self.location_log('首页请求发生其他错误,错误信息为:'+str(e.args))

          if city_response != '':
              # 解析城市信息url
              city_list=self.parse_city(city_response)

              # 遍历城市url列表,获取该城市下所有的郊区列表信息并保存
              for city in city_list:
                  try:
                      # city='https://www.menulog.com.au/browse/central-north-coast'
                      # 获取响应
                      area_response=self.get_response(city)
                      print('请求:' + city+'成功')
                      self.location_log('请求:' + city+'成功')
                  except TimeoutError as e:
                      area_response=''
                      print(city+'请求超时')
                      self.location_log(city+'请求超时')
                  except Exception as e:
                      area_response=''
                      print(city+'请求发生其他错误,错误信息为:'+str(e.args))
                      self.location_log(city+'请求发生其他错误,错误信息为:'+str(e.args))

                  if area_response != '':
                      city_name=city.split('/')[-1]
                      # 解析location信息列表
                      location_list=self.parse_location(area_response)
                      print(len(location_list))
                      # 保存location
                      self.save_data(city_name,location_list)
                      time.sleep(10)



if __name__ == '__main__':
      get_loc=GetLocation()
      get_loc.run()