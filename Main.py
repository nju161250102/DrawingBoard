# coding=utf-8
import wx
import os
import math
import thread
import pygame
import cv2 as cv
import Model


class SDLThread:
    def __init__(self, panel, size):
        self.panel = panel
        self.size = size
        self.main_screen = pygame.display.set_mode(size)
        self.main_screen.fill((255, 255, 255))
        self.shapes = []
        self.lines = []
        self.current_num = 0
        self.state = 0  # 0-等待绘制 1-正在绘制 2-选择模式
        self.panel.identify_button.Bind(wx.EVT_BUTTON, self.get_shape)
        self.panel.choose_button.Bind(wx.EVT_BUTTON, self.choose_event)
        self.panel.draw_button.Bind(wx.EVT_BUTTON, self.draw_event)

    def add_point(self, pos):
        if len(self.lines) > 0:
            self.lines[-1].append(pos)

    def choose_event(self, event):
        self.state = 2

    def draw_event(self, event):
        self.state = 0
        self.current_num = len(self.shapes)
        self.panel.set_text("请绘制图形", "")

    def draw_lines(self, screen):
        for line in self.lines:
            if len(line) > 1:
                pygame.draw.lines(screen, self.get_color(), False, line, 1)

    def draw(self):
        for index, shape in enumerate(self.shapes):
            shape.draw(self.main_screen, index == self.current_num)
        self.draw_lines(self.main_screen)
        pygame.display.flip()

    def get_color(self):
        return (0, 0 ,0)

    def get_shape(self, event):
        if self.state != 0 or len(self.lines) == 0:
            return
        screen = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        screen.fill((255, 255, 255, 0))
        self.draw_lines(screen)
        pygame.image.save(screen, "s.png")
        img = cv.imread("s.png")
        # 二值化图像
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

        out_binary, contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in range(len(contours)):
            # 轮廓逼近
            epsilon = 0.03 * cv.arcLength(contours[cnt], True)
            approx = cv.approxPolyDP(contours[cnt], epsilon, True)

            # 分析几何形状
            corners = len(approx)
            # print approx
            if corners == 3:
                points = [(p[0][0], p[0][1]) for p in approx]
                self.shapes.append(Model.Triangle(points, self.get_color(), self.panel.get_input()))
            elif corners == 4:
                x_list = [p[0][0] for p in approx]
                y_list = [p[0][1] for p in approx]
                x_list.sort()
                y_list.sort()
                pos = ((x_list[0] + x_list[1]) / 2, (y_list[0] + y_list[1]) / 2)
                size = ((x_list[2] + x_list[3]) / 2 - pos[0], (y_list[2] + y_list[3]) / 2 - pos[1])
                if float(abs(size[0] - size[1])) / max(size[0], size[1]) < 0.1:
                    self.shapes.append(Model.Square(pos, (size[0] + size[1]) / 2,
                                                    self.get_color(), self.panel.get_input()))
                else:
                    self.shapes.append(Model.Rect(pos, size, self.get_color(), self.panel.get_input()))
            elif corners >= 7:
                mm = cv.moments(contours[cnt])
                cx = int(mm['m10'] / mm['m00'])
                cy = int(mm['m01'] / mm['m00'])
                radius_list = map(lambda point: math.sqrt((point[0][0] - cx)**2 + (point[0][1] - cy)**2), approx)
                radius = int(sum(radius_list) / len(radius_list))
                self.shapes.append(Model.Circle((cx, cy), radius, self.get_color(), self.panel.get_input()))
        self.lines = []
        self.current_num = len(self.shapes)
        self.main_screen.fill((255, 255, 255))
        self.panel.set_text("识别结果：" + self.shapes[-1].get_shape(), "")

    def run(self):
        while True:
            if not pygame.display.get_init():
                break
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # 鼠标单击左键
                if event.button == 1:
                    # 处于等待绘制状态
                    if self.state == 0:
                        self.state = 1
                        self.lines.append([])
                    # 处于正在绘制状态
                    elif self.state == 1:
                        self.state = 0
                    elif self.state == 2:
                        for index, shape in enumerate(self.shapes):
                            if shape.judge_point(pos):
                                self.current_num = index
                                self.panel.set_text("选择的图形形状：" + shape.get_shape(), shape.info)
                                break
                # 鼠标单击右键
                elif event.button == 3:
                    pass
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if self.state == 1 and pos[1] < self.size[1]:
                    self.add_point(pos)
            if self.current_num < len(self.shapes):
                self.shapes[self.current_num].info = self.panel.get_input()
            self.draw()

    def start(self):
        thread.start_new_thread(self.run, ())


class SDLPanel(wx.Panel):
    def __init__(self, parent, panel_id, panel_size):
        wx.Panel.__init__(self, parent, panel_id, size=panel_size)
        self.Fit()
        os.environ['SDL_WINDOWID'] = str(self.GetHandle())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.display.init()
        self.thread = SDLThread(parent, panel_size)
        self.thread.start()


class MyFrame(wx.Frame):
    def __init__(self, parent, panel_id, title, panel_size, win_size):
        wx.Frame.__init__(self, parent, panel_id, title, size=win_size)
        self.SetMaxSize(win_size)
        self.choose_button = wx.Button(self, label="选择", pos=(10, 610), size=(70, 30))
        self.draw_button = wx.Button(self, label="绘图", pos=(90, 610), size=(70, 30))
        self.identify_button = wx.Button(self, label="识别", pos=(170, 610), size=(70, 30))
        self.input_box = wx.TextCtrl(self, -1, '', pos=(250, 610), size=(210, 30))
        self.type_box = wx.TextCtrl(self,  -1, '', pos=(0, 650), size=(win_size[0], 30))
        self.type_box.SetEditable(False)
        self.pnlSDL = SDLPanel(self, -1, panel_size)

    def get_input(self):
        return self.input_box.GetValue()

    def set_text(self, label, info):
        self.input_box.SetValue(info)
        self.type_box.SetValue(label)


def main():
    app = wx.App()
    frame = MyFrame(None, wx.ID_ANY, "PY画板", (800, 600), (810, 715))
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
