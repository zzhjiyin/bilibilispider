import requests
from bs4 import BeautifulSoup
import json
from bilibili_api import video
import re
import csv
import traceback
import  time
import pymysql

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
# url="https://space.bilibili.com/20927?from=search&seid=15325431671173261800"
#
# r = requests.get(url, headers=headers)
# html = r.content.decode()
# soup = BeautifulSoup(html,'lxml')
#
# v = video.get_video_info(bvid="BV1n64y127w4")
# # print(json.dumps(v, indent=4, ensure_ascii=False))
# json_str = json.dumps(v)
# pattern = re.compile(r'BV.{10}')
# result = pattern.findall(json_str)
# # print(result)
# print(v)
results=[]
title_list=[]
bvid_list=[]
url="https://api.bilibili.com/x/space/arc/search?mid=20927&pn=1&ps=25&index=1&jsonp=jsonp"
r = requests.get(url, headers=headers)
html = r.content.decode()
jsont=  r.json()
results= jsont['data']['list']['vlist']
for i in results:
    if bool(re.search("美国单曲周榜", i['title'])) == True:
        bvid_list.append(i['bvid'])
        title_list.append(i['title'])
sql_list = list(zip(bvid_list,title_list))
#print(sql_list)

def get_conn():
    """
    :return: 连接，游标
    """
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1",
                           user="root",
                           password="4zzhjiyin",
                           db="bilibili",
                           charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor


def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def insert_history():
    """
        插入历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        print(f"{time.asctime()}开始插入数据")
        conn, cursor = get_conn()
        sql = "insert into web(bvid,title) values (%s,%s)"
        for i in range(0,len(sql_list)):
            cursor.execute(sql,[sql_list[i][0],sql_list[i][1]])
            print(sql_list[i][0]," ",sql_list[i][1])
        conn.commit()
        print(f"{time.asctime()}插入完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)
def update_details():
    """
    更新 表
    :return:
    """
    cursor = None
    conn = None
    try:
        conn, cursor = get_conn()
        print(f"{time.asctime()}开始更新最新数据")
        sql = "insert into web(bvid,title) values (%s,%s)"
        sql_query = "select bvid,title from web"
        for i in sql_list:
            if not cursor.execute(sql_query):
                for i in range(0,len(sql_list)):
                    cursor.execute(sql,[sql_list[i][0],sql_list[i][1]])
        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}更新最新数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def text_input():
    default_setting=',width="800",height="600"'
    text="https://www.bilibili.com/video/{}".format(sql_list[0][0])
    get_aid="https://api.bilibili.com/x/web-interface/archive/stat?bvid={}".format((sql_list[0][0]))
    get_cid="https://api.bilibili.com/x/player/pagelist?bvid={}&jsonp=jsonp".format(sql_list[0][0])
    r = requests.get(get_cid, headers=headers)
    jsont=  r.json()
    cid = jsont['data']['cid']
    r = requests.get(get_aid, headers=headers)
    jsont=  r.json()
    aid = jsont['data']['aid']
    return text,cid,aid
#update_details()
url= text_input()
def get_cid(url):
    r = requests.get(url, headers=headers)
    jsont = r.json()
    cid = jsont['data'][0]['cid']
    return cid


def get_aid(url):
    r = requests.get(url, headers=headers)
    jsont = r.json()
    aid = jsont['data']['aid']
    return aid
print(text_input())
