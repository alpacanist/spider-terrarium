# -*- coding:utf-8 -*-
# 修改自：http://cuiqingcai.com/993.html

import urllib
import urllib2
import re

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
    #去除乱码
    removeGibberish = re.compile('<span style="display:none">(.*?)</span>')
    removeJammer = re.compile('<font class="jammer">(.*?)</font>')

    def replace(self,x):
        x = re.sub(self.removeGibberish,"",x)
        x = re.sub(self.removeJammer,"",x)
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

#长佩爬虫类
class CP:

    #初始化，传入基地址
    def __init__(self,baseUrl):
        self.baseURL = baseUrl
        self.tool = Tool()
        self.file = None
        #楼层标号，初始为1
        self.floor = 1
        #默认的标题，如果没有成功获取到标题的话则会用这个标题
        self.defaultTitle = u"error"

    #传入页码，获取该页帖子的代码
    def getPage(self,pageNum):
        try:
            url = self.baseURL+ '&page=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8','ignore')
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接失败,错误原因",e.reason
                return None

    #获取帖子标签和标题
    def getTitle(self,page):
        pattern_tag = re.compile(u'<h1 class="ts".*?<a href=".*?typeid=.*?">(.*?)</a>',re.S)
        pattern_title = re.compile(u'<h1 class="ts".*?<span id="thread_subject">(.*?)</span>',re.S)
        result_tag = re.search(pattern_tag,page)
        result_title = re.search(pattern_title,page)
        if result_tag or result_title:
            #print result.group(1)  #测试输出
            return result_tag.group(1).strip()+result_title.group(1).strip()
        else:
            return None

    #获取帖子一共有多少页
    def getPageNum(self,page):
        pattern = re.compile(u'共 (.*?) 页',re.S)
        result = re.search(pattern,page)
        if result:
            #print result.group(1)  #测试输出
            return result.group(1).strip()
        else:
            return 1

    #获取每一层楼的内容,传入页面内容
    def getContent(self,page):
        pattern = re.compile('<td class="t_f" id="postmessage_.*?">(.*?)</td>',re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            #将文本进行去除标签处理，同时在前后加入换行符
            content = "\n"+self.tool.replace(item)+"\n"
            contents.append(content.encode('utf-8','ignore'))
        return contents

    def setFileTitle(self,title):
        #如果标题不是为None，即成功获取到标题
        print title
        if title is not None:
            self.file = open("cp/" + title + ".txt","w+")
        else:
            self.file = open("cp/"  + self.defaultTitle + ".txt","w+")

    def writeData(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            floorLine = "\n" + str(self.floor-1) + u"-----------------------------------------------------------------------------------------\n"
            self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1


    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        try:
            try:
                print "该帖子共有" + str(pageNum) + "页"
            except:
                print "该帖不存在"
            try:
                for i in range(1,int(pageNum)+1):
                    print "正在写入第" + str(i) + "页数据"
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
for i in range(20000, 20001):
    print i
    baseURL = 'http://allcp.net/forum.php?mod=viewthread&tid='+str(i)
    cp = CP(baseURL)
    cp.start()
