#!/usr/bin/env python3

import sys
from PIL import Image, ImageDraw, ImageFont
from flow_chart import FlowChart
from input_parser import InputParser

font_path = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
font_size = 70
h_font_size = 50
sheet = (2480, 3508)
margin = 50


class Algorithm:
    row = 0

    def __init__(self, h, font_path_l=None, font_size_l=None):
        dim = (sheet[0]//2-margin, sheet[1]-margin-h)
        self.im = Image.new("RGB", dim, color="white")
        self.drawer = ImageDraw.Draw(self.im)
        self.font_path = font_path_l if font_path_l else font_path
        self.font_size = font_size_l if font_size_l else font_size
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.line_spacing = self.font_size // 5

    def add_lines(self, algo):
        for ln in algo:
            self.add_line(ln.rstrip("\n"))
    
    def add_line(self, text):
        words = text.split(" ")
        start = self.row
        while words:
            ln = words.copy()
            w, h = self.drawer.textsize(" ".join(ln), font=self.font)
            page_w = self.im.size[0]
            while w > page_w:
                ln = ln[:-1]
                w, h = self.drawer.textsize(" ".join(ln), font=self.font)
            self.drawer.text((0, self.row), " ".join(ln),
                             fill="black", font=self.font)
            self.row += h + self.line_spacing
            if len(ln) != len(words):
                words = words[len(ln):]
            else:
                words = []
        return self.row - start

class Page:
    def __init__(self, algo_path, *args, **kwargs):
        self.im = Image.new(*args, **kwargs)
        self.drawer = ImageDraw.Draw(self.im)
        with open(algo_path) as file:
            self.head = file.readline()
            self.algo = file.readlines()

    def get_font(self, font_size):
        return ImageFont.truetype(font_path, int(font_size*1.5))

    def add_txt(self, txt, font, row, max_w, x):
        words = txt.split(" ")
        line_spacing = font.size // 5
        start = row
        while words:
            ln = words.copy()
            w, h = self.drawer.textsize(" ".join(ln), font=font)
            while w > max_w - margin:
                ln = ln[:-1]
                w, h = self.drawer.textsize(" ".join(ln), font=font)
            self.drawer.text((((max_w - w) // 2) + x, row), " ".join(ln),
                             fill="black", font=font)

            row += h + line_spacing
            if len(ln) != len(words):
                words = words[len(ln):]
            else:
                words = []

        return row - start

    def beautify(self):
        w, h = self.im.size

        tm = self.add_txt(self.head, self.get_font(h_font_size*1.5), 0, w, 0)
        font = self.get_font(h_font_size*1.25)

        self.drawer.line([w//2, tm, w//2, h], fill="black")
        self.drawer.line([0, tm, h, tm], fill="black")

        self.add_txt("Flow Chart", font, tm, w//2, 0)
        tm += self.add_txt("Algorithm", font, tm, w//2, w//2)

        self.drawer.line([0, tm, h, tm], fill="black")
        self.tm = tm + 10

    def add_flow_chart(self, path, x, y):
        y += self.tm
        flow_chart = FlowChart("RGB", (x, y), color="white")
        with open(path) as file:
            input_parser = InputParser(file)
            input_parser.instruct(flow_chart)
        self.im.paste(flow_chart.im, (0, self.tm))

    def add_algorithm(self, x, y):
        algorithm = Algorithm(self.tm)
        algorithm.add_lines(self.algo)
        self.im.paste(algorithm.im, (x+margin, y+margin+self.tm))


def main():
    if len(sys.argv) != 3:
        print("Usage: ./algorithm.py algorithm_filepath instructions_filepath")
        sys.exit(64)
    algo_path = sys.argv[1]
    inst_path = sys.argv[2]
    page = Page(algo_path, "RGB", sheet, color="white")
    page.beautify()
    page.add_flow_chart(inst_path, sheet[0]//2, sheet[1])
    page.add_algorithm(sheet[0]//2, 0)

    page.im.show()
    if (path := input("Save As: ")):
        page.im.save(path)


if __name__ == "__main__":
    main()


