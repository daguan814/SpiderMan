def print_map(step=20, size=8, block=4, cell_w=4):
    """
    打印 8x8 地图（一次性打印）：
    - 左下角为 0
    - 向右 +1
    - 向上 +step
    - 每 block x block 分块显示（默认 4x4）
    """
    def hline():
        blocks = size // block
        line = "┼"
        for _ in range(blocks):
            line += "─" * ((cell_w + 1) * block - 1) + "┼"
        return line

    lines = []

    for y in range(size - 1, -1, -1):
        if y % block == block - 1:
            lines.append(hline())

        row = "│"
        for x in range(size):
            row += f"{y * step + x:>{cell_w}}"
            if (x + 1) % block == 0:
                row += "│"
            else:
                row += " "
        lines.append(row)

    # 打印整张图，一次 print
    print("\n".join(lines))

