# 简易的异步爬虫

## 使用说明
- 异步爬虫是基于asyncio，aiohttp。
- AsyncSpider 为主流程类，主要负责创建asyncio.Queue和触发asyncio event loop的事件循环，主流程必须执行完asyncio.Queue所有任务才结束。
- Task类为任务基类，主要存储需要爬取的url，parse函数为这个页面对应的页面数据爬取逻辑，形参work_queue为asyncio.Queue。
- TaskA 的爬取结果可能是一些url，这时候可以针对新的url创建TaskB，TaskB有对应的parse函数。然后把TaskB加入到work_queue，等待执行爬取。
- 整个爬虫流程模型如下：
```
AsyncSpider.event_loop()
  \
  asyncio.Queue.put_nowait(TaskA) -> loop.run_until_complete(asyncio.wait(tasks))
    \
    TaskA().parse() -> new url -> New TaskB() -> asyncio.Queue.put_nowait(TaskB)
      \
      TaskB().parse() -> new url -> New TaskC() -> asyncio.Queue.put_nowait(TaskC)
        \
        ……
          \
         TaskE().parse() -> result -> mysql/mongodb/txt
            \
            asyncio.Queue is [], return
```
或者这样
```
AsyncSpider.event_loop()
  \
  asyncio.Queue.put_nowait(TaskA) -> loop.run_until_complete(asyncio.wait(tasks))
    \
    TaskA().parse() -> new url -> New TaskB()， New TaskC() -> asyncio.Queue.put_nowait(TaskB) put_nowait(TaskC)
      \    \
       \   TaskB().parse() -> new url -> New TaskE() -> asyncio.Queue.put_nowait(TaskE)
        \
        TaskC().parse() -> new url -> New TaskD() -> asyncio.Queue.put_nowait(TaskD)
          \
          ……
            \
          TaskF().parse() -> result -> mysql/mongodb/txt
              \
            asyncio.Queue is [], return
```

## 使用例子
```python
# -*- coding: utf-8 -*-

import re
from AsyncSpider import AsyncSpider


# 任务类型1
class TaskA(AsyncSpider.Task):
    
    # 解析页面
    async def parse(self, html, work_queue):
        id_re = re.compile(r'"https://blog\.csdn\.net/Notzuonotdied/article/details/(.*?)"')
        id_list = id_re.findall(html.decode('utf-8'))
        for id in id_list:
            print(id)
            url = "https://blog.csdn.net/Notzuonotdied/article/details/" + id
            task = TaskB(url)             # 爬取到的url作为任务类型2的url
            work_queue.put_nowait(task)   # 把任务类型2加入待处理的队列
            
# 任务类型2
class TaskB(AsyncSpider.Task):
    
    # 解析页面
    async def parse(self, html, work_queue):
        content_re = re.compile(r'id="content_views"(.*?)id="csdn-shop-window"', re.DOTALL)   # 简单的匹配，获取到文章内容
        content = content_re.findall(html.decode('utf-8'))
        print(content)    # 记录数据，可以存mysql，mongodb，txt等，或者做进一步的数据清洗
       

if __name__ == '__main__':
    # 简单的博客爬虫demo，任务类型1爬取文章列表的url，任务类型2爬取文章的具体内容。
    l = [TaskA("https://blog.csdn.net/notzuonotdied")]
    async_example = AsyncSpider.AsyncSpider(l, 500)   #500为并发执行的协程数量
    async_example.event_loop()
```
