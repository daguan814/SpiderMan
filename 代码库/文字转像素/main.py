#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INPUT_PATH = "11.jpg"
OUTPUT_PATH = "output.png"
TEXT = "zyl"
FONT_SIZE = 12


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render an image by replacing each pixel with text.")
    parser.add_argument("-i", "--input", default=INPUT_PATH, help="Input image path")
    parser.add_argument("-o", "--output", default=OUTPUT_PATH, help="Output image path")
    parser.add_argument("-t", "--text", default=TEXT,
                        help="Text to render for each pixel")
    parser.add_argument("--charset", default=None,
                        help="Characters ordered from dark to light")
    parser.add_argument("--invert", action="store_true",
                        help="Invert charset mapping (light to dark)")
    parser.add_argument("--font", default=None,
                        help="Optional font file path (TTF/OTF)")
    parser.add_argument("--font-size", type=int, default=FONT_SIZE,
                        help="Font size for each pixel cell")
    parser.add_argument("--max-width", type=int, default=None,
                        help="Resize input to max width (keep aspect)")
    parser.add_argument("--max-height", type=int, default=None,
                        help="Resize input to max height (keep aspect)")
    return parser.parse_args()


def find_default_cjk_font() -> Path | None:
    candidates = [
        # macOS
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
        # Windows
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        # Linux
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/arphic/ukai.ttc"),
        Path("/usr/share/fonts/truetype/arphic/uming.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def load_font(font_path: str | None, font_size: int) -> ImageFont.FreeTypeFont:
    if font_path:
        return ImageFont.truetype(font_path, font_size)
    default_cjk = find_default_cjk_font()
    if default_cjk:
        return ImageFont.truetype(str(default_cjk), font_size)
    return ImageFont.load_default()


def resize_if_needed(img: Image.Image, max_w: int | None, max_h: int | None) -> Image.Image:
    if max_w is None and max_h is None:
        return img

    w, h = img.size
    scale_w = max_w / w if max_w else 1.0
    scale_h = max_h / h if max_h else 1.0
    scale = min(scale_w, scale_h, 1.0)
    if scale >= 1.0:
        return img

    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def pixel_to_char(pixel: tuple[int, int, int], charset: str, invert: bool) -> str:
    r, g, b = pixel
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    chars = charset[::-1] if invert else charset
    idx = int((lum / 255) * (len(chars) - 1))
    return chars[idx]


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    img = Image.open(input_path).convert("RGBA")
    img = resize_if_needed(img, args.max_width, args.max_height)

    # Flatten alpha onto white so we always draw RGB colors.
    if "A" in img.getbands():
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(background, img).convert("RGB")
    else:
        img = img.convert("RGB")

    font = load_font(args.font, args.font_size)

    cell_w = args.font_size
    cell_h = args.font_size
    out_w = img.width * cell_w
    out_h = img.height * cell_h

    out_img = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    draw = ImageDraw.Draw(out_img)

    text = args.text
    charset = args.charset
    if charset:
        charset = charset.strip()
        if not charset:
            raise ValueError("charset cannot be empty")

    for y in range(img.height):
        for x in range(img.width):
            color = img.getpixel((x, y))
            if charset:
                text = pixel_to_char(color, charset, args.invert)
            draw.text((x * cell_w, y * cell_h), text, fill=color, font=font)
        progress = int(((y + 1) / img.height) * 100)
        sys.stdout.write(f"\rProgress: {progress}%")
        sys.stdout.flush()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(output_path)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
