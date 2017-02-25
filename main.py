# -*- coding:utf-8 -*-
import os,sys,json,requests,threading
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Lock
from pixivpy3 import *

user = "Your@Pixiv.net"  #你的Pixiv登陆邮箱/用户名
pwd = "YourPassword"          #你的Pixiv登陆密码
path = './downloads/pixiv/' #下载位置
max_thread = 32             #最大线程数量

if not os.path.exists(path):
    os.makedirs(path)

lock = Lock()
api = PixivAPI()
token = api.login(user, pwd)

illust_url_list = []
#读取作品下载链接到illust_url_list
def read_illust(pg):
    global pub,illust_url_list,page_count
    with lock:
        page_count += 1
    result = api.me_favorite_works(publicity=pub,page=pg)
    for i in result.response :
        with lock:
            print("reading %s illust list...%d/%d"%(pub,page_count,pg_result.pagination.pages),end='\r')
        if (i.work.page_count > 1):
            illust=api.works(i.work.id)
            for p in illust.response[0].metadata.pages:
                with lock:
                    illust_url_list.append(p.image_urls.large)
        else:
            with lock:
                illust_url_list.append(i.work.image_urls.large)

download_count=0;
def download_illust(illust_url):
    global illust_url_list,download_count
    with lock:
        download_count +=1
        print("downloading %d/%d"%(download_count,len(illust_url_list)),end='\r')
    api.download(illust_url,path)

fav_list = ['pubilc','private']
page_count = 0
page_list = None
pub = None
for k in fav_list:
    page_count = 0#清空页码计数器
    page_list = []#清空页码列表
    pub = k
    pg_result = api.me_favorite_works(publicity = pub)
    for i in range(pg_result.pagination.pages):
        page_list.append(i+1)
    pool = ThreadPool(max_thread)
    pool.map(read_illust, page_list)
    pool.close()
    pool.join()
    print('\n',end='\r')
pool = ThreadPool(max_thread)
data = pool.map(download_illust, illust_url_list)
pool.close()
pool.join()
print('\n下载完毕')
