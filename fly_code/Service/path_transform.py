# -*- coding: UTF-8 -*-
"""
路径转换工具（仅用于生成 & 打印）
"""

# =========================================================
# 从 target_paths 导入原始 PATH_MAP（0 起飞）
# =========================================================

from target_paths import PATH_MAP


# =========================================================
# 坐标变换
# =========================================================

def mirror_point_lr(p):
    row = p // 20
    col = p % 20
    return row * 20 + (7 - col)


def mirror_point_ud(p):
    row = p // 20
    col = p % 20
    return (7 - row) * 20 + col


# =========================================================
# 方向映射
# =========================================================
# 说明：
# - 前 / 后 永远不变
# - 左右在需要时互换

DIR_LR_SWAP = {1: 1, 2: 2, 3: 4, 4: 3}
DIR_KEEP    = {1: 1, 2: 2, 3: 3, 4: 4}


# =========================================================
# 路径变换
# =========================================================

def transform_path(path, point_func, dir_map, yaw_flip):
    """
    yaw_flip: True -> yaw 取反
              False -> yaw 不变
    """
    new_path = []
    for d, p, yaw in path:
        new_d = dir_map[d]
        new_p = point_func(p)
        new_yaw = -yaw if yaw_flip else yaw
        new_path.append((new_d, new_p, new_yaw))
    return new_path


def transform_path_map(path_map, point_func, dir_map, yaw_flip):
    new_map = {}
    for target, path in path_map.items():
        new_target = point_func(target)
        new_map[new_target] = transform_path(
            path, point_func, dir_map, yaw_flip
        )
    return new_map


# =========================================================
# 可读格式打印（用于粘贴）
# =========================================================

def pretty_print_path_map(path_map, name="PATH_MAP"):
    print(f"{name} = {{")
    for target in sorted(path_map.keys(), reverse=True):
        path = path_map[target]
        print(f"    {target}: [  # 共{len(path)}点")
        for step in path:
            print(f"        {step},")
        print("    ],\n")
    print("}")


# =========================================================
# 主入口
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # 0 -> 7（左右镜像）
    # 前后不变，左右互换，yaw 取反
    # -----------------------------------------------------
    map_7 = transform_path_map(
        PATH_MAP,
        mirror_point_lr,
        DIR_LR_SWAP,
        yaw_flip=True
    )

    # -----------------------------------------------------
    # 0 -> 140（上下镜像）
    # 前后不变，左右互换，yaw 取反
    # -----------------------------------------------------
    # -----------------------------------------------------
    # 0 -> 140（上下镜像）
    # 前后不变，左右互换，yaw 取反
    # -----------------------------------------------------
    map_140 = transform_path_map(
        PATH_MAP,
        mirror_point_ud,
        DIR_LR_SWAP,
        yaw_flip=True
    )

    # -----------------------------------------------------
    # 140 -> 147（左右镜像 140）
    # 方向不变，yaw 不变，只换坐标
    # -----------------------------------------------------
    map_147 = transform_path_map(
        map_140,
        mirror_point_lr,
        DIR_LR_SWAP,
        yaw_flip=True
    )

    # -----------------------------------------------------
    # 只打印生成的三个（不包含原始）
    # -----------------------------------------------------
    final_map = {}
    final_map.update(map_7)
    final_map.update(map_140)
    final_map.update(map_147)

    pretty_print_path_map(final_map)
