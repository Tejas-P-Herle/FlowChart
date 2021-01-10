from PIL import ImageFont
import math

class Block:
    font_path = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
    supported_blocks = ["process", "decision", "io", "start",
                        "end", "stop", "connector", "loop"]
    ccorners = None
    def __init__(self, im, block, width, height,
                 center_factor, row, text, font_size):
        self.drawer = im.drawer
        self.skew_factor = im.skew_factor
        self.distance = im.distance
        self.rotate = im.rotate

        self.corners = []
        center = im.center * center_factor
        self.center_factor = center_factor
        self.center, self.row = center, row
        self.block = block
        self.ccorners = []

        draw = False
        breaker = 4
        while not draw and breaker:
            if self.corners:
                
                text_area = self.set_text(text, height, font_size, draw=False)
                tlm = max(0, text_area[0] - im.txt_margin)
                tm = max(0, text_area[1] - im.txt_margin)
                if tlm < self.corners[3][0]:
                    if block in ["start", "end", "stop", "process", "io"]:
                        width += -1 * (tlm - self.corners[3][0])
                    else:
                        width += -1 * (tlm - self.corners[3][0]) * 2
                    if block in ["connector", "decision"]:
                        height = width
                elif tm < self.corners[0][1]:
                    height += -1 * (tm - self.corners[0][1]) * 2
                else:
                    draw = True
                    
            if block == "process":
                self.process(width, height, center, row, draw=draw)
            elif block == "decision":
                self.decision(height, center, row, draw=draw)
            elif block == "io":
                self.io(width, height, center, row, draw=draw)
            elif block in ["start", "end", "stop"]:
                if im.overwrite_user_setting:
                    self.curve_factor = (height/10) * 8
                self.tip(width, height, center, row, draw=draw)
            elif block == "connector":
                self.connector(height, center, row, draw=draw)
            elif block == "loop":
                self.loop(width, height, center, row, draw=draw)
            breaker -= 1

        text_area = self.set_text(text, height, font_size, draw=True)
        self.width, self.height = width, height

    @classmethod
    def get_font(cls, font_size):
        return ImageFont.truetype(cls.font_path, font_size)

    def set_text(self, text, height, font_size=70, draw=False):
        font = self.get_font(font_size)
        w, h = self.drawer.textsize(text, font=font)
        pos = (self.center - w//2, self.row + height//2 - h//2)
        if draw:
            self.drawer.text(pos, text, fill="black", font=font)
        return pos

    def process(self, width, height, center, row, draw=False):
        start, end = center - width, center + width
        pos = [start, row, end, row + height]
        if draw:
            self.drawer.rectangle(pos, outline="black")

        self.corners = [(center, row),          (end, row + height // 2),
                        (center, row + height), (start, row + height// 2)]

    def decision(self, height, center, row, draw=False):
        pos = [
            (center, row),
            (center + height // 2, row + height // 2),
            (center, row + height),
            (center - height // 2, row + height// 2)
        ]

        if draw:
            self.drawer.polygon(pos, outline="black")
        
        self.corners = pos

    def io(self, width, height, center, row, draw=False):
        start, end = center - width, center + width
        
        tl, tr = start + self.skew_factor, end + self.skew_factor
        bl, br = start - self.skew_factor, end - self.skew_factor

        pos = [
            (tl, row),
            (bl, row + height),
            (br, row + height),
            (tr, row)
        ]
        
        if draw:
            self.drawer.polygon(pos, outline="black")
        
        self.corners = [
            (center, row),
            (tr-self.skew_factor, row+height//2),
            (center, row+height),
            (tl-self.skew_factor, row+height//2)
        ]

    def tip(self, width, height, center, row, draw=False):
        start, end = center - width, center + width

        arc1 = [start, row, start + self.curve_factor, row + height]
        arc2 = [end - self.curve_factor, row, end, row + height]
        
        if draw:
            self.drawer.arc(arc1, start=90, end=-90, fill="black")
            self.drawer.arc(arc2, start=-90, end=90, fill="black")
       
        empty = self.curve_factor // 2
        lstart, lend = start + empty, end - empty
        line1 = [lstart, row, lend, row]
        line2 = [lstart, row + height, lend, row + height]
        
        if draw:
            self.drawer.line(line1, fill="black")
            self.drawer.line(line2, fill="black")

        self.corners = [(center, row),          (end, row + height // 2),
                        (center, row + height), (start, row + height// 2)]

    def connector(self, height, center, row, draw=False):
        start, end = center - height // 2, center + height // 2

        pos = [start, row, end, row + height]

        if draw:
            self.drawer.ellipse(pos, outline="black")

        self.corners = [(center, row),          (end, row + height // 2),
                        (center, row + height), (start, row + height// 2)]

    def loop(self, width, height, center, row, draw=False):
        start, end = center - width, center + width

        pos = [
            (start + self.skew_factor, row),
            (start, row + height // 2),
            (start + self.skew_factor, row + height),
            (end - self.skew_factor, row + height),
            (end, row + height // 2),
            (end - self.skew_factor, row),
        ]

        if draw:
            self.drawer.polygon(pos, outline="black")

        self.corners = [(center, row),          (end, row + height // 2),
                        (center, row + height), (start, row + height// 2)]

