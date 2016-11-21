# spider-terrarium
一组网络爬虫生活的玻璃箱。
A collection of web crawlers using python urllib.
## xq.py
爬取晋江论坛主题帖。
### 功能
1. 指定需要下载的论坛编号（fid）
2. 批量下载/下载指定主题编号到名为 `xq/<fid>` 的目录
### 如何使用？
1. 下载，在终端中打开目录
2. 运行 `python xq.py`
3. 按命令行提示操作
## xq.py
Crawls bbs.jjwxc.net forum threads. 
### Features
1. Crawl threads from a particular sub-forum by fid
2. Switch between batch-download/single-thread mode, download in to directory `xq/<fid>`
### How to use?
1. Download and cd to directory in terminal
2. Run `python xq.py`
3. Follow instructions
