# Created by moeheart at 10/24/2020
# 由BOSS名称的各种变化形式到BOSS的对应方法，以及其它相关功能。
# 本文件废弃，其功能转移到tools.Names中.
    
BOSS_RAW = {"铁黎": [1, 1, []], 
            "陈徽": [1, 2, []],
            "藤原武裔": [1, 3, []],
            "源思弦": [1, 4, ["咒飚狐", "咒凌狐", "咒狐"]],
            "驺吾": [1, 5, []],
            "方有崖": [1, 6, []],
            "周贽": [2, 1, ["狼牙精锐", "狼牙刀盾兵"]],
            "厌夜": [2, 2, []],
            "迟驻": [2, 3, []],
            "白某": [2, 4, ["少阴符灵", "少阳符灵"]],
            "安小逢": [2, 5, ["狼牙斧卫", "水鬼"]],
            "余晖": [3, 1, []],
            "宓桃": [3, 2, ["天欲宫弟子", "天欲宫男宠"]],
            "武雪散": [3, 3, []],
            "猿飞": [3, 4, []],
            "哑头陀": [3, 5, ["毗流驮迦", "毗留博叉", "充能核心", "提多罗吒", "毗沙门"]],
            "岳琳&岳琅": [3, 6, ["岳琳", "岳琅", "蜂群毛贼", "蜂群蟊贼", "蜂群凶贼", "蜂群胖墩"]],
            "胡汤&罗芬": [4, 1, ["胡汤", "罗芬"]],
            "赵八嫂": [4, 2, []],
            "海荼": [4, 3, ["天怒惊霆戟", "水鬼"]],
            "姜集苦": [4, 4, []],
            "宇文灭": [4, 5, []],
            "宫威": [4, 6, []],
            "宫傲": [4, 7, []],
            "修罗僧": [5, 7, []],
            "巨型尖吻凤": [6, 1, []],
            "桑乔": [6, 2, []],
            "悉达罗摩": [6, 3, ["蛊兽"]],
            "尤珈罗摩": [6, 4, ["赐恩血瘤", "血蛊巢心"]],
            "月泉淮": [6, 5, []],
            "乌蒙贵": [6, 6, ["黑条巨蛾"]],
            }
            
MAP_NAME_LIST = ["未知地图", "敖龙岛", "范阳夜变", "达摩洞", "白帝江关", "修罗挑战", "雷域大泽"]
            
BOSS_DICT = {}
MAP_DICT = {}
NICK_TO_BOSS = {}

for line in BOSS_RAW:
    MAP_DICT[line] = BOSS_RAW[line][0]
    BOSS_DICT[line] = BOSS_RAW[line][1]
    NICK_TO_BOSS[line] = line
    for otherName in BOSS_RAW[line][2]:
        MAP_DICT[otherName] = BOSS_RAW[line][0]
        BOSS_DICT[otherName] = BOSS_RAW[line][1]
        NICK_TO_BOSS[otherName] = line
        
def getBossDictFromMap(map):
    if map == "敖龙岛":
        bossDict = {"铁黎": 1, "陈徽": 2, "藤原武裔": 3, "源思弦": 4, "驺吾": 5, "方有崖": 6}
        bossDictR = ["", "铁黎", "陈徽", "藤原武裔", "源思弦", "驺吾", "方有崖"]
    elif map == "范阳夜变":
        bossDict = {"周贽": 1, "厌夜": 2, "迟驻": 3, "白某": 4, "安小逢": 5}
        bossDictR = ["", "周贽", "厌夜", "迟驻", "白某", "安小逢"]
    elif map == "达摩洞":
        bossDict = {"余晖": 1, "宓桃": 2, "武雪散": 3, "猿飞": 4, "哑头陀": 5, "岳琳&岳琅": 6}
        bossDictR = ["", "余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅"]
    elif map == "白帝江关":
        bossDict = {"胡汤&罗芬": 1, "赵八嫂": 2, "海荼": 3, "姜集苦": 4, "宇文灭": 5, "宫威": 6, "宫傲": 7}
        bossDictR = ["", "胡汤&罗芬", "赵八嫂", "海荼", "姜集苦", "宇文灭", "宫威", "宫傲"]
    elif map == "雷域大泽":
        bossDict = {"巨型尖吻凤": 1, "桑乔": 2, "悉达罗摩": 3, "尤珈罗摩": 4, "月泉淮": 5, "乌蒙贵": 6}
        bossDictR = ["", "巨型尖吻凤", "桑乔", "悉达罗摩", "尤珈罗摩", "月泉淮", "乌蒙贵"]
    elif map == "修罗挑战":
        bossDict = {"修罗僧": 1}
        bossDictR = ["", "修罗僧"]
    else:
        bossDict = {}
        bossDictR = [""]
    return bossDict, bossDictR
    
def getNickToBoss(nick):

    #TODO 修复与更新
    if nick in NICK_TO_BOSS:
        return NICK_TO_BOSS[nick]
    else:
        return nick

def getMap(self):
    mapid = self.rawdata['20'][0]
    if mapid == "428":
        self.mapDetail = "25人英雄敖龙岛"
    elif mapid == "427":
        self.mapDetail = "25人普通敖龙岛"
    elif mapid == "426":
        self.mapDetail = "10人普通敖龙岛"
    elif mapid == "454":
        self.mapDetail = "25人英雄范阳夜变"
    elif mapid == "453":
        self.mapDetail = "25人普通范阳夜变"
    elif mapid == "452":
        self.mapDetail = "10人普通范阳夜变"
    elif mapid == "484":
        self.mapDetail = "25人英雄达摩洞"
    elif mapid == "483":
        self.mapDetail = "25人普通达摩洞"
    elif mapid == "482":
        self.mapDetail = "10人普通达摩洞"
    elif mapid == "520":
        self.mapDetail = "25人英雄白帝江关"
    elif mapid == "519":
        self.mapDetail = "25人普通白帝江关"
    elif mapid == "518":
        self.mapDetail = "10人普通白帝江关"
    elif mapid == "520":
        self.mapDetail = "25人英雄白帝江关"
    elif mapid == "519":
        self.mapDetail = "25人普通白帝江关"
    elif mapid == "518":
        self.mapDetail = "10人普通白帝江关"
    else:
        self.mapDetail = "未知"



