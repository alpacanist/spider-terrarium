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


#橙光爬虫类
class CG:

    #初始化，传入基地址
    def __init__(self,gamenum,fileName):
        self.baseURL = 'http://www.66rpg.com/game/' + str(gamenum)
        self.file = fileName
        self.gameNUM = gamenum
        self.key = [u'编号：',u'标题：',u'作者：',u'人气：',u'鲜花：',u'字数：',u'分享：',u'点赞：',u'收藏：',u'发布时间：',u'最后更新：']
        # 编号是游戏数据的首项
        self.statistics = [str(gamenum)+'\n']
        self.tags = []
        self.tool = Tool()

    #传入编号
    #获取该游戏页代码
    def getGame(self):
        try:
            url = self.baseURL
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8','ignore')
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接失败,错误原因",e.reason
                return None

    #获取游戏标签
    def getTags(self,game):
        pattern = re.compile(u'<label class="tag">.*?<a href="/list/tag.*?target="_blank">(.*?)</a>.*?</label>',re.S)
        items = re.findall(pattern,game)
        for i in range(0,len(items)-1):
            #在后加入换行符
            datum = items[i] +"\n"
            self.tags.append(datum.encode('utf-8','ignore'))


    #获取游戏数据：标题，作者，游戏人气，鲜花，字数，分享，点赞，收藏，发布时间，最后更新
    def getStatistics(self,game):
        # 标题
        pattern_title = re.compile(u'<div class="game-info fl">.*?<div class="title">.*?<span title=.*?>(.*?)</span>',re.S)
        result_title = re.search(pattern_title,game)
        if result_title:
            #print result_title.group(1)  #测试输出
            self.statistics.append(result_title.group(1).strip()+'\n')
        else:
            self.statistics.append(u'未知\n')

        # 作者
        pattern_author = re.compile(u'<div class="infos fl">.*?<div class="name">.*?<a href="/friend.*?">(.*?)</a>',re.S)
        result_author = re.search(pattern_author,game)
        if result_author:
            #print result_author.group(1)  #测试输出
            self.statistics.append(result_author.group(1).strip()+'\n')
        else:
            self.statistics.append(u'未知\n')

        # 剩余数据
        pattern = re.compile('<div class="clearfix">.*?<span class="fl">.*?<span class="fr.*?">(.*?)</span>',re.S)
        items = re.findall(pattern,game)
        for item in items:
            #在后加入换行符
            datum = item +"\n"
            self.statistics.append(datum.encode('utf-8','ignore'))
        # print len(self.statistics)


    def writeData(self,file):
        floorLine = "\n" + u"-----------------------------------------------------------------------------------------\n"
        file.write(floorLine)
        #向文件写入游戏数据
        for i in range(0, len(self.key)):
            file.write(self.key[i].encode('utf-8','ignore') + self.statistics[i].encode('utf-8','ignore'))
        #写入游戏所属标签
        file.write('标签：\n')
        for tag in self.tags:
            file.write('- ')
            file.write(tag)


    def start(self):
        try:
            game = self.getGame()
            if game:
                file = open(self.file + ".txt","a")
                self.getStatistics(game)
                self.getTags(game)
                self.writeData(file)
        #出现写入异常
        except IOError,e:
            print "写入异常，原因" + e.message


# 此处写入
print u"橙光游戏爬虫"
choice = raw_input ("请输入编号进入对应功能：\n1. 获取单个游戏数据\n2. 批量获取游戏数据\n")
if not os.path.exists("cg"):
    os.makedirs("cg")
if choice == '1':
    gamenum = raw_input("请输入游戏编号: \nhttp://www.66rpg.com/game/")
    # 创建形如 gamenum.txt 的文件名
    cg = CG(gamenum, 'cg/'+str(gamenum))
    cg.start()
elif choice == '2':
    minmax = raw_input("请输入游戏编号范围（示例：0-999）: \n").split('-')
    min = int(minmax[0])
    max = int(minmax[1])
    print "共收集" + str(max-min+1) + "个游戏的数据"
    for i in range(min,max+1):
        print "正在写入第" + str(i-min+1) + "个游戏……"
        # 创建形如 min-max.txt 的文件名，模式追加
        cg = CG(i,'cg/'+str(min)+'-'+str(max))
        cg.start()
