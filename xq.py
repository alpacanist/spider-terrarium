# -*- coding:utf-8 -*-
# 修改自：http://cuiqingcai.com/993.html

import urllib
import urllib2
import re
import os

#处理页面标签类
class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()


#闲情爬虫类
class DMXQ:

    #初始化，传入基地址
    def __init__(self,baseUrl,path):
        self.baseURL = baseUrl
        self.tool = Tool()
        self.file = None
        #楼层标号，初始为1
        self.floor = 1
        #默认的标题，如果没有成功获取到标题的话则会用这个标题
        self.defaultTitle = u" 本贴已被删除！"
        self.path = path

    #传入页码，获取该页帖子的代码
    def getPage(self,pageNum):
        try:
            url = self.baseURL+ '&page=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('GBK','ignore')
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接失败,错误原因",e.reason
                return None

    #获取帖子标题
    def getTitle(self,page):
        pattern = re.compile(u'主题：(.*?)<font',re.S)
        result = re.search(pattern,page)
        if result:
            #print result.group(1)  #测试输出
            return result.group(1).strip()
        else:
            return None

    #获取帖子一共有多少页
    def getPageNum(self,page):
        pattern = re.compile(u'共(.*?)页',re.S)
        result = re.search(pattern,page)
        if result:
            #print result.group(1)  #测试输出
            return result.group(1).strip()
        else:
            return 1

    #获取每一层楼的内容,传入页面内容
    def getContent(self,page):
        pattern = re.compile('id="topic">(.*?)</div>',re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            #将文本进行去除标签处理，同时在前后加入换行符
            content = "\n"+self.tool.replace(item)+"\n"
            contents.append(content.encode('utf-8'))
        return contents

    def setFileTitle(self,title):
        #如果标题不是为None，即成功获取到标题
        if title is not None:
            self.file = open(self.path + title + ".txt","w+")
        else:
            self.file = open(self.path + self.defaultTitle + ".txt","w+")

    def writeData(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            floorLine = "\n" + str(self.floor-1) + u"-----------------------------------------------------------------------------------------\n"
            self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1


    def start(self):
        indexPage = self.getPage(0)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        try:
            try:
                print "该帖子共有" + str(pageNum) + "页"
            except:
                print "该帖不存在"
            try:
                for i in range(0,int(pageNum)):
                    print "正在写入第" + str(i+1) + "页数据"
                    page = self.getPage(i)
                    contents = self.getContent(page)
                    self.writeData(contents)
            except:
                print "无法写入"
        #出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message
        finally:
            print "写入任务完成"



# 此处写入
def main():
    fid = raw_input("输入论坛编号：")
    path = "xq/"+fid+"/"
    if not os.path.exists(path):
        os.makedirs(path)
    menu = raw_input("输入下载模式（1 - 批量 2 - 单贴）：")
    if menu == '1':
        print "输入帖子编号范围（示例：0-999）: "
        minmax = raw_input("http://bbs.jjwxc.net/showmsg.php?board="+fid+"&id=").split('-')
        min = int(minmax[0])
        max = int(minmax[1])
        print "共下载" + str(max-min+1) + "个主题帖"
    elif menu == '2':
        print "输入帖子编号: "
        min = int(raw_input("http://bbs.jjwxc.net/showmsg.php?board="+fid+"&id="))
        max = min
    else:
        print "没有这种模式"
    for i in range(min, max+1):
        baseURL = 'http://bbs.jjwxc.net/showmsg.php?board='+fid+'&id='+str(i)
        dmxq = DMXQ(baseURL,path)
        dmxq.start()

if __name__ == "__main__":
    main()
