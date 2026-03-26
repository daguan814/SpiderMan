#  -*- coding: UTF-8 -*-

# MindPlus
# Python
from helloFly import fly 
from Service.print_map import print_map

"""
所有方法前面的第一个参数都是飞机机号
"""

# ================= 参数 =================
start = 0 # 定义起飞点

fh = fly()
print("按下k2起飞！")
while not (fh.getKeyPress(2)):  # 等待按下k2按键
	fh.sleep(0.01)
fh.ledCtrl(0,0,[0,255,0]) # 亮绿灯
fh.takeOff(0,100) # 起飞100cm
"""
方向：1-向前，2-向后，3-向左，4-向右
"""
if start == 0: # 在0号起飞点起飞
    direction1, point1 = 1, 40  # 向前, 到40
    direction2, point2 = 4, 42  # 向右，到42

elif start == 1: # 在1号起飞点起飞
    direction1, point1 = 2, 100  # 向后, 到100
    direction2, point2 = 4, 102  # 向右，到102

elif start == 2: # 在2号起飞点起飞
    direction1, point1 = 2, 107  # 向后, 到107
    direction2, point2 = 3, 105  # 向左，到105

elif start == 3: # 在3号起飞点起飞
    direction1, point1 = 1, 47  # 向前, 到47
    direction2, point2 = 3, 45  # 向左，到45

fh.moveSearchTag(0,direction1,100,point1) # 执行路线1
fh.moveSearchTag(0,direction2,100,point2) # 执行路线2

fh.flyHigh(0,200) # 高度升到200cm
fh.photographMode(0,1) # 拍照
while not (fh.photoOk()):
	fh.sleep(0.01)
fh.ledCtrl(0,0,[255,0,0])  # 亮红灯
fh.flyCtrl(0,0)   # 降落

# 打印地图，判断任务点
print_map()