# Created by moeheart at 01/14/2022
# 奶毒复盘，用于奶毒复盘的生成，展示

from replayer.ReplayerBase import ReplayerBase
from replayer.BattleHistory import BattleHistory, SingleSkill
from replayer.TableConstructor import TableConstructor, ToolTip
from tools.Names import *
from Constants import *
from tools.Functions import *
from equip.AttributeDisplayRemote import AttributeDisplayRemote
from equip.EquipmentExport import EquipmentAnalyser, ExcelExportEquipment
from replayer.Name import *

import os
import time
import json
import copy
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import urllib.request
import hashlib
import webbrowser
import pyperclip

class BuTianJueWindow():
    '''
    奶毒复盘界面显示类.
    通过tkinter将复盘数据显示在图形界面中.
    '''

    def getMaskName(self, name):
        '''
        获取名称打码的结果。事实上只需要对统计列表中的玩家打码.
        params:
        - name: 打码之前的玩家名.
        '''
        s = name.strip('"')
        if s == "":
            return s
        elif self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s) - 1)

    def final(self):
        '''
        关闭窗口。
        '''
        self.windowAlive = False
        self.window.destroy()

    def exportEquipment(self):
        '''
        导出装备信息到剪贴板.
        '''
        copyText = self.result["equip"]["raw"]
        pyperclip.copy(copyText)
        messagebox.showinfo(title='提示', message='复制成功！')

    def OpenInWeb(self):
        '''
        打开网页版的复盘界面.
        '''
        url = "http://139.199.102.41:8009/showReplayPro.html?id=%d"%self.result["overall"]["shortID"]
        webbrowser.open(url)

    def showHelp(self):
        '''
        展示复盘窗口的帮助界面，用于解释对应心法的一些显示规则.
        '''
        text = '''时间轴中从上到下的四个条分别表示：迷仙引梦、仙王蛊鼎、蛊惑众生、醉舞九天。
醉舞九天作为不占gcd的技能，不会在技能轴中显示，而是改为在时间轴内部显示。
战斗效率包含醉舞九天的读条时间，而gcd效率则不包含。'''
        messagebox.showinfo(title='说明', message=text)

    def loadWindow(self):
        '''
        使用tkinter绘制详细复盘窗口。
        '''
        window = tk.Toplevel()
        # window = tk.Tk()
        window.title('奶毒复盘')
        window.geometry('750x900')

        # print(self.result)

        # if "mask" in self.result["overall"]:
        #     self.mask = self.result["overall"]["mask"]  # 使用数据中的mask选项顶掉框架中现场读取的判定

        # Part 1: 全局
        frame1 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground="#3f1f9f")
        frame1.place(x=10, y=10)
        frame1sub = tk.Frame(frame1)
        frame1sub.place(x=0, y=0)
        tb = TableConstructor(self.config, frame1sub)
        tb.AppendContext("复盘版本：", justify="right")
        tb.AppendContext(self.result["overall"]["edition"])
        tb.EndOfLine()
        tb.AppendContext("玩家ID：", justify="right")
        tb.AppendContext(self.result["overall"]["playerID"], color="#3f1f9f")
        tb.EndOfLine()
        tb.AppendContext("服务器：", justify="right")
        tb.AppendContext(self.result["overall"]["server"])
        tb.EndOfLine()
        tb.AppendContext("战斗时间：", justify="right")
        tb.AppendContext(self.result["overall"]["battleTimePrint"])
        tb.EndOfLine()
        tb.AppendContext("生成时间：", justify="right")
        tb.AppendContext(self.result["overall"]["generateTimePrint"])
        tb.EndOfLine()
        tb.AppendContext("地图：", justify="right")
        tb.AppendContext(self.result["overall"]["map"])
        tb.EndOfLine()
        tb.AppendContext("首领：", justify="right")
        tb.AppendContext(self.result["overall"]["boss"], color="#ff0000")
        tb.EndOfLine()
        tb.AppendContext("人数：", justify="right")
        tb.AppendContext("%.2f"%self.result["overall"].get("numPlayer", 0))
        tb.EndOfLine()
        tb.AppendContext("战斗时长：", justify="right")
        tb.AppendContext(self.result["overall"]["sumTimePrint"])
        tb.EndOfLine()
        tb.AppendContext("数据种类：", justify="right")
        tb.AppendContext(self.result["overall"]["dataType"])
        tb.EndOfLine()

        # Part 2: 装备
        frame2 = tk.Frame(window, width=200, height=230, highlightthickness=1, highlightbackground="#3f1f9f")
        frame2.place(x=220, y=10)
        frame2sub = tk.Frame(frame2)
        frame2sub.place(x=0, y=0)
        if self.result["equip"]["available"] == 0:
            text = "装备信息获取失败。\n在进入战斗后打开团队装分面板即可获取。\n如果是第一视角也可以自动获取。"
            tk.Label(frame2, text=text, justify="left").place(x=0, y=0)
        else:
            tb = TableConstructor(self.config, frame2sub)
            tb.AppendContext("装备分数：", justify="right")
            color4 = "#000000"
            if "大橙武" in self.result["equip"]["sketch"]:
                color4 = "#ffcc00"
            tb.AppendContext("%d"%self.result["equip"]["score"], color=color4)
            tb.EndOfLine()
            tb.AppendContext("详情：", justify="right")
            tb.AppendContext(self.result["equip"]["sketch"])
            tb.EndOfLine()
            tb.AppendContext("强化：", justify="right")
            tb.AppendContext(self.result["equip"].get("forge", ""))
            tb.EndOfLine()
            tb.AppendContext("根骨：", justify="right")
            tb.AppendContext("%d"%self.result["equip"]["spirit"])
            tb.EndOfLine()
            tb.AppendContext("治疗量：", justify="right")
            tb.AppendContext("%d(%d)"%(self.result["equip"]["heal"], self.result["equip"]["healBase"]))
            tb.EndOfLine()
            tb.AppendContext("会心：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["critPercent"], self.result["equip"]["crit"]))
            tb.EndOfLine()
            tb.AppendContext("会心效果：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["critpowPercent"], self.result["equip"]["critpow"]))
            tb.EndOfLine()
            tb.AppendContext("加速：", justify="right")
            tb.AppendContext("%s(%d)"%(self.result["equip"]["hastePercent"], self.result["equip"]["haste"]))
            tb.EndOfLine()

            b2 = tk.Button(frame2, text='导出', height=1, command=self.exportEquipment)
            b2.place(x=140, y=180)

        # Part 3: 治疗
        frame3 = tk.Frame(window, width=310, height=150, highlightthickness=1, highlightbackground="#3f1f9f")
        frame3.place(x=430, y=10)
        frame3sub = tk.Frame(frame3)
        frame3sub.place(x=0, y=0)

        tb = TableConstructor(self.config, frame3sub)
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("有效HPS", "最常用语境下的每秒治疗量，注意包含重伤时间。")
        tb.AppendHeader("虚条HPS", "指虚条的最右端，包含溢出治疗量，也即计算所有绿字。")
        tb.EndOfLine()
        for record in self.result["healer"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["healEff"])
            tb.AppendContext(record["heal"])
            tb.EndOfLine()

        # Part 4: 奇穴
        frame4 = tk.Frame(window, width=310, height=70, highlightthickness=1, highlightbackground="#3f1f9f")
        frame4.place(x=430, y=170)
        if self.result["qixue"]["available"] == 0:
            text = "奇穴信息获取失败。\n在进入战斗后查看目标的奇穴即可获取。\n如果是第一视角也可以自动获取。"
            tk.Label(frame4, text=text, justify="left").place(x=0, y=0)
        else:
            text = ""
            for i in range(1, 7):
                text = text + self.result["qixue"][str(i)] + ','
            text = text + '\n'
            for i in range(7, 13):
                text = text + self.result["qixue"][str(i)] + ','
            text = text[:-1]
            tk.Label(frame4, text=text, justify="left").place(x=0, y=0)

        # Part 5: 技能
        # TODO 加入图片转存
        frame5 = tk.Frame(window, width=730, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame5.place(x=10, y=250)

        frame5_1 = tk.Frame(frame5, width=180, height=95)
        frame5_1.place(x=0, y=0)
        frame5_1.photo = tk.PhotoImage(file="icons/2745.png")
        label = tk.Label(frame5_1, image=frame5_1.photo)
        label.place(x=5, y=25)
        ToolTip(label, "冰蚕牵丝")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["bcqs"]["num"], self.result["skill"]["bcqs"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["bcqs"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["bcqs"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["bcqs"]["effRate"])
        label = tk.Label(frame5_1, text=text, justify="left")
        label.place(x=60, y=15)

        frame5_2 = tk.Frame(frame5, width=180, height=95)
        frame5_2.place(x=180, y=0)
        frame5_2.photo = tk.PhotoImage(file="icons/2746.png")
        label = tk.Label(frame5_2, image=frame5_2.photo)
        label.place(x=5, y=25)
        ToolTip(label, "醉舞九天")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["zwjt"]["num"], self.result["skill"]["zwjt"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["zwjt"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["zwjt"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["zwjt"]["effRate"])
        label = tk.Label(frame5_2, text=text, justify="left")
        label.place(x=60, y=15)

        frame5_3 = tk.Frame(frame5, width=180, height=95)
        frame5_3.place(x=360, y=0)
        frame5_3.photo = tk.PhotoImage(file="icons/3028.png")
        label = tk.Label(frame5_3, image=frame5_3.photo)
        label.place(x=5, y=25)
        ToolTip(label, "圣手织天")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["sszt"]["num"], self.result["skill"]["sszt"]["numPerSec"])
        text = text + "延迟：%dms\n" % self.result["skill"]["sszt"]["delay"]
        text = text + "HPS：%d\n" % self.result["skill"]["sszt"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["sszt"]["effRate"])
        label = tk.Label(frame5_3, text=text, justify="left")
        label.place(x=60, y=15)

        frame5_4 = tk.Frame(frame5, width=180, height=95)
        frame5_4.place(x=540, y=0)
        frame5_4.photo = tk.PhotoImage(file="icons/2748.png")
        label = tk.Label(frame5_4, image=frame5_4.photo)
        label.place(x=5, y=25)
        ToolTip(label, "千蝶吐瑞")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["qdtr"]["num"], self.result["skill"]["qdtr"]["numPerSec"])
        text = text + "HPS：%d\n" % self.result["skill"]["qdtr"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["qdtr"]["effRate"])
        label = tk.Label(frame5_4, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_5 = tk.Frame(frame5, width=180, height=95)
        frame5_5.place(x=0, y=100)
        frame5_5.photo = tk.PhotoImage(file="icons/9567.png")
        label = tk.Label(frame5_5, image=frame5_5.photo)
        label.place(x=5, y=25)
        ToolTip(label, "蝶池")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["dc"]["num"], self.result["skill"]["dc"]["numPerSec"])
        text = text + "HPS：%d\n" % self.result["skill"]["dc"]["HPS"]
        text = text + "有效比例：%s%%\n" % parseCent(self.result["skill"]["dc"]["effRate"])
        label = tk.Label(frame5_5, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_6 = tk.Frame(frame5, width=180, height=95)
        frame5_6.place(x=180, y=100)
        frame5_6.photo = tk.PhotoImage(file="icons/7255.png")
        label = tk.Label(frame5_6, image=frame5_6.photo)
        label.place(x=5, y=25)
        ToolTip(label, "迷仙引梦")
        text = "数量：%d(%.2f)\n" % (self.result["skill"]["mxym"]["num"], self.result["skill"]["mxym"]["numPerSec"])
        text = text + "HPS：%d\n" % self.result["skill"]["mxym"]["HPS"]
        text = text + "覆盖率：%s%%\n" % parseCent(self.result["skill"]["mxym"]["cover"])
        label = tk.Label(frame5_6, text=text, justify="left")
        label.place(x=60, y=20)

        frame5_7 = tk.Frame(frame5, width=180, height=95)
        frame5_7.place(x=360, y=100)
        text = "蝶旋HPS：%d\n" % self.result["skill"]["dx"]["HPS"]
        text = text + "蝶旋次数：%d(%.2f)\n" % (self.result["skill"]["dx"]["num"], self.result["skill"]["dx"]["numPerSec"])
        text = text + "沐风覆盖率：%s%%\n" % parseCent(self.result["skill"]["mufeng"]["cover"])
        text = text + "蛊惑覆盖率：%s%%\n" % parseCent(self.result["skill"]["ghzs"]["cover"])
        label = tk.Label(frame5_7, text=text, justify="left")
        label.place(x=20, y=15)

        frame5_8 = tk.Frame(frame5, width=180, height=95)
        frame5_8.place(x=540, y=100)
        text = "gcd效率：%s%%\n" % parseCent(self.result["skill"]["general"]["efficiency"])
        text = text + "战斗效率：%s%%\n" % parseCent(self.result["skill"]["general"]["efficiencyNonGcd"])
        label = tk.Label(frame5_8, text=text, justify="left")
        label.place(x=20, y=30)

        button = tk.Button(frame5, text='？', height=1, command=self.showHelp)
        button.place(x=680, y=160)

        # Part 6: 回放

        frame6 = tk.Frame(window, width=730, height=150, highlightthickness=1, highlightbackground="#3f1f9f")
        frame6.place(x=10, y=460)
        battleTime = self.result["overall"]["sumTime"]
        battleTimePixels = int(battleTime / 100)
        startTime = self.result["replay"]["startTime"]
        canvas6 = tk.Canvas(frame6, width=720, height=140, scrollregion=(0, 0, battleTimePixels, 120))  # 创建canvas
        canvas6.place(x=0, y=0) #放置canvas的位置
        frame6sub = tk.Frame(canvas6) #把frame放在canvas里
        frame6sub.place(width=720, height=120) #frame的长宽，和canvas差不多的
        vbar=tk.Scrollbar(canvas6, orient=tk.HORIZONTAL)
        vbar.place(y=120,width=720,height=20)
        vbar.configure(command=canvas6.xview)
        canvas6.config(xscrollcommand=vbar.set)
        canvas6.create_window((360, int(battleTimePixels/2)), window=frame6sub)

        # 加载图片列表
        canvas6.imDict = {}
        canvas6.im = {}
        imFile = os.listdir('icons')
        for line in imFile:
            imID = line.split('.')[0]
            if line.split('.')[1] == "png":
                canvas6.imDict[imID] = Image.open("icons/%s.png" % imID).resize((20, 20), Image.ANTIALIAS)
                canvas6.im[imID] = ImageTk.PhotoImage(canvas6.imDict[imID])

        # 绘制主时间轴及时间
        canvas6.create_rectangle(0, 30, battleTimePixels, 70, fill='white')
        # 迷仙引梦
        for i in range(1, len(self.result["replay"]["mxym"])):
            posStart = int((self.result["replay"]["mxym"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["mxym"][i][0] - startTime) / 100)
            # if posEnd - posStart < 3:
            #     posEnd = posStart + 3
            mxym = self.result["replay"]["mxym"][i-1][1]
            if mxym == 1:
                canvas6.create_rectangle(posStart, 31, posEnd, 40, fill="#cc3385", width=0)
        # 仙王蛊鼎
        for i in range(1, len(self.result["replay"]["xwgd"])):
            posStart = int((self.result["replay"]["xwgd"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["xwgd"][i][0] - startTime) / 100)
            xwgd = self.result["replay"]["xwgd"][i-1][1]
            if xwgd == 1:
                canvas6.create_rectangle(posStart, 41, posEnd, 50, fill="#4419b7", width=0)
        # 蛊惑众生
        for i in range(1, len(self.result["replay"]["ghzs"])):
            posStart = int((self.result["replay"]["ghzs"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["ghzs"][i][0] - startTime) / 100)
            ghzs = self.result["replay"]["ghzs"][i-1][1]
            if ghzs == 1:
                canvas6.create_rectangle(posStart, 51, posEnd, 60, fill="#ff58ee", width=0)
        # 醉舞九天
        for i in range(1, len(self.result["replay"]["zwjt"])):
            posStart = int((self.result["replay"]["zwjt"][i-1][0] - startTime) / 100)
            posStart = max(posStart, 1)
            posEnd = int((self.result["replay"]["zwjt"][i][0] - startTime) / 100)
            zwjt = self.result["replay"]["zwjt"][i-1][1]
            if zwjt == 1:
                canvas6.create_rectangle(posStart, 61, posEnd, 70, fill="#957ded", width=0)

        nowt = 0
        while nowt < battleTime:
            nowt += 10000
            text = parseTime(nowt / 1000)
            pos = int(nowt / 100)
            canvas6.create_text(pos, 50, text=text)
        # 绘制常规技能轴
        for record in self.result["replay"]["normal"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 80, image=canvas6.im[record["iconid"]])
            # 绘制表示持续的条
            if posStart + 20 < posEnd:
                canvas6.create_rectangle(posStart+20, 70, posEnd, 90, fill="#64fab4")
            # 绘制重复次数
            if posStart + 30 < posEnd and record["num"] > 1:
                canvas6.create_text(posStart+30, 80, text="*%d"%record["num"])

        # 绘制特殊技能轴
        for record in self.result["replay"]["special"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 100, image=canvas6.im[record["iconid"]])

        # 绘制点名轴
        for record in self.result["replay"]["call"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 100, image=canvas6.im[record["iconid"]])
            # 绘制表示持续的条
            if posStart + 20 < posEnd:
                canvas6.create_rectangle(posStart+20, 90, posEnd, 110, fill="#ff7777")
            # 绘制名称
            if posStart + 30 < posEnd:
                text = record["skillname"]
                canvas6.create_text(posStart+20, 100, text=text, anchor=tk.W)

        # 绘制环境轴
        for record in self.result["replay"]["environment"]:
            posStart = int((record["start"] - startTime) / 100)
            posEnd = int((record["start"] + record["duration"] - startTime) / 100)
            canvas6.create_image(posStart+10, 20, image=canvas6.im[record["iconid"]])
            # 绘制表示持续的条
            if posStart + 20 < posEnd:
                canvas6.create_rectangle(posStart+20, 10, posEnd, 30, fill="#ff7777")
            # 绘制名称
            if posStart + 30 < posEnd:
                text = record["skillname"]
                if record["num"] > 1:
                    text += "*%d"%record["num"]
                canvas6.create_text(posStart+20, 20, text=text, anchor=tk.W)

        tk.Label(frame6sub, text="test").place(x=20, y=20)

        # Part 7: 输出
        frame7 = tk.Frame(window, width=290, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame7.place(x=10, y=620)
        numDPS = self.result["dps"]["numDPS"]
        canvas = tk.Canvas(frame7,width=290,height=190,scrollregion=(0,0,270,numDPS*24)) #创建canvas
        canvas.place(x=0, y=0) #放置canvas的位置
        frame7sub = tk.Frame(canvas) #把frame放在canvas里
        frame7sub.place(width=270, height=190) #frame的长宽，和canvas差不多的
        vbar=tk.Scrollbar(canvas,orient=tk.VERTICAL) #竖直滚动条
        vbar.place(x=270,width=20,height=190)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set) #设置
        canvas.create_window((135,numDPS*12), window=frame7sub)  #create_window

        tb = TableConstructor(self.config, frame7sub)
        tb.AppendHeader("玩家名", "", width=13)
        tb.AppendHeader("DPS", "全程的DPS")
        tb.AppendHeader("吃锅次数", "无效的次数不会计算")
        tb.EndOfLine()
        for record in self.result["dps"]["table"]:
            name = self.getMaskName(record["name"])
            color = getColor(record["occ"])
            tb.AppendContext(name, color=color, width=13)
            tb.AppendContext(record["damage"])
            tb.AppendContext(record["xwgdNum"])
            tb.EndOfLine()

        # Part 8: 打分
        frame8 = tk.Frame(window, width=210, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame8.place(x=320, y=620)
        frame8sub = tk.Frame(frame8)
        frame8sub.place(x=30, y=30)

        if self.result["score"]["available"] == 10:
            tk.Label(frame8, text="复盘生成时的版本尚不支持打分。").place(x=10, y=150)
        # elif self.result["score"]["available"] == 1:
        #     tb = TableConstructor(self.config, frame8sub)
        #     tb.AppendHeader("数值分：", "对治疗数值的打分，包括治疗量、各个技能数量。")
        #     descA = "治疗量评分：%.1f\n盾数量评分：%.1f\n徵数量评分：%.1f\n宫数量评分：%.1f" % (self.result["score"]["scoreA1"], self.result["score"]["scoreA2"],
        #                                                        self.result["score"]["scoreA3"], self.result["score"]["scoreA4"])
        #     tb.AppendHeader(self.result["score"]["scoreA"], descA, width=9)
        #     lvlA, colorA, _ = self.getLvl(self.result["score"]["scoreA"])
        #     tb.AppendContext(lvlA, color=colorA)
        #     tb.EndOfLine()
        #     tb.AppendHeader("统计分：", "对统计结果的打分，包括梅花三弄和HOT的覆盖率。")
        #     descB = "盾覆盖率评分：%.1f\nHOT覆盖率评分：%.1f" % (self.result["score"]["scoreB1"], self.result["score"]["scoreB2"])
        #     tb.AppendHeader(self.result["score"]["scoreB"], descB, width=9)
        #     lvlB, colorB, _ = self.getLvl(self.result["score"]["scoreB"])
        #     tb.AppendContext(lvlB, color=colorB)
        #     tb.EndOfLine()
        #     tb.AppendHeader("操作分：", "对操作表现的打分，包括战斗效率，各个技能延迟。")
        #     descC = "战斗效率评分：%.1f\n盾延迟评分：%.1f\n徵延迟评分：%.1f\n宫延迟评分：%.1f" % (self.result["score"]["scoreC1"], self.result["score"]["scoreC2"],
        #                                                        self.result["score"]["scoreC3"], self.result["score"]["scoreC4"])
        #     tb.AppendHeader(self.result["score"]["scoreC"], descC, width=9)
        #     lvlC, colorC, _ = self.getLvl(self.result["score"]["scoreC"])
        #     tb.AppendContext(lvlC, color=colorC)
        #     tb.EndOfLine()
        #
        #     tb.AppendHeader("总评：", "综合计算这几项的结果。")
        #     tb.AppendContext(self.result["score"]["sum"], width=9)
        #     lvl, color, desc = self.getLvl(self.result["score"]["sum"])
        #     tb.AppendContext(lvl, color=color)
        #     tb.EndOfLine()
        #     tk.Label(frame8, text=desc, fg=color).place(x=10, y=150)

        # Part 9: 广告
        frame9 = tk.Frame(window, width=200, height=200, highlightthickness=1, highlightbackground="#3f1f9f")
        frame9.place(x=540, y=620)
        frame9sub = tk.Frame(frame9)
        frame9sub.place(x=0, y=0)

        tk.Label(frame9, text="科技&五奶群：418483739").place(x=20, y=20)
        tk.Label(frame9, text="奶毒PVE群：208732360").place(x=20, y=40)
        if "shortID" in self.result["overall"]:
            tk.Label(frame9, text="复盘编号：%s"%self.result["overall"]["shortID"]).place(x=20, y=70)
            b2 = tk.Button(frame9, text='在网页中打开', height=1, command=self.OpenInWeb)
            b2.place(x=40, y=90)

        # tk.Label(frame9, text="新建文件夹！").place(x=40, y=140)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def start(self):
        '''
        创建并展示窗口.
        '''
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()

    def alive(self):
        '''
        返回窗口是否仍生存.
        returns:
        - res: 布尔类型，窗口是否仍生存.
        '''
        return self.windowAlive

    def __init__(self, config, result):
        '''
        初始化.
        params:
        - result: 灵素复盘的结果.
        '''
        self.config = config
        self.mask = config.mask
        self.result = result

class BuTianJueReplayer(ReplayerBase):
    '''
    奶毒复盘类.
    分析战斗记录并生成json格式的结果，对结果的解析在其他类中完成。
    '''

    def FirstStageAnalysis(self):
        '''
        第一阶段复盘.
        主要处理全局信息，玩家列表等.
        '''

        # 除玩家名外，所有的全局信息都可以在第一阶段直接获得
        self.result["overall"] = {}
        self.result["overall"]["edition"] = "奶毒复盘 v%s"%EDITION
        self.result["overall"]["playerID"] = "未知"
        self.result["overall"]["server"] = self.bld.info.server
        self.result["overall"]["battleTime"] = self.bld.info.battleTime
        self.result["overall"]["battleTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        self.result["overall"]["generateTime"] = int(time.time())
        self.result["overall"]["generateTimePrint"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["generateTime"]))
        self.result["overall"]["map"] = self.bld.info.map
        self.result["overall"]["boss"] = getNickToBoss(self.bld.info.boss)
        self.result["overall"]["sumTime"] = self.bld.info.sumTime
        self.result["overall"]["sumTimePrint"] = parseTime(self.bld.info.sumTime / 1000)
        self.result["overall"]["dataType"] = self.bld.dataType
        self.result["overall"]["mask"] = self.config.mask

        # 需要记录特定治疗量的BOSS
        self.npcName = ""
        self.npcKey = 0
        for key in self.bld.info.npc:
            if self.bld.info.npc[key].name in ['"宓桃"', '"毗留博叉"'] or self.bld.info.npc[key].name == self.npcName:
                self.npcKey = key
                break

        # 记录盾的存在情况与减疗
        jianLiaoLog = {}

        # 记录战斗中断的时间，通常用于P2为垃圾时间的BOSS.
        self.interrupt = 0

        # 不知道有什么用
        self.activeBoss = ""

        # 记录战斗开始时间与结束时间
        if self.startTime == 0:
            self.startTime = self.bld.log[0].time
        if self.finalTime == 0:
            self.finalTime = self.bld.log[-1].time

        # 如果时间被大幅度修剪过，则修正战斗时间
        if abs(self.finalTime - self.startTime - self.result["overall"]["sumTime"]) > 6000:
            actualTime = self.finalTime - self.startTime
            self.result["overall"]["sumTime"] = actualTime
            self.result["overall"]["sumTimePrint"] = parseTime(actualTime / 1000)

        # 记录所有治疗的key，首先尝试直接使用心法列表获取.
        self.healerDict = {}
        XiangZhiList = []

        # 记录具体心法的表.
        occDetailList = {}
        for key in self.bld.info.player:
            occDetailList[key] = self.bld.info.player[key].occ

        self.peiwuCounter = {}
        for key in self.bld.info.player:
            self.peiwuCounter[key] = ShieldCounterNew("20877", self.startTime, self.finalTime)

        # 自动推导奶歌角色名与ID，在连接场景中会被指定，这一步可跳过
        if self.myname == "":
            raise Exception("角色名暂时不可自动推导，需要通过前序分析来手动指定")
        else:
            for key in self.bld.info.player:
                if self.bld.info.player[key].name == self.myname:
                    self.mykey = key

        for event in self.bld.log:

            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if self.interrupt != 0:
                continue

            if event.dataType == "Skill":
                # 记录治疗心法的出现情况.
                if event.caster not in self.healerDict and event.id in ["565", "554", "555", "2232", "6662", "2233", "6675",
                                                                  "2231", "101", "142", "138", "14231", "14140", "14301", "16852", "18864",
                                                                  "27621", "27623", "28083"]:  # 奶妈的特征技能
                    self.healerDict[event.caster] = 0

                if event.caster in occDetailList and occDetailList[event.caster] in ['1', '2', '3', '4', '5', '6', '7', '10',
                                                                           '21', '22', '212']:
                    occDetailList[event.caster] = checkOccDetailBySkill(occDetailList[event.caster], event.id, event.damageEff)

                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"宓桃"':
                    self.activeBoss = "宓桃"
                if event.target in self.bld.info.npc and self.bld.info.npc[event.target].name == '"毗留博叉"':
                    self.activeBoss = "哑头陀"

            elif event.dataType == "Buff":
                if event.id in ["20877"] and event.caster == self.mykey:  # buff配伍
                    self.peiwuCounter[event.target].setState(event.time, event.stack)
                if event.id in ["15774", "17200"]:  # buff精神匮乏
                    if event.target not in jianLiaoLog:
                        jianLiaoLog[event.target] = BuffCounter("17200", self.startTime, self.finalTime)
                    jianLiaoLog[event.target].setState(event.time, event.stack)
                if event.caster in occDetailList and occDetailList[event.caster] in ['21']:
                    occDetailList[event.caster] = checkOccDetailByBuff(occDetailList[event.caster], event.id)

            elif event.dataType == "Shout":
                # 为未来需要统计喊话时备用.
                pass

        if self.interrupt != 0:
            self.result["overall"]["sumTime"] -= (self.finalTime - self.interrupt)
            self.result["overall"]["sumTimePrint"] = parseTime(self.result["overall"]["sumTime"] / 1000)
            self.finalTime = self.interrupt

        # for key in self.bld.info.player:
        #     self.shieldCountersNew[key].inferFirst()

        self.result["overall"]["playerID"] = self.myname

        self.occDetailList = occDetailList

        # 获取到玩家信息，继续全局信息的推断
        self.result["overall"]["mykey"] = self.mykey
        self.result["overall"]["name"] = self.myname

        # 获取玩家装备和奇穴，即使获取失败也存档
        self.result["equip"] = {"available": 0}
        if self.bld.info.player[self.mykey].equip != {} and "beta" not in EDITION:
            self.result["equip"]["available"] = 1
            ea = EquipmentAnalyser()
            jsonEquip = ea.convert2(self.bld.info.player[self.mykey].equip, self.bld.info.player[self.mykey].equipScore)
            eee = ExcelExportEquipment()
            strEquip = eee.export(jsonEquip)
            adr = AttributeDisplayRemote()
            res = adr.Display(strEquip, "6h")
            self.result["equip"]["score"] = int(self.bld.info.player[self.mykey].equipScore)
            self.result["equip"]["sketch"] = jsonEquip["sketch"]
            self.result["equip"]["forge"] = jsonEquip["forge"]
            self.result["equip"]["spirit"] = res["根骨"]
            self.result["equip"]["heal"] = res["治疗"]
            self.result["equip"]["healBase"] = res["基础治疗"]
            self.result["equip"]["critPercent"] = res["会心"]
            self.result["equip"]["crit"] = res["会心等级"]
            self.result["equip"]["critpowPercent"] = res["会效"]
            self.result["equip"]["critpow"] = res["会效等级"]
            self.result["equip"]["hastePercent"] = res["加速"]
            self.result["equip"]["haste"] = res["加速等级"]
            if not self.config.xiangzhiSpeedForce:
                self.haste = self.result["equip"]["haste"]
            self.result["equip"]["raw"] = strEquip

        self.result["qixue"] = {"available": 0}
        if self.bld.info.player[self.mykey].qx != {}:
            self.result["qixue"]["available"] = 1
            for key in self.bld.info.player[self.mykey].qx:
                qxKey = "1,%s,1" % self.bld.info.player[self.mykey].qx[key]["2"]
                qxKey0 = "1,%s,0" % self.bld.info.player[self.mykey].qx[key]["2"]
                if qxKey in SKILL_NAME:
                    self.result["qixue"][key] = SKILL_NAME[qxKey]
                elif qxKey0 in SKILL_NAME:
                    self.result["qixue"][key] = SKILL_NAME[qxKey0]
                else:
                    self.result["qixue"][key] = self.bld.info.player[self.mykey].qx[key]["2"]

        # print(self.result["overall"])
        # print(self.result["equip"])
        # print(self.result["qixue"])

        # res = {}
        # for line in self.result["qixue"]:
        #     if line != "available":
        #         key = self.result["qixue"][line]
        #         value = SKILL_NAME["1,%s,1"%key]
        #         res[key] = value
        # print(res)

        self.result["overall"]["hasteReal"] = self.haste

        return 0

    def SecondStageAnalysis(self):
        '''
        第二阶段复盘.
        主要处理技能统计，战斗细节等.
        '''

        occDetailList = self.occDetailList

        num = 0

        # 以承疗者记录的关键治疗
        self.criticalHealCounter = {}
        hpsActive = 0

        # 以治疗者记录的关键治疗
        if self.activeBoss in ["宓桃", "哑头陀"]:
            hpsActive = 0
            hpsTime = 0
            hpsSumTime = 0
            numSmall = 0

        numHeal = 0
        numEffHeal = 0
        npcHealStat = {}
        numPurge = 0  # 驱散次数
        battleStat = {}  # 伤害占比统计，[无盾伤害，有盾伤害，桑柔伤害，玉简伤害]
        damageDict = {}  # 伤害统计
        healStat = {}  # 治疗统计
        myHealRank = 0  # 个人治疗量排名
        numHealer = 0  # 治疗数量
        battleTimeDict = {}  # 进战时间
        sumPlayer = 0  # 玩家数量

        xwgdNumDict = {}  # 仙王蛊鼎触发次数
        firstXwgd = 0
        firstXwgdTaketime = 0

        # 技能统计
        dxSkill = SkillHealCounter("3051", self.startTime, self.finalTime, self.haste)  # 蝶旋
        dcSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 蝶池
        bcqsSkill = SkillHealCounter("2232", self.startTime, self.finalTime, self.haste)  # 冰蚕牵丝
        zwjtSkill = SkillHealCounter("6252", self.startTime, self.finalTime, self.haste)  # 醉舞九天
        ssztSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 圣手织天
        qdtrSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 千蝶吐瑞
        mxymSkill = SkillHealCounter("?", self.startTime, self.finalTime, self.haste)  # 迷仙引梦

        zwjtDict = BuffCounter("?", self.startTime, self.finalTime)  # 用buff类型来记录醉舞九天的具体时间
        mxymDict = BuffCounter("?", self.startTime, self.finalTime)  # 迷仙引梦记录
        xwgdDict = BuffCounter("?", self.startTime, self.finalTime)  # 锅记录
        ghzsDict = BuffCounter("?", self.startTime, self.finalTime)  # 蛊惑记录

        cyDict = BuffCounter("2844", self.startTime, self.finalTime)  # 蚕引
        cwDict = BuffCounter("12770", self.startTime, self.finalTime)  # cw特效
        mufengDict = BuffCounter("412", self.startTime, self.finalTime)  # 沐风

        battleDict = {}
        firstHitDict = {}

        for line in self.bld.info.player:
            battleDict[line] = BuffCounter("0", self.startTime, self.finalTime)  # 战斗状态统计
            firstHitDict[line] = 0
            battleStat[line] = [0]
            xwgdNumDict[line] = 0

        lastSkillTime = self.startTime

        # 杂项
        wuhuoHeal = 0  # 无惑
        xjmjHeal = 0  # 献祭秘籍
        bdxjHeal = 0  # 碧蝶献祭

        # 战斗回放初始化
        bh = BattleHistory(self.startTime, self.finalTime)
        ss = SingleSkill(self.startTime, self.haste)

        # 技能信息
        # [技能统计对象, 技能名, [所有技能ID], 图标ID, 是否为gcd技能, 运功时长, 是否倒读条, 是否吃加速]
        skillInfo = [[None, "未知", ["0"], "0", True, 0, False, True],
                     [None, "扶摇直上", ["9002"], "1485", True, 0, False, True],
                     [None, "蹑云逐月", ["9003"], "1490", True, 0, False, True],

                     [bcqsSkill, "冰蚕牵丝", ["2232", "2526", "27391", "6662"], "2745", True, 24, False, True],
                     [ssztSkill, "圣手织天", ["13425", "13426"], "3028", True, 0, False, True],
                     [qdtrSkill, "千蝶吐瑞", ["2449"], "2748", True, 8, True, True],
                     [None, "迷仙引梦", ["15132"], "7255", True, 8, False, True],
                     [None, "仙王蛊鼎", ["2234"], "2747", True, 24, False, True],
                     [None, "玄水蛊", ["3702"], "3038", True, 0, False, True],
                     [None, "圣元阵", ["25058"], "13447", True, 0, False, True],
                     [None, "蛊惑众生", ["2231"], "2744", True, 0, False, True],
                     [None, "碧蝶引", ["2965"], "3025", True, 0, False, True],

                     # [None, "醉舞九天", ["6252"], "2746", False, 16, True, True],
                     [None, "化蝶", ["2228"], "2830", False, 0, False, True],
                     [None, "蛊虫献祭", ["2226"], "2762", False, 0, False, True],
                     [None, "蝶鸾", ["3054"], "2764", False, 0, False, True],
                     [None, "女娲补天", ["2230"], "2743", False, 0, False, True],
                     [None, "灵蛊", ["18584"], "2777", False, 0, False, True],
                    ]

        zwjtTime = getLength(16, self.haste)

        gcdSkillIndex = {}
        nonGcdSkillIndex = {}
        for i in range(len(skillInfo)):
            line = skillInfo[i]
            for id in line[2]:
                if line[4]:
                    gcdSkillIndex[id] = i
                else:
                    nonGcdSkillIndex[id] = i

        xiangZhiUnimportant = ["4877", "15054", "15057",  # 水特效作用，盾奇穴效果
                               "25683", "24787",  # 破招
                               "22155", "22207",  # 大附魔
                               "3071", "18274", "14646",  # 治疗套装，寒清，书离
                               "23951", #  贯体通用
                               "14536", "14537", # 盾填充, 盾移除
                               "3584", "2448",  # 蛊惑
                               "604", # 春泥
                               "4697", "13237", # 队友阵眼
                               "6800", # 风？
                               "13332", # 锋凌横绝阵
                               "22211",  # 治疗衣服大附魔
                               "9007",  # 后跳 (TODO) 统计各种后跳
                               "9004", "9005", "9006",  # 左右小轻功
                               "29532", "29541",  # 飘黄
                               "14427", "14426",  # 浮生清脉阵
                               ## 奶毒分割线
                               "3051", "3644", "3473" # 蝶旋
                               "2957",  # 圣手织天壳
                               "2233", "6252",  # 醉舞 TODO 统计醉舞！
                               "15134",  # 迷仙引梦
                               "2998",  # 无惑
                               "2968",  # 打断成功
                               "18590",  # 打断伤害
                               "25686", "24790",  # 破招
                               "26771",  # 献祭少量治疗
                               "3023",  # 献祭解控
                               "3061",  # 碧蝶献祭治疗
                               "18884",  # 蝶池治疗
                               "2235",  # 千蝶壳
                               "2978",  # 招宠物判断技能
                               ]

        for event in self.bld.log:
            if event.time < self.startTime:
                continue
            if event.time > self.finalTime:
                continue

            if event.dataType == "Skill":
                # 统计化解(暂时只能统计jx3dat的，因为jcl里压根没有)
                if event.effect == 7:
                    # numAbsorb1 += event.healEff
                    pass
                else:
                    # 所有治疗技能都不计算化解.
                    # 统计自身治疗
                    if event.caster == self.mykey and event.heal != 0:
                        numHeal += event.heal
                        numEffHeal += event.healEff

                    # 统计团队治疗
                    if event.heal + event.healEff > 0 and event.effect != 7 and event.caster in self.healerDict:
                        if event.caster not in healStat:
                            healStat[event.caster] = [0, 0]
                        healStat[event.caster][0] += event.healEff
                        healStat[event.caster][1] += event.heal

                    # 统计自身技能使用情况.
                    # if event.caster == self.mykey and event.scheme == 1 and event.id in xiangZhiUnimportant and event.heal != 0:
                    #     print(event.id, event.time)

                    if event.scheme == 1 and event.heal != 0 and event.caster == self.mykey and event.id not in gcdSkillIndex and event.id not in xiangZhiUnimportant:
                        # 打印所有有治疗量的技能，以进行整理
                        # print("[Heal]", event.id, event.heal)
                        pass

                    if event.caster == self.mykey and event.scheme == 1 and event.id not in xiangZhiUnimportant:  # 影子宫、桑柔等需要过滤的技能
                        # skillLog.append([event.time, event.id])

                        # 若技能没有连续，则在战斗回放中记录技能
                        if ((event.id not in gcdSkillIndex or gcdSkillIndex[event.id] != gcdSkillIndex[ss.skill]) and event.id not in nonGcdSkillIndex)\
                          or event.time - ss.timeEnd > 3000:
                            # 记录本次技能
                            # print("[ReplaceSkill]", event.id, ss.skill)
                            # 此处的逻辑完全可以去掉，保留这个逻辑就是为了监控哪些是值得挖掘的隐藏技能
                            if ss.skill != "0":
                                index = gcdSkillIndex[ss.skill]
                                line = skillInfo[index]
                                bh.setNormalSkill(ss.skill, line[1], line[3],
                                                  ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                                                  roundCent(ss.healEff / (ss.heal + 1e-10)),
                                                  int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")
                            ss.reset()
                        # if ss.num == 1:
                        #     # 记录一个快照
                        #     ss2 = copy.copy(ss)
                        # 根据技能表进行自动处理
                        if event.id in gcdSkillIndex:
                            if ss.skill == "0":
                                ss.initSkill(event)
                            index = gcdSkillIndex[event.id]
                            line = skillInfo[index]
                            castTime = line[5]
                            if event.id in ["2232", "2526", "27391", "6662"]:
                                # 检查冰蚕诀
                                sf = cyDict.checkState(event.time - 200)
                                if sf:
                                    castTime = 0
                            ss.analyseSkill(event, castTime, line[0], tunnel=line[6], hasteAffected=line[7])
                        elif event.id in nonGcdSkillIndex:  # 特殊技能
                            desc = ""
                            index = nonGcdSkillIndex[event.id]
                            line = skillInfo[index]
                            bh.setSpecialSkill(event.id, line[1], line[3], event.time, 0, desc)
                        else:
                            pass

                    if event.caster == self.mykey and event.scheme == 1:
                        # 统计不计入时间轴的治疗量
                        if event.id in ["3051", "3473"]:  # 蝶旋
                            dxSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        if event.id in ["15134"]:  # 迷仙引梦
                            mxymSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                            if event.time - mxymDict.log[-1][0] > 200:
                                mxymDict.setState(event.time - 2000, 1)
                                mxymDict.setState(event.time, 0)
                        if event.id in ["18884"]:  # 蝶池
                            dcSkill.recordSkill(event.time, event.heal, event.healEff, event.time)
                        if event.id in ["2998"]:  # 无惑
                            wuhuoHeal += event.healEff
                        if event.id in ["26771"]:  # 献祭秘籍
                            xjmjHeal += event.healEff
                        if event.id in ["3061"]:  # 碧蝶献祭
                            bdxjHeal += event.healEff
                        if event.id in ["6252"]:  # 醉舞九天
                            zwjtSkill.recordSkill(event.time, event.heal, event.healEff, 0)
                            # 醉舞也计入战斗效率中
                            if event.time - zwjtDict.log[-1][0] > 200:
                                zwjtDict.setState(event.time - zwjtTime, 1)
                                zwjtDict.setState(event.time, 0)
                        if event.id in ["2234"]:  # 仙王蛊鼎
                            if firstXwgd == 0:
                                firstXwgd = 1
                                if firstXwgdTaketime != 0:
                                    xwgdDict.setState(self.startTime, 1)
                                    xwgdDict.setState(firstXwgdTaketime, 0)
                            xwgdDict.setState(event.time, 1)
                            xwgdDict.setState(event.time + 60000, 0)
                        if event.id in ["23951"] and event.level == 51:
                            xwgdNumDict[event.target] += 1
                            if firstXwgd == 0:
                                firstXwgdTaketime = event.time


                    # if event.caster == self.mykey and event.scheme == 2:
                    #     if event.id in ["631"]:  # 握针
                    #         wozhenBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)
                    #     if event.id in ["5693"]:  # 述怀
                    #         shuhuaiBuff.recordSkill(event.time, event.heal, event.healEff, lastSkillTime)

                    # 统计对NPC的治疗情况.
                    if event.healEff > 0 and event.target == self.npcKey:
                        if event.caster not in npcHealStat:
                            npcHealStat[event.caster] = 0
                        npcHealStat[event.caster] += event.healEff

                    # 统计以承疗者计算的关键治疗
                    if event.healEff > 0 and self.npcKey != 0:
                        if event.target in self.criticalHealCounter and self.criticalHealCounter[event.target].checkState(event.time):
                            if event.caster not in npcHealStat:
                                npcHealStat[event.caster] = event.healEff
                            else:
                                npcHealStat[event.caster] += event.healEff

                    # 统计以治疗者计算的关键治疗
                    if self.activeBoss in ["宓桃", "哑头陀"]:
                        if event.healEff > 0 and self.npcKey != 0 and hpsActive:
                            if event.caster not in npcHealStat:
                                npcHealStat[event.caster] = 0
                            npcHealStat[event.caster] += event.healEff

                # 统计伤害技能
                if event.damageEff > 0 and event.id not in ["24710", "24730", "25426", "25445"]:  # 技能黑名单
                    if event.caster in self.peiwuCounter:
                        # if event.caster not in battleStat:
                        #     battleStat[event.caster] = [0]  # 伤害
                        battleStat[event.caster][0] += event.damageEff

                # 根据战斗信息推测进战状态
                if event.caster in self.bld.info.player and firstHitDict[event.caster] == 0 and (event.damageEff > 0 or event.healEff > 0):
                    firstHitDict[event.caster] = 1
                    if event.scheme == 1:
                        battleDict[event.caster].setState(event.time, 1)

            elif event.dataType == "Buff":
                if event.id == "需要处理的buff！现在还没有":
                    if event.target not in self.criticalHealCounter:
                        self.criticalHealCounter[event.target] = BuffCounter("buffID", self.startTime, self.finalTime)
                    self.criticalHealCounter[event.target].setState(event.time, event.stack)
                if event.id in ["6360"] and event.level in [66, 76, 86] and event.stack == 1:  # 特效腰坠:
                    bh.setSpecialSkill(event.id, "特效腰坠", "3414",
                                       event.time, 0, "开启特效腰坠")
                if event.id in ["12770"] and event.stack == 1:  # cw特效: TODO 奶毒
                    bh.setSpecialSkill(event.id, "cw特效", "14404",
                                       event.time, 0, "触发cw特效")
                    cwDict.setState(event.time, event.stack)
                if event.id in ["3067"] and event.target == self.mykey:  # 沐风
                    mufengDict.setState(event.time, event.stack)
                if event.id in ["2316"] and event.caster == self.mykey:  # 蛊惑
                    ghzsDict.setState(event.time, event.stack)
                if event.id in ["2844"] and event.target == self.mykey:  # 蚕引
                    cyDict.setState(event.time, event.stack)

            elif event.dataType == "Shout":
                pass

            elif event.dataType == "Death":
                pass

            elif event.dataType == "Battle":
                if event.id in self.bld.info.player:
                    battleDict[event.id].setState(event.time, event.fight)

            num += 1

        # 记录最后一个技能
        if ss.skill != "0":
            index = gcdSkillIndex[ss.skill]
            line = skillInfo[index]
            bh.setNormalSkill(ss.skill, line[1], line[3],
                              ss.timeStart, ss.timeEnd - ss.timeStart, ss.num, ss.heal,
                              roundCent(ss.healEff / (ss.heal + 1e-10)),
                              int(ss.delay / (ss.delayNum + 1e-10)), ss.busy, "")

        # 同步BOSS的技能信息
        if self.bossBh is not None:
            bh.log["environment"] = self.bossBh.log["environment"]
            bh.log["call"] = self.bossBh.log["call"]

        if hpsActive:
            hpsSumTime += (self.finalTime - int(hpsTime)) / 1000

        # 计算伤害
        for key in battleStat:
            line = battleStat[key]
            damageDict[key] = line[0]

        # 关键治疗量统计
        if self.activeBoss in ["宓桃", "哑头陀"]:
            for line in npcHealStat:
                npcHealStat[line] /= (hpsSumTime + 1e-10)

        # 计算团队治疗区(Part 3)
        self.result["healer"] = {"table": [], "numHealer": 0}
        healList = dictToPairs(healStat)
        healList.sort(key=lambda x: -x[1][0])

        sumHeal = 0
        numid = 0
        topHeal = 0
        for line in healList:
            if numid == 0:
                topHeal = line[1][0]
            sumHeal += line[1][0]
            numid += 1
            if line[0] == self.mykey and myHealRank == 0:
                myHealRank = numid
            # 当前逻辑为治疗量大于第一的20%才被记为治疗，否则为老板
            if line[1][0] > topHeal * 0.2:
                numHealer += 1
        if myHealRank > numHealer:
            numHealer = myHealRank
        self.result["healer"]["numHealer"] = numHealer
        for line in healList:
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "healEff": int(line[1][0] / self.result["overall"]["sumTime"] * 1000),
                   "heal": int(line[1][1] / self.result["overall"]["sumTime"] * 1000)}
            self.result["healer"]["table"].append(res)

        # 计算DPS列表(Part 7)
        self.result["dps"] = {"table": [], "numDPS": 0}

        damageList = dictToPairs(damageDict)
        damageList.sort(key=lambda x: -x[1])

        # 计算DPS的盾指标
        for key in self.peiwuCounter:
            liveCount = battleDict[key].buffTimeIntegral()  # 存活时间比例
            if battleDict[key].sumTime() - liveCount < 8000:  # 脱战缓冲时间
                liveCount = battleDict[key].sumTime()
            battleTimeDict[key] = liveCount
            sumPlayer += liveCount / battleDict[key].sumTime()

        for line in damageList:
            self.result["dps"]["numDPS"] += 1
            res = {"name": self.bld.info.player[line[0]].name,
                   "occ": self.bld.info.player[line[0]].occ,
                   "damage": int(line[1] / self.result["overall"]["sumTime"] * 1000),
                   "xwgdNum": xwgdNumDict[line[0]],
                   }
            self.result["dps"]["table"].append(res)

        mxymDict.shrink(100)
        ghzsDict.shrink(100)
        zwjtDict.shrink(100)

        # 计算技能统计
        self.result["overall"]["numPlayer"] = int(sumPlayer * 100) / 100

        self.result["skill"] = {}
        # 冰蚕牵丝
        self.result["skill"]["bcqs"] = {}
        self.result["skill"]["bcqs"]["num"] = bcqsSkill.getNum()
        self.result["skill"]["bcqs"]["numPerSec"] = roundCent(
            self.result["skill"]["bcqs"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["bcqs"]["delay"] = int(bcqsSkill.getAverageDelay())
        effHeal = bcqsSkill.getHealEff()
        self.result["skill"]["bcqs"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["bcqs"]["effRate"] = effHeal / (bcqsSkill.getHeal() + 1e-10)
        # 醉舞九天
        self.result["skill"]["zwjt"] = {}
        self.result["skill"]["zwjt"]["num"] = zwjtSkill.getNum()
        self.result["skill"]["zwjt"]["numPerSec"] = roundCent(
            self.result["skill"]["zwjt"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["zwjt"]["delay"] = int(zwjtSkill.getAverageDelay())
        effHeal = zwjtSkill.getHealEff()
        self.result["skill"]["zwjt"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["zwjt"]["effRate"] = effHeal / (zwjtSkill.getHeal() + 1e-10)
        # 圣手织天
        self.result["skill"]["sszt"] = {}
        self.result["skill"]["sszt"]["num"] = ssztSkill.getNum()
        self.result["skill"]["sszt"]["numPerSec"] = roundCent(
            self.result["skill"]["sszt"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["sszt"]["delay"] = int(ssztSkill.getAverageDelay())
        effHeal = ssztSkill.getHealEff()
        self.result["skill"]["sszt"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["sszt"]["effRate"] = effHeal / (ssztSkill.getHeal() + 1e-10)
        # 千蝶吐瑞
        self.result["skill"]["qdtr"] = {}
        self.result["skill"]["qdtr"]["num"] = qdtrSkill.getNum()
        self.result["skill"]["qdtr"]["numPerSec"] = roundCent(
            self.result["skill"]["qdtr"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        self.result["skill"]["qdtr"]["delay"] = int(qdtrSkill.getAverageDelay())
        effHeal = qdtrSkill.getHealEff()
        self.result["skill"]["qdtr"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["qdtr"]["effRate"] = effHeal / (qdtrSkill.getHeal() + 1e-10)
        # 蝶池
        self.result["skill"]["dc"] = {}
        self.result["skill"]["dc"]["num"] = dcSkill.getNum()
        self.result["skill"]["dc"]["numPerSec"] = roundCent(
            self.result["skill"]["dc"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = dcSkill.getHealEff()
        self.result["skill"]["dc"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["dc"]["effRate"] = effHeal / (dcSkill.getHeal() + 1e-10)
        # 迷仙引梦
        self.result["skill"]["mxym"] = {}
        self.result["skill"]["mxym"]["num"] = mxymSkill.getNum()
        self.result["skill"]["mxym"]["numPerSec"] = roundCent(
            self.result["skill"]["mxym"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = mxymSkill.getHealEff()
        self.result["skill"]["mxym"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["mxym"]["effRate"] = effHeal / (mxymSkill.getHeal() + 1e-10)
        num = battleTimeDict[self.mykey]
        sum = mxymDict.buffTimeIntegral()
        self.result["skill"]["mxym"]["cover"] = roundCent(sum / (num + 1e-10))
        # 蝶旋
        self.result["skill"]["dx"] = {}
        self.result["skill"]["dx"]["num"] = dxSkill.getNum()
        self.result["skill"]["dx"]["numPerSec"] = roundCent(
            self.result["skill"]["dx"]["num"] / self.result["overall"]["sumTime"] * 1000, 2)
        effHeal = dxSkill.getHealEff()
        self.result["skill"]["dx"]["HPS"] = int(effHeal / self.result["overall"]["sumTime"] * 1000)
        self.result["skill"]["dx"]["effRate"] = effHeal / (dxSkill.getHeal() + 1e-10)
        # 杂项
        self.result["skill"]["mufeng"] = {}
        num = battleTimeDict[self.mykey]
        sum = mufengDict.buffTimeIntegral()
        self.result["skill"]["mufeng"]["cover"] = roundCent(sum / (num + 1e-10))
        self.result["skill"]["ghzs"] = {}
        num = battleTimeDict[self.mykey]
        sum = ghzsDict.buffTimeIntegral()
        self.result["skill"]["ghzs"]["cover"] = roundCent(sum / (num + 1e-10))
        # 整体
        self.result["skill"]["general"] = {}
        # self.result["skill"]["general"]["HanQingNum"] = numHanQing
        self.result["skill"]["general"]["efficiency"] = bh.getNormalEfficiency()
        self.result["skill"]["general"]["efficiencyNonGcd"] = bh.getNonGcdEfficiency(zwjtDict.log)
        # 计算战斗回放
        self.result["replay"] = bh.getJsonReplay(self.mykey)
        self.result["replay"]["mxym"] = mxymDict.log
        self.result["replay"]["xwgd"] = xwgdDict.log
        self.result["replay"]["ghzs"] = ghzsDict.log
        self.result["replay"]["zwjt"] = zwjtDict.log

        # self.result["replay"]["heat"] = {"interval": 500, "timeline": hotHeat}

        # print(self.result["healer"])
        # print(self.result["dps"])
        # for line in self.result["skill"]:
        #     print(line, self.result["skill"][line])
        # for line in self.result["replay"]["normal"]:
        #     print(line)
        # print("===")
        # for line in self.result["replay"]["special"]:
        #     print(line)

    def recordRater(self):
        '''
        实现打分. 由于此处是单BOSS，因此打分直接由类内进行，不再整体打分。
        '''
        self.result["score"] = {"available": 10, "sum": 0}

    def getHash(self):
        '''
        获取战斗结果的哈希值.
        '''
        hashStr = ""
        nameList = []
        for key in self.bld.info.player:
            nameList.append(self.bld.info.player[key].name)
        nameList.sort()
        battleMinute = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.result["overall"]["battleTime"]))
        hashStr = battleMinute + self.result["overall"]["map"] + "".join(nameList) + self.result["overall"]["edition"]
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self):
        '''
        准备上传复盘结果，并向服务器上传.
        '''
        if "beta" in EDITION:
            return
        upload = {}
        upload["server"] = self.result["overall"]["server"]
        upload["id"] = self.result["overall"]["playerID"]
        upload["occ"] = "lingsu"
        upload["score"] = self.result["score"]["sum"]
        upload["battledate"] = time.strftime("%Y-%m-%d", time.localtime(self.result["overall"]["battleTime"]))
        upload["mapdetail"] = self.result["overall"]["map"]
        upload["boss"] = self.result["overall"]["boss"]
        upload["statistics"] = self.result
        upload["public"] = self.xiangzhiPublic
        upload["edition"] = EDITION
        upload["editionfull"] = parseEdition(EDITION)
        upload["replayedition"] = self.result["overall"]["edition"]
        upload["userid"] = self.config.items_user["uuid"]
        upload["battletime"] = self.result["overall"]["battleTime"]
        upload["submittime"] = int(time.time())
        upload["hash"] = self.getHash()

        Jdata = json.dumps(upload)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        # print(jparse)
        resp = urllib.request.urlopen('http://139.199.102.41:8009/uploadReplayPro', data=jparse)
        res = json.load(resp)
        # print(res)
        if res["result"] != "fail":
            self.result["overall"]["shortID"] = res["shortID"]
        else:
            self.result["overall"]["shortID"] = "数据保存出错"
        return res

    def replay(self):
        '''
        开始灵素复盘分析.
        '''
        self.FirstStageAnalysis()
        self.SecondStageAnalysis()
        self.recordRater()
        self.prepareUpload()

    def __init__(self, config, fileNameInfo, path="", bldDict={}, window=None, myname="", bossBh=None, startTime=0, finalTime=0, win=0):
        '''
        初始化.
        params:
        - config: 设置类.
        - fileNameInfo: 需要复盘的文件名.
        - path: 路径.
        - bldDict: 战斗数据缓存.
        - window: 主窗口，用于显示进度条.
        - myname: 需要复盘的奶歌名.
        - bossBh: BOSS施放的技能列表类，用于生成时间轴.
        - startTime: 演员复盘推断得到的战斗开始时间.
        - finalTime: 演员复盘推断得到的战斗结束时间.
        '''
        #self.win = 0
        super().__init__(config, fileNameInfo, path, bldDict, window)

        self.myname = myname
        self.bossBh = bossBh
        self.failThreshold = config.failThreshold
        self.mask = config.mask
        self.xiangzhiPublic = config.xiangzhiPublic
        self.config = config
        #self.filePath = path + '\\' + fileNameInfo[0]
        self.bld = bldDict[fileNameInfo[0]]
        self.startTime = startTime
        self.finalTime = finalTime

        self.result = {}
        self.haste = config.speed


