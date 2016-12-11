# -*- coding:utf-8 -*-
import os,sys,json,requests
from pixivpy3 import *
user=raw_input("Username:")
pwd=raw_input("Password:")
path = raw_input("Save as:")
path=path+'\\'
if not os.path.exists(path):
    os.makedirs(path)
api = PixivAPI()
token = api.login(user, pwd)

def multi_download(url,path,ill_id,count=1):
    id_str=str(ill_id)
    url_model=url[:url.find(id_str)+len(id_str)+2]
    file_ext=os.path.splitext(url)[1]
    if not os.path.exists(path+'\\'+str(ill_id)+'\\'):
        os.makedirs(path+'\\'+str(ill_id)+'\\')
    for p in range(count):
        print("\tpage:%d"%(p))
        api.download(url_model+str(p)+file_ext,path+'\\'+str(ill_id)+'\\')
#下载公开收藏
json_result = api.me_favorite_works(publicity='public')
for i in json_result.response :
    illust = i.work
    print("downloading %d page count: %d" % (illust.id,illust.page_count))
    if (illust.page_count > 1):
        multi_download(illust.image_urls.large,path,illust.id,illust.page_count)
    else:
        api.download(illust.image_urls.large,path)
#下载私人收藏
json_result = api.me_favorite_works(publicity='private')
for i in json_result.response :
    illust = i.work
    print("downloading %d page count: %d" % (illust.id,illust.page_count))
    if (illust.page_count > 1):
        multi_download(illust.image_urls.large,path,illust.id,illust.page_count)
    else:
        api.download(illust.image_urls.large,path)
