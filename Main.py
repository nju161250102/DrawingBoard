# coding=utf-8
import pygame
import numpy as np
import cv2 as cv


def handle(img):
    h, w, ch = img.shape
    result = np.zeros((h, w, ch), dtype=np.uint8)
    # 二值化图像
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    out_binary, contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for cnt in range(len(contours)):
        # 轮廓逼近
        epsilon = 0.1 * cv.arcLength(contours[cnt], True)
        approx = cv.approxPolyDP(contours[cnt], epsilon, True)

        # 分析几何形状
        corners = len(approx)
        if corners == 3:
            print "三角形"
        if corners == 4:
            print "矩形"
        if corners >= 10:
            print "圆形"
        if 4 < corners < 10:
            print "多边形"
    print "---------------------------"


def main():
    (width, height) = (800, 600)
    # 创建窗口
    screen = pygame.display.set_mode((width, height))
    screen.fill((255, 255, 255))
    screen_list = []
    # 设置窗口名称
    pygame.display.set_caption("My Game")
    # 创建 Clock 对象
    clock = pygame.time.Clock()
    draw_flag = False
    points = []

    while True:
        # 设置帧数为 30
        clock.tick(30)

        (x, y) = pygame.mouse.get_pos()
        if draw_flag:
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(screen_list[-1], (0, 0, 0), not draw_flag, points)

        # 遍历处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                draw_flag = not draw_flag
                if draw_flag:
                    sub_screen = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                    sub_screen.fill((255, 255, 255, 0))
                    screen_list.append(sub_screen)
                    points = []
                else:
                    pygame.draw.lines(screen_list[-1], (0, 0, 0), not draw_flag, points)
                    pygame.image.save(screen_list[-1], "s.png")
                    img = cv.imread("s.png")
                    handle(img)
        # 更新画面
        for s in screen_list:
            screen.blit(pygame.Surface.convert_alpha(s), (0, 0))
        pygame.display.update()


if __name__ == '__main__':
    main()
