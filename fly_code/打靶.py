# -*- coding: UTF-8 -*-

from helloFly import fly
from Service.target_paths import get_path_points

# ================= 参数 =================

CHECK_TAG = 63           # 靶标编号
TAKEOFF_HIGH = 100       # 起飞高度，靶标高度
MOVE_DISTANCE = 50       # 所有移动统一 50cm

# ================= 初始化 =================
fh = fly()

# 等待开始
print("按下k2起飞！")
while not fh.getKeyPress(2):  # 按下 K2 起飞
    fh.sleep(0.01)

fh.xySpeed(0, 65)   # 设置横向移动速度
fh.zSpeed(0, 50)    # 设置飞行速度

fh.ledCtrl(0, 0, [0, 255, 0])  # 绿灯起飞
fh.takeOff(0, TAKEOFF_HIGH)

# ================= 获取靶标路径（★ 对应点 2） =================
path_points = get_path_points(CHECK_TAG)

if not path_points:
    print("⚠ 未配置该靶标路径，终止任务")
    fh.ledCtrl(0, 0, [255, 255, 0])  # 黄灯警告
    fh.flyCtrl(0, 0)
    exit()

# ================= 打靶流程 =================
for index, (direction, tag_id, rotate_angle) in enumerate(path_points):
    print(f"[Target {index+1}] dir={direction}, tag={tag_id}, rot={rotate_angle}")

    # 1. 移动并寻找靶标
    fh.moveSearchTag(
        id=0,
        dir=direction,
        distance=MOVE_DISTANCE,
        tagID=tag_id
    )

    fh.sleep(1)  # 稳定悬停

    # 2. 射击前旋转
    if rotate_angle != 0:
        fh.rotation(0, rotate_angle)
        fh.sleep(0.5)

    # 3. 发射激光
    fh.shootCtrl(0, 0)
    fh.sleep(5)

    # 4. 转回原方向
    if rotate_angle != 0:
        fh.rotation(0, -rotate_angle)
        fh.sleep(0.5)

# ================= 结束 =================
fh.ledCtrl(0, 0, [255, 0, 0])  # 红灯
fh.flyHigh(0, 40)
fh.flyCtrl(0, 0)
