"""第三方包：pip install requests 后发一个请求，对应笔记 5.7。

先在 PyCharm 下方 Terminal 里运行：pip install requests
本文件需要联网才能跑通。
"""

import requests

# 发一个 GET 请求，把返回内容拿回来
resp = requests.get("https://api.github.com")
print(resp.status_code)     # 200：请求成功
print(resp.text[:100])      # 返回内容的前 100 个字符

# 返回内容是 JSON 时，一步转成字典接着取值
resp = requests.get("https://api.github.com/users/octocat")
data = resp.json()
print(data["login"])
print(data.get("name", "无名氏"))
