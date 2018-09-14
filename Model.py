# coding=utf-8
import pygame
import Tools


class Shape(object):
    def __init__(self, color, info):
        """
        形状父类
        :param color: 颜色
        :param info: 标注信息
        """
        self.color = color
        self.info = info

    def draw(self, screen, active):
        """
        绘制形状
        :param screen: 用于绘制的pygame.Surface
        :param active: 当前形状是否被选中
        """
        pass

    def get_shape(self):
        """
        获取形状名称
        :return: 返回形状名称
        """
        pass

    def judge_point(self, point):
        """
        判断点是否在形状内部
        :param point: 点坐标(x, y)
        :return: Boolean
        """
        pass


class Triangle(Shape):
    def __init__(self, points, color, info):
        """
        三角形
        :param points: 三个顶点的坐标
        :param color: 颜色
        :param info: 标注
        """
        Shape.__init__(self, color, info)
        self.points = points

    def draw(self, screen, active):
        pygame.draw.lines(screen, self.color, True, self.points, 3 if active else 1)

    def get_shape(self):
        return "三角形"

    def judge_point(self, point):
        x, y = Tools.decompose(self.points[1], self.points[2], point, origin=self.points[0])
        return 0 < x < 1 and 0 < y < 1 and 0 < x + y < 1


class Rect(Shape):
    def __init__(self, points, color, info):
        """
        矩形（包括长方形和正方形）
        :param points: 四个顶点的坐标
        :param color: 颜色
        :param info: 标注
        """
        Shape.__init__(self, color, info)
        self.points = points

    def draw(self, screen, active):
        pygame.draw.lines(screen, self.color, True, self.points, 3 if active else 1)

    def get_shape(self):
        if Tools.get_distance(self.points[0], self.points[1]) - Tools.get_distance(self.points[0], self.points[3]) < 1:
            return "正方形"
        else:
            return "长方形"

    def judge_point(self, point):
        x, y = Tools.decompose(self.points[1], self.points[3], point, origin=self.points[0])
        return 0 < x < 1 and 0 < y < 1


class Circle(Shape):
    def __init__(self, pos, radius, color, info):
        """
        圆形
        :param pos: 圆心位置
        :param radius: 半径
        :param color: 颜色
        :param info: 标注信息
        """
        Shape.__init__(self, color, info)
        self.pos = pos
        self.radius = radius

    def draw(self, screen, active):
        pygame.draw.circle(screen, self.color, self.pos, self.radius, 3 if active else 1)

    def get_shape(self):
        return "圆形"

    def judge_point(self, point):
        return Tools.get_distance(point, self.pos) < self.radius
