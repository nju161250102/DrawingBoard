# coding=utf-8
import wx
import os
import thread
import pygame
import cv2 as cv


class SubScreen(object):
    def __init__(self, size, color=(0, 0, 0), width=1):
        self.lines = []
        self.color = color
        self.width = width
        self.label = ""
        self.info = ""
        self.screen = pygame.Surface(size, pygame.SRCALPHA, 32)
        self.screen.fill((255, 255, 255, 0))

    def draw(self):
        for line in self.lines:
            if len(line) > 1:
                pygame.draw.lines(self.screen, self.color, False, line, self.width)

    def active_draw(self):
        for line in self.lines:
            if len(line) > 1:
                active_color = (255 - self.color[0], self.color[1], self.color[2])
                pygame.draw.lines(self.screen, active_color, False, line, self.width + 1)

    def new_line(self):
        self.lines.append([])

    def add_point(self, pos):
        if len(self.lines) > 0:
            self.lines[-1].append(pos)

    def del_line(self):
        if len(self.lines) > 0:
            self.lines.pop()

    def get_shape(self):
        self.draw()
        pygame.image.save(self.screen, "s.png")
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
            if corners == 3:
                self.label = "三角形"
            elif corners == 4:
                self.label = "矩形"
            elif corners >= 7:
                self.label = "圆形"
            elif 4 < corners < 7:
                self.label = "多边形"


class SDLThread:
    def __init__(self, panel, size):
        self.panel = panel
        self.size = size
        self.main_screen = pygame.display.set_mode(size)
        self.main_screen.fill((255, 255, 255))
        self.screen_list = [SubScreen(size)]
        self.current_num = 0
        self.draw_state = 0  # 0-等待绘制 1-正在绘制 2-结束图层绘制

        # self.panel.pre_button.Bind(wx.EVT_BUTTON, self.pre_screen)
        # self.panel.next_button.Bind(wx.EVT_BUTTON, self.next_screen)

    def current_screen(self):
        return self.screen_list[self.current_num]

    def draw(self):
        if self.current_num < len(self.screen_list) - 1:
            self.current_screen().active_draw()
        for screen in self.screen_list:
            screen.draw()
            self.main_screen.blit(pygame.Surface.convert_alpha(screen.screen), (0, 0))
        pygame.display.flip()

    def save_screen(self):
        # 结束一个图层的绘制
        # self.draw_state = 0
        self.current_screen().get_shape()
        self.current_screen().info = self.panel.get_input()

    def add_screen(self):
        if self.current_num == len(self.screen_list) - 1:
            self.screen_list.append(SubScreen(self.size))
            self.current_num += 1

    def run(self):
        while True:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # 鼠标单击左键
                if event.button == 1:
                    # 处于等待绘制状态
                    if self.draw_state == 0:
                        self.draw_state = 1
                        self.current_screen().new_line()
                    # 处于正在绘制状态
                    elif self.draw_state == 1:
                        self.draw_state = 0
                        self.save_screen()
                    self.current_screen().add_point(pos)
                # 鼠标单击右键
                elif event.button == 3:
                    self.save_screen()
                    self.add_screen()
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if self.draw_state == 1 and pos[1] < self.size[1]:
                    self.current_screen().add_point(pos)

            # print self.current_screen().lines
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
        self.input_box = wx.TextCtrl(self, -1, '', pos=(310, 620), size=(200, 30))
        self.type_box = wx.TextCtrl(self,  -1, '', pos=(110, 620), size=(100, 30))
        self.type_box.SetEditable(False)
        self.pre_button = wx.Button(self, label="上一图层", pos=(10, 610), size=(80, 30))
        self.next_button = wx.Button(self, label="下一图层", pos=(10, 650), size=(80, 30))
        self.pnlSDL = SDLPanel(self, -1, panel_size)

    def get_input(self):
        return self.input_box.GetValue()


def main():
    app = wx.App()
    frame = MyFrame(None, wx.ID_ANY, "PY画板", (800, 600), (810, 740))
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
