import re
import os
import json
import requests
import shutil
from multiprocessing import Pool
from multiprocessing import Lock
from multiprocessing.dummy import Pool as ThreadPool

_REQUESTS_KWARGS = {
  # 'proxies': {
  #   'https': 'http://127.0.0.1:8888',
  # },
  'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}
class Pixiv(object):
    """docstring for Pixiv"""
    def __init__(self,username,password):
        # WebAPI
        self.webHeaders={
            'Cookie':'PHPSESSID=17005869_1273880beec4db4631ffce64d8c09a5d',
        }
        self.webId=17005869 
        self.webPostKey="1d74690f1612f3a28746ab5de3d16b50"
        # IOS Client API
        self.username=username
        self.password=password
        self.client_id = 'bYGKuGVw91e0NMfPGp44euvGt59s'
        self.client_secret = 'HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK'
        self.headers = {
            'App-OS': 'ios',
            'App-OS-Version': '10.3.1',
            'App-Version': '6.7.1',
            'User-Agent': 'PixivIOSApp/6.7.1 (iOS 10.3.1; iPhone8,1)',
        }
        self.lock = Lock()
        self.max_thread=8
        self.my_fav_illusts=[]
        self.illusts_url=[]
        self.process=0
        self.login()
    # 登陆
    def login(self):
        url = 'https://oauth.secure.pixiv.net/auth/token'
        data = {
            'get_secure_url': 1,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }
        r = requests.post(url,headers=self.headers, data=data)
        ret = json.loads(r.text)
        # print("login access_token：%s"%ret['response']['access_token'])
        self.headers['Authorization'] = 'Bearer %s' % ret['response']['access_token']
    def webLogin(self):
        pass
    # 读取收藏列表
    def getFavorite(self, page=1, per_page=50, pub='public', image_sizes=['px_128x128', 'px_480mw', 'large']):
        url = 'https://public-api.secure.pixiv.net/v1/me/favorite_works.json'

        self.headers['Referer'] = 'http://spapi.pixiv.net/'
        self.headers['User-Agent'] = 'PixivIOSApp/5.8.7'
        params = {
            'page': page,
            'per_page': per_page,
            'publicity': pub,
            'image_sizes': ','.join(image_sizes),
        }
        r = requests.get(url,headers=self.headers, params=params)
        ret = json.loads(r.text)
        return ret
    # 读取收藏列表 pub =['show','hide']
    def webGetFavorite(self,page=1, pub='show'):
        url = 'https://www.pixiv.net/touch/ajax/user/bookmarks'
        params = {
            'id': self.webId,
            'type': 'illust',
            'rest': pub,
            'p': page,
        }
        r = requests.get(url,headers=self.webHeaders, params=params)
        ret = json.loads(r.text)
        return ret

    def loadFavotire(self,d):
        for j in p.webGetFavorite(d[0],d[1])['bookmarks']:
            with self.lock:
                self.my_fav_illusts.append(j['id'])
    # 载入所有收藏
    def loadAllFavotire(self):
        threadPool=[]
        for pub in ['show','hide']:
            count_page = self.webGetFavorite(1,pub)['lastPage']
            print("%s has %d pages"%(pub,count_page))
            pool = ThreadPool(self.max_thread)
            pool.map(self.loadFavotire, [[i,pub] for i in range(1,count_page+1)])
            pool.close()
            pool.join()
        print("load done,total %d illusts\n"%(len(self.my_fav_illusts)))
    def getOriginal(self,illust_id):
        url = 'https://app-api.pixiv.net/v1/illust/detail'

        self.headers['Referer']=''
        params = {
            'illust_id': illust_id,
        }
        r = requests.get(url,headers=self.headers, params=params)
        ret = json.loads(r.text)

        urls=[]
        try:
            if ret['illust']['page_count']>1:
                for x in ret['illust']['meta_pages']:
                    urls.append(x['image_urls']['original'])
            else:
                urls.append(ret['illust']['meta_single_page']['original_image_url'])
        except Exception as e:
            print(ret)
        
        return urls
    def loadOriginal(self,illust_id):
        urls = self.getOriginal(illust_id)
        with self.lock:
            for url in urls:
                self.illusts_url.append(url)
            self.process=self.process+1
            print("now loading %d%% %d/%d"%((self.process/len(self.my_fav_illusts))*100,self.process,len(self.my_fav_illusts)),end='\r')
    def loadAllOriginal(self):
        pool = ThreadPool(self.max_thread)
        pool.map(self.loadOriginal, self.my_fav_illusts)
        pool.close()
        pool.join()
        print("\nload done,total %d urls\n"%(len(self.illusts_url)))
    def download(self,illust_id,save_as='./'):
        original_url=self.getOriginal(illust_id)

        self.headers['Referer']='https://app-api.pixiv.net/'
        r = requests.get(original_url,headers=self.headers, stream=True)
        img_path=save_as+os.path.basename(original_url)
        with open(img_path, 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)
        del r

#读取
p=Pixiv("youremail", "password")
p.loadAllFavotire()
p.loadAllOriginal()
# result1=['43205533','38187550','38215204']
# for i in result1:
#     print("downloading %s"%i)
#     p.download(i)
