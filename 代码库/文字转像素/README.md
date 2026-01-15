# 文字转像素

把输入图片的每个像素替换为一段文字，输出为新图片。

## 依赖

- Python 3.10+
- Pillow

安装：

```bash
pip install pillow
```

## 用法

```bash
python main.py -i input.jpg -o output.png -t "你" --font /path/to/font.ttf --font-size 12
```

灰度映射字符集（从深到浅）：

```bash
python main.py -i input.jpg -o output.png --charset "@%#*+=-:. " --font /path/to/font.ttf --font-size 12
```

可选：缩小输入以加快速度

```bash
python main.py -i input.jpg -o output.png -t "你" --font /path/to/font.ttf --font-size 12 --max-width 200 --max-height 200
```

## 参数说明

- `-i/--input` 输入图片路径
- `-o/--output` 输出图片路径
- `-t/--text` 用于替换像素的文字
- `--charset` 灰度映射字符集（从深到浅），启用后会忽略 `--text`
- `--invert` 反转字符集映射（从浅到深）
- `--font` 字体文件路径（TTF/OTF），不指定时会尝试自动选择系统中文字体
- `--font-size` 像素对应的文字大小
- `--max-width`/`--max-height` 缩放输入图片，保持比例

## 说明

- 默认字体可能不支持中文，建议指定字体。
- 输出尺寸会按 `输入尺寸 * font-size` 放大。
