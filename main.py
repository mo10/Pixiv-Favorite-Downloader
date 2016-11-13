# -*- coding:utf-8 -*-
import sys,json,requests
from pixivpy3 import *

api = PixivAPI()
token = api.login("Your Username", "Your Password")
path = "Save in Path"
#下载公开收藏
json_result = api.me_favorite_works(publicity='public')
for i in json_result.response :
	illust = i.work
	print("downloading public favorite %d" % (illust.id))
	api.download(illust.image_urls.large,path)
#下载私人收藏
json_result = api.me_favorite_works(publicity='private')
for i in json_result.response :
	illust = i.work
	print("downloading private favorite %d" % (illust.id))
	api.download(illust.image_urls.large,path)
