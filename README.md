# Pixiv Favorite Downloader
Tested on Python3.6 似乎不支持Python2.7
###Install pixivpy
~~~
pip install pixivpy
~~~

###Usage
先编辑main.py,修改里面的`user`变量和`pwd`变量的值,填写你的Pixiv账号密码,保存运行即可

####关于 max_thread 变量
`max_thread`变量用于限制下载线程数量,理论上这个变量值越大下载速度快,当然我不清楚连接数太多会不会被Ban.自己看着改吧,默认值为`32`
