# coding=utf-8
import pygame
import cv2 as cv


class SubScreen(object):

    def __init__(self, size):
        self.points = []
        self.color = (0, 0, 0)
        self.width = 1
        self.screen = pygame.Surface(size, pygame.SRCALPHA, 32)
        self.screen.fill((255, 255, 255, 0))


def handle(img):
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


def main():
    # 窗口大小
    size = (800, 600)
    input_height = 100
    # 图层列表
    screen_list = []
    active_screen = SubScreen(size)
    current_string = ""

    # 创建窗口
    screen = pygame.display.set_mode((size[0], size[1] + input_height))
    screen.fill((255, 255, 255))
    # 设置窗口名称
    pygame.display.set_caption("PY画板")
    # 创建 Clock 对象
    clock = pygame.time.Clock()
    draw_flag = False

    while True:
        # 设置帧数为 30
        clock.tick(30)

        # 遍历处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标单击左键
                if event.button == 1:
                    if draw_flag:
                        draw_flag = False
                        pygame.draw.lines(active_screen.screen, (0, 0, 0), True, active_screen.points)
                    else:
                        draw_flag = True
                elif event.button == 3:
                    if len(active_screen.points) > 1:
                        screen_list.append(active_screen)
                        pygame.image.save(active_screen.screen, "s.png")
                        img = cv.imread("s.png")
                        print handle(img)
                        active_screen = SubScreen(size)
            elif event.type == pygame.MOUSEMOTION:
                (x, y) = pygame.mouse.get_pos()
                if draw_flag and y < size[1]:
                    active_screen.points.append((x, y))
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_BACKSPACE:
                    current_string = current_string[0:-1]
                elif key <= 127:
                    print chr(key)
                    current_string += chr(key)
        # 更新画面
        pygame.draw.rect(screen, (0, 0, 0), (20, 20 + size[1], 200, 50), 0)
        pygame.draw.rect(screen, (255, 255, 255), (22, 22 + size[1], 200 - 4, 50 - 4), 0)
        pygame.font.init()
        font_object = pygame.font.Font(None, 18)
        screen.blit(font_object.render(current_string, 1, (0, 0, 0)), (20, 20 + size[1], 200, 50))
        if len(active_screen.points) > 1:
            pygame.draw.lines(active_screen.screen, active_screen.color, not draw_flag, active_screen.points)
        for s in screen_list:
            screen.blit(pygame.Surface.convert_alpha(s.screen), (0, 0))
        screen.blit(pygame.Surface.convert_alpha(active_screen.screen), (0, 0))
        pygame.display.update()


if __name__ == '__main__':
    main()
