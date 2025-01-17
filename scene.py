from manim import *
from numpy import column_stack

class Scn(Scene):
    def construct(self):
        self.camera.background_color =  ManimColor.from_hex('#0d1117')
        self.parse("sample.bf")

    def parse(self, codefile: str):
        code =  open(codefile).read()
        codeunfiltered = "".join(filter(lambda c: c != '@', code))
        # memory section
        memsection = Rectangle(WHITE, height=8, width=4.0)
        memsection.to_edge(UR, 0)
        memlabel = Text("Memory", font="Monospace")
        memlabel.next_to(memsection, UP)
        memlabel.shift(DOWN * 1.1)
        
        memgrid = Rectangle(WHITE, height=1, width=3.0)
        memidrect = Rectangle(WHITE, height=1, width=1)
        memidrect.next_to(memgrid, LEFT, buff=0)
        memvalue =  DecimalNumber(0, 0, color=WHITE)
        memvalue.move_to(memgrid.get_center())
        memidlabel = DecimalNumber(0, 0, color=WHITE)
        memidlabel.move_to(memidrect.get_center())
        memid = VGroup(memidrect, memidlabel)
        memcell = [VGroup(memgrid, memid, memvalue)]

        memcell[0].next_to(memlabel, DOWN * 0.6)
        for i in range(1, 7):
            memcell.append(memcell[0].copy())
            memcell[i][1][1].set_value(i)
            memcell[i].next_to(memcell[i-1], DOWN, buff=0)
        # placeholder gyatt
        #mem2 = memcell.copy()
        #mem2.next_to(memcell, DOWN, buff=0)
        #mem3 = memcell.copy()
        #mem3.next_to(mem2, DOWN, buff=0)
        #mem4 = memcell.copy()
        #mem4.next_to(mem3, DOWN, buff=0)
        #mem5 = memcell.copy()
        #mem5.next_to(mem4, DOWN, buff=0)
        #mem6 = memcell.copy()
        #mem6.next_to(mem5, DOWN, buff=0)
        #mem7 = memcell.copy()
        #mem7.next_to(mem6, DOWN, buff=0)
        
        ram = [0,0,0,0,0,0,0]

        self.add(memsection, memlabel)
        self.add(*memcell)

        # code section
        coderect = Rectangle(WHITE, height=8, width=10.2)
        coderect.to_edge(UL, buff=0)
        codelabel = Text("Code:", color=WHITE, font="Monospace")
        codelabel.to_edge(UL, buff=0.2)
        codecontent = Code(
            "sample.bf",
            tab_width=4,
            background_stroke_width=1,
            background_stroke_color=WHITE,
            insert_line_no=False,
            style=Code.styles_list[15],
            language="brainfuck",
        )
        code = open(codefile).readlines()
        codecontent.scale_to_fit_width(8)
        codecontent.move_to(coderect.get_center())
        codecontent.shift(DOWN * 0.3)
        self.add(codelabel, coderect, codecontent)

        # do the actual parsing ##########################
        linepointer = 0
        columnpointer = 0
        memorypointer = 0
        loopstack = []
        currLoop = -1
        ignoringId = -1
        isEOF = lambda : (columnpointer + 1) == len(codecontent.code) and (linepointer + 1) == len(codecontent.code[-1])
        currmemory = lambda : memcell[memorypointer][2]
        programArrow = Arrow(max_stroke_width_to_length_ratio=0, start=UP, end=DOWN)
        programArrow.next_to(codecontent.code[0][0], UP)
        memoryArrow = Arrow(max_stroke_width_to_length_ratio=0, start=LEFT, end=RIGHT)
        memoryArrow.next_to(memcell[0], LEFT)
        self.add(programArrow, memoryArrow)
        self.wait(2)
        while not isEOF():
            if code[columnpointer][linepointer] == '\n':
                columnpointer = columnpointer + 1
                linepointer = 0
            else:
                if code[columnpointer][linepointer] == '[':
                    if ram[memorypointer] == 0 and ignoringId == -1:
                        ignoringId = len(loopstack)
                    else: 
                        loopstack.append((columnpointer, linepointer))
                    currLoop += 1

                elif code[columnpointer][linepointer] == ']':
                    if ram[memorypointer] == 0:
                        if ignoringId == currLoop:
                            ignoringId = -1
                            self.play(programArrow.animate.next_to(codecontent.code[columnpointer][linepointer], UP))
                        currLoop -= 1
                    else:
                        columnpointer, linepointer = loopstack[currLoop]
                        self.play(programArrow.animate.next_to(codecontent.code[columnpointer][linepointer], UP))

                if ignoringId == -1:
                    if code[columnpointer][linepointer] == '-':
                        ram[memorypointer] = (ram[memorypointer] - 1) % 256
                        self.play(currmemory().animate.set_value(ram[memorypointer]))
                    elif code[columnpointer][linepointer] == '+':
                        ram[memorypointer] = (ram[memorypointer] + 1) % 256
                        self.play(currmemory().animate.set_value(ram[memorypointer]))
                    elif code[columnpointer][linepointer] == '>':
                        memorypointer += 1
                        self.play(memoryArrow.animate.next_to(memcell[memorypointer], LEFT))
                    elif code[columnpointer][linepointer] == '<':
                        memorypointer -= 1
                        self.play(memoryArrow.animate.next_to(memcell[memorypointer], LEFT))
                linepointer += 1
                if ignoringId == -1:
                    self.play(programArrow.animate.next_to(codecontent.code[columnpointer][linepointer], UP))
