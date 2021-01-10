#!/usr/bin/env python3


import math
import sys
from PIL import Image, ImageDraw
from os import path
from block import Block
from input_parser import InputParser


class FlowChart:
    
    spacing = 100
    blk_size = (20, 20)
    font_size = 60
    txt_margin = 50

    overwrite_user_setting = True
    curve_factor = 160
    skew_factor = 50
    arl = 30
    ara = (math.pi/180)*45

    blocks = None

    def __init__(self, *args, **kwargs):
        self.im = Image.new(*args, **kwargs)
        self.row = 50
        self.center = args[1][0] // 2
        self.drawer = ImageDraw.Draw(self.im)
        self.blocks = []

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1) ** 2 + (y2-y1) ** 2)

    def rotate(self, x, y, xo, yo, theta):
        xf = xo + math.cos(theta) * (x - xo) - math.sin(theta) * (y - yo)
        yf = yo + math.sin(theta) * (x - xo) + math.cos(theta) * (y - yo)
        return xf, yf

    def arrow(self, *pts, draw=True):
        if len(pts) < 2:
            return
            raise ValueError("Line can't be drawn between less than 2 points")
        pt1, pt2 = pts[-2:]
        d = self.distance(*pt1, *pt2)
        if d == 0:
            raise ValueError("Distance Between Last 2 Points is 0")
        ahx = pt2[0] - (self.arl*(pt2[0] - pt1[0]))/d
        if pt2[1] > pt1[1]:
            ahy = pt2[1] - math.sqrt(self.arl**2 - (pt2[0] - ahx)**2)
        else:
            ahy = pt2[1] + math.sqrt(self.arl**2 - (pt2[0] - ahx)**2)
        
        if draw:
            self.drawer.line(pts, fill="black")
        pt_right = self.rotate(ahx, ahy, *pt2, -self.ara)
        pt_left = self.rotate(ahx, ahy, *pt2, self.ara)
        if draw:
            self.drawer.line([*pt_right, *pt2], fill="black")
            self.drawer.line([*pt_left, *pt2], fill="black")
        return *pts, (ahx, ahy)

    def is_colliding(self, pt_a, pt_b, corner):
        if corner == -1:
            return
        if ((pt_b[1] == pt_a[1] and corner in [0, 2])
            or (pt_b[0] == pt_a[0] and corner in [1, 3])):
             return corner
        elif corner == 1 and pt_a[0] > pt_b[0]:
            return corner
    
    def get_pts(self, block_a, block_b, ac=True):

        if isinstance(block_a, Block):
            spt_corner, ept_corner = self.get_corner(block_a, block_b, ac)
            spt = block_a.corners[spt_corner]
            ept = block_b.corners[ept_corner]
        else:
            spt, ept = block_a
            spt_corner = block_b
            ept_corner = -1

        block_spacing = self.blk_size[1]*10 + self.spacing*2
        pts = [spt]
        mp_index = -1
        if spt[0] != ept[0] and spt[1] != ept[1]:
            if spt_corner % 2:
                if spt[0] < ept[0]:
                    pts.append((spt[0], ept[1]))
                else:
                    pts.append((ept[0], spt[1]))
            else:
                if spt[1] < ept[1]:
                    pts.append((spt[0], ept[1]))
                else:
                    pts.append((ept[0], spt[1]))
                    
            mp_index = 1
        pts.append(ept)
        for (j, pt_a, pt_b, corner) in [(1, pts[0], pts[1], spt_corner),
                                        (-1, pts[-2], pts[-1], ept_corner)]:
            c = self.is_colliding(pt_a, pt_b, corner)
            if c != None:
                if c % 2:
                    if j == 1:
                        pts.insert(j, (pt_a[0]-self.spacing*(c-2), pt_a[1]))
                    else:
                        pts.insert(j, (pt_b[0]-self.spacing*(c-2), pt_b[1]))
                        
                else:
                    if j == 1:
                        pts.insert(j, (pt_a[0], pt_a[1]+self.spacing*(c-1)))
                    else:
                        pts.insert(j, (pt_b[0], pt_b[1]+self.spacing*(c-1)))
                if j == 1:
                    mp_index += 1
        if mp_index not in [0, -1]:
            if spt_corner % 2:
                if spt[0] < ept[0] or spt_corner == 3:
                    pts[mp_index] = (pts[mp_index+1][0], pts[mp_index-1][1])
                else:
                    pts[mp_index] = (pts[mp_index-1][0], pts[mp_index+1][1])
            else:
                if spt[1] > ept[1] or spt_corner == 2:
                    pts[mp_index] = (pts[mp_index+1][0], pts[mp_index-1][1])
                else:
                    pts[mp_index] = (pts[mp_index-1][0], pts[mp_index+1][1])
                    
        return pts

    def add_prefered(self, preference, min_corners, block, add=True):
        for c in preference:
            if c in min_corners:
                if add:
                    block.ccorners.append(c)
                return c
        if add:
            block.ccorners.append(preference[0])
        return preference[0]
        
    def get_corner(self, block_a, block_b, ac=True):
        
        ba_corners = {i:block_a.ccorners.count(i) for i in range(4)}
        ba_min = min(ba_corners.values())
        mba_corners = [c for c, v in ba_corners.items() if v == ba_min]
        bb_corners = {i:block_b.ccorners.count(i) for i in range(4)}
        bb_min = min(bb_corners.values())
        mbb_corners = [c for c, v in bb_corners.items() if v == bb_min]

        if block_a.center_factor < block_b.center_factor:
            if block_a.block == "decision":
                c1 = self.add_prefered([1, 2, 3], mba_corners, block_a, ac)
                c2 = self.add_prefered([0, 3, 1], mbb_corners, block_b, ac)
            else:
                c1 = self.add_prefered([2, 1, 3, 0], mba_corners, block_a, ac)
                c2 = self.add_prefered([3, 0, 1, 2], mbb_corners, block_b, ac)

        elif block_a.center_factor > block_b.center_factor:
            if block_a.block == "decision":
                c1 = self.add_prefered([3, 2, 1], mba_corners, block_a, ac)
                c2 = self.add_prefered([0, 1, 3], mbb_corners, block_b, ac)
            else:
                c1 = self.add_prefered([2, 3, 0, 1], mba_corners, block_a, ac)
                c2 = self.add_prefered([0, 1, 3, 2], mbb_corners, block_b, ac)

        elif block_a.center_factor == block_b.center_factor:
            if block_a.corners[0][1] > block_b.corners[2][1]:
                c1 = self.add_prefered([3, 2, 1, 0], mba_corners, block_a, ac)
                c2 = self.add_prefered([3, 2, 1, 0], mbb_corners, block_b, ac)
            else:
                c1 = self.add_prefered([2, 1, 3, 0], mba_corners, block_a, ac)
                c2 = self.add_prefered([0, 1, 3, 2], mbb_corners, block_b, ac)
        else:
            err = "Unable To Find Connection Between {} and {}"
            raise RuntimeError(err.format(block_a.block, block_b.block))
        return [c1, c2]

    def connect(self, block_a, block_b, text):
        if isinstance(block_b, Block):
            
            # Connect 2 Blocks
            pts = self.get_pts(block_a, block_b)
            self.arrow(*pts)
        else:
            
            # Connect a block and a line
            bf_id, bt_id = block_b.split(".", 2)
            af_blk, at_blk = self.blocks[int(bf_id)], self.blocks[int(bt_id)]
            pts = self.get_pts(af_blk, at_blk, ac=False)
            ept = ((pts[-1][0] + pts[-2][0])//2, (pts[-1][1] + pts[-2][1])//2)
            if block_a.corners[0][0] > ept[0]:
                corner = 3
            else:
                corner = 1
            pts = self.get_pts((block_a.corners[corner], ept), corner)
            self.arrow(*pts)
        
        if not text:
            return
        
        # Find the arrow head
        pts = pts[:2]
        font = Block.get_font(self.font_size)
        pt2, a_pt = self.arrow(*pts, draw=False)[-2:]
        
        # Add text to the end of the factor
        x_pad, y_pad = (a_pt[0] - pt2[0])*1.25, (a_pt[1] - pt2[1])*1.25
        pos = ((pts[0][0]+pts[1][0]+x_pad)//2, (pts[0][1]+pts[1][1]+y_pad)//2)
        w, h = self.drawer.textsize(text, font=font)
        if abs(pts[0][0] - pts[1][0]) < abs(pts[0][1] - pts[1][1]):
            self.drawer.text((pos[0]-w-self.blk_size[0], pos[1]-h//2),
                             text, font=font, fill="black")
        else:
            self.drawer.text((pos[0]-w//2, pos[1]-h-self.blk_size[1]),
                             text, font=font, fill="black")
            

    def draw(self, block, text, center=1):
        if block not in Block.supported_blocks:
            err_msg = "Block {} is not Supported\nSupported Blocks: {}"
            raise ValueError(err_msg.format(block, Block.supported_blocks))
        blk_size = self.blk_size
        if self.overwrite_user_setting:
            self.curve_factor = blk_size[1] * 8

        width, height = blk_size[0] * 10, blk_size[1] * 10
        if block == "connector":
            width = height

        row = self.row
        block = Block(self, block, width, height, center,
                      row, text, self.font_size)
        self.blocks.append(block)
        return block

    def show(self, blocking=True):
        self.im.show()
        if blocking:
            input("Press Any Key to Continue")

    def save(self):
        retry = True
        while retry:
            file_path = input("Save As: ")
            if path.exists(file_path):
                conf = input("File Path Exists, Overwrite <Y/n>? ").lower()
                if conf in ["y", "yes"]:
                    retry = False
            else:
                retry = False
        self.im.save(file_path)
        

def main():
    flow_chart = FlowChart("RGB", (2480, 3508), color="white")
    try:
        fp = sys.stdin
        if "-f" in sys.argv:
            file_path = sys.argv[sys.argv.index("-f")+1]
            fp = open(file_path)
        input_parser = InputParser(fp)
        input_parser.instruct(flow_chart)
    finally:
        fp.close()
    return flow_chart


if __name__ == "__main__":
    flow_chart = main()
    flow_chart.show(blocking=False)
    flow_chart.save()

