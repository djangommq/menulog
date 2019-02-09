# menulog

## 代码地址
[gitlab](https://gitlab.yunfutech.com/uber_crawler/menulog)  
脚本操作见 readme.md


## 使用说明

1. 运行
    ```
        每次启动前修改menulog.py脚本中的VERSION
        python3 menulog.py
    ```

2. 失败处理
    ```
        每次运行请求location ,成功的location会保存在input/has_location文件中, 失败的会保存在fail_data/fail_location文件中,
        每次运行结束后删除fail_location文件,重新启动脚本会再次请求失败的location,重复多次
    ```
3. 
    ```
        请求的失败的餐馆会保存在fail_data/fail_rest文件中,运行处理失败餐馆脚本
        python3 load_fail.py
        会循环遍历请求这些失败的餐馆 , 每次回输出列表的长度 , 列表的长度不再改变为止
    ```
    
4. 数据保存
    ```
        数据最终保存在东京0上的mongo数据库,运行脚本导出数据
        数据保存在~/crawlerOutput/date/menulog中
    ```



