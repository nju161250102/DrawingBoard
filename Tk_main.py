# coding=utf-8
import wx
import os
import thread
import pygame
import cv2 as cv


class SubScreen(object):

    def __init__(self, size):
        self.points = []
        self.color = (0, 0, 0)
        self.width = 1
        self.label = ""
        self.info = ""
        self.screen = pygame.Surface(size, pygame.SRCALPHA, 32)
        self.screen.fill((255, 255, 255, 0))


class SDLThread:
    def __init__(self, panel, size):
        self.panel = panel
        self.size = size
        self.m_bKeepGoing = self.m_bRunning = False
        self.screen = pygame.display.set_mode(size)
        self.screen.fill((255, 255, 255))
        self.screen_list = []
        self.active_screen = SubScreen(size)
        self.draw_flag = False

    def handle(self, img):
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
                return "三角形"
            if corners == 4:
                return "矩形"
            if corners >= 7:
                return "圆形"
            if 4 < corners < 7:
                return "多边形"
        return ""

    def Start(self):
        self.m_bKeepGoing = self.m_bRunning = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.m_bKeepGoing = False

    def IsRunning(self):
        return self.m_bRunning

    def Run(self):
        while self.m_bKeepGoing:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.Stop()  # 待确定
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标单击左键
                if event.button == 1:
                    if self.draw_flag:
                        self.draw_flag = False
                        pygame.draw.lines(self.active_screen.screen, (0, 0, 0), True, self.active_screen.points)
                    else:
                        self.draw_flag = True
                elif event.button == 3:
                    if len(self.active_screen.points) > 1:
                        pygame.image.save(self.active_screen.screen, "s.png")
                        img = cv.imread("s.png")
                        self.panel.type_box.SetValue(self.handle(img))
                        self.active_screen.label = self.panel.type_box.GetValue()
                        self.active_screen.info = self.panel.input_box.GetValue()
                        self.screen_list.append(self.active_screen)
                        self.active_screen = SubScreen(self.size)
            elif event.type == pygame.MOUSEMOTION:
                (x, y) = pygame.mouse.get_pos()
                if self.draw_flag and y < self.size[1]:
                    self.active_screen.points.append((x, y))

            if len(self.active_screen.points) > 1:
                pygame.draw.lines(self.active_screen.screen, self.active_screen.color, not self.draw_flag, self.active_screen.points)
            for s in self.screen_list:
                self.screen.blit(pygame.Surface.convert_alpha(s.screen), (0, 0))
            self.screen.blit(pygame.Surface.convert_alpha(self.active_screen.screen), (0, 0))
            pygame.display.flip()
        self.m_bRunning = False


class SDLPanel(wx.Panel):
    def __init__(self, parent, ID, tplSize):
        wx.Panel.__init__(self, parent, ID, size=tplSize)
        self.Fit()
        os.environ['SDL_WINDOWID'] = str(self.GetHandle())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.display.init()
        self.thread = SDLThread(parent, tplSize)
        self.thread.Start()

    def __del__(self):
        self.thread.Stop()


class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title, tplSize, win_size):
        wx.Frame.__init__(self, parent, ID, title, size=win_size)
        self.input_box = wx.TextCtrl(self, -1, '', pos=(210, 620), size=(200, 30))
        self.type_box = wx.TextCtrl(self,  -1, '', pos=(10, 620), size=(100, 30))
        self.type_box.SetEditable(False)
        self.pnlSDL = SDLPanel(self, -1, tplSize)
        # self.Fit()


app = wx.App()
frame = MyFrame(None, wx.ID_ANY, "SDL Frame", (800, 600), (800, 700))
frame.Show()
app.MainLoop()
