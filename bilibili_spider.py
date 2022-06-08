import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import traceback
import  time
import pymysql

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
proxies = {
    'https': 'socks5://127.0.0.1:10808'

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
r = requests.get(url, headers=headers,proxies=proxies)
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
                           password="zh332233",
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
        # print(f"{time.asctime()}开始更新最新数据")
        sql = "insert into web(bvid,title) values (%s,%s)"
        sql_query = "select bvid,title from web"
        cursor.execute(sql_query)
        query = cursor.fetchall()
        # print(query[0][0])
        query_list1=[]
        query_list2=[]
        for i in query:
            query_list1.append(i[0])
            query_list2.append(i[1])
        # print(query_list)
        update_list1 = [x for x in (bvid_list + query_list1) if x not in query_list1]
        update_list2 = [x for x in (title_list + query_list2) if x not in query_list2]
        update_list = list(zip(update_list1,update_list2))
        # print(update_list)
        for i in range(0,len(update_list)):
            cursor.execute(sql,[update_list[i][0],update_list[i][1]])
        # for i in bvid_list:
        #     if i not in query_list:
        #         print(i)
        # for i in sql_list:
        #     if  not cursor.execute(sql_query):
        #         for i in range(0,len(sql_list)):
        #             cursor.execute(sql,[sql_list[i][0],sql_list[i][1]])
        conn.commit()  # 提交事务 update delete insert操作
        # print(f"{time.asctime()}更新最新数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)
    return update_list

def text_input(bv,aid,cid):
    default_setting=' width="800" height="600"'
    share_url = "https://www.bilibili.com/video/{}".format(bv)
    video_url = '<iframe src="//player.bilibili.com/player.html?aid={}&bvid={}&cid={}&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"{}> </iframe>'  .format(aid,bv,cid,default_setting)
    return share_url,video_url

def get_cid(url):
    get_cid="https://api.bilibili.com/x/player/pagelist?bvid={}&jsonp=jsonp".format(url)
    r = requests.get(get_cid, headers=headers,proxies=proxies)
    jsont = r.json()
    cid = jsont['data'][0]['cid']
    return cid


def get_aid(url):
    get_aid="https://api.bilibili.com/x/web-interface/archive/stat?bvid={}".format(url)
    r = requests.get(get_aid, headers=headers,proxies=proxies)
    jsont = r.json()
    aid = jsont['data']['aid']
    return aid

def get_bv_des(url):
    text="https://www.bilibili.com/video/{}".format(url)
    r = requests.get(text, headers=headers,proxies=proxies)
    html = r.content.decode()
    soup = BeautifulSoup(html,'lxml')
    text = soup.find(name = 'div',attrs={'class':'desc-info desc-v2'}).get_text()
    # text = soup.find('div', class_='desc-info desc-v2 open').get_text()
    # text = soup.select('#v_desc > div.desc-info.desc-v2.open > span')
    return text
if __name__ == '__main__':
# update_details()
    aid = get_aid(sql_list[0][0])
    des = get_bv_des(sql_list[0][0])
    cid = get_cid(sql_list[0][0])
    text = text_input(sql_list[0][0],aid,cid)
    # print("aid:",aid)
    # print("cid:",cid)
    # insert_history()
    update_list = update_details()
    if len(update_list):
        print(f"{time.asctime()}开始更新最新数据")
        print(update_list)
        print("分享地址:\n",text[0])
        print("iframe:\n",text[1])
        print(des)
        print(f"{time.asctime()}更新最新数据完毕")
    else:
        print("no update")
