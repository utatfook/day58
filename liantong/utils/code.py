import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def check_code(width=120, height=30, char_length=5, font_size=28):
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')

    def rndChar():
        # 生成随机字母
        """ Return a Unicode string of one character with ordinal i; 0 <= i <= 0x10ffff. """
        return chr(random.randint(48, 57))

    def rndColor():
        # 生成随机颜色
        return random.randint(0, 255), random.randint(10, 255), random.randint(64, 255)

    # 写文字
    # font = ImageFont.truetype(size=28)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        h = random.randint(0, 4)
        draw.text(xy=(i * width / char_length, h), text=char, fill=rndColor())

    # 写干扰点
    for i in range(40):
        draw.point(xy=(random.randint(0, width), random.randint(0, height)), fill=rndColor())

    # 写干扰圆圈
    for i in range(40):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc(xy=(x, y, x + 4, y + 4), start=0, end=90, fill=rndColor())

    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(xy=(x1, y1, x2, y2), fill=rndColor())

    # ImageFilter是滤波功能，可以模糊图片，增强图片等，EDGE_ENHANCE_MORE是增强边缘，以便阅读。
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    # 返回了两个东西，一是渲染好的图片，二是图片中的字符串
    return img, ''.join(code)
