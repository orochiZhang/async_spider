# -*- coding: utf-8 -*-

import aiohttp
import aiofiles
import asyncio


class Task(object):
    
    def __init__(self, url, ):
        self.url = url
    
    # 解析页面
    async def parse(self, html, work_queue):
        pass


class AsyncSpider(object):
    
    def __init__(self, task, max_threads):
        self.tasks = task
        self.max_threads = max_threads
    
    # 事件循环
    def event_loop(self):
        q = asyncio.Queue()
        [q.put_nowait(task) for task in self.tasks]
        loop = asyncio.get_event_loop()
        tasks = [self.handle_tasks(task_id, q, ) for task_id in range(self.max_threads)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
    
    # 任务分发
    async def handle_tasks(self, task_id, work_queue):
        while not work_queue.empty():
            task = await work_queue.get()
            try:
                await self.get_results(task.url, task, work_queue)
            except Exception as e:
                print(e)
    
    # 爬虫主流程
    async def get_results(self, url, task, work_queue):
        html = await self.get_body(url)
        await task.parse(html, work_queue)
        return 1
    
    # 获取html
    async def get_body(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.read()
                    return html
                else:
                    # 记录失败的页面
                    await self.write_file(str(response.status) + " " + url, 'err.txt')
    
    # 异步写文件
    async def write_file(self, contents, file):
        async with aiofiles.open(file, mode='a') as f:
            if contents.endswith('\n'):
                await f.writelines(contents)
            else:
                await f.writelines(contents + '\n')

