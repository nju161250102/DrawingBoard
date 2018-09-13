# coding=utf-8
import pygame
import math


class Shape(object):
    def __init__(self, color, info):
        self.color = color
        self.info = info

    def draw(self, screen, active):
        pass

    def get_shape(self):
        pass

    def judge_point(self, point):
        pass


class Triangle(Shape):
    def __init__(self, points, color, info):
        Shape.__init__(self, color, info)
        self.points = points

    def draw(self, screen, active):
        pygame.draw.lines(screen, self.color, True, self.points, 3 if active else 1)

    def get_shape(self):
        return "三角形"

    def judge_point(self, point):
        t1 = self._cross_product(point, self.points[0], self.points[1])
        t2 = self._cross_product(point, self.points[1], self.points[2])
        t3 = self._cross_product(point, self.points[2], self.points[0])
        return (t1 < 0 and t2 < 0 and t3 < 0) or (t1 > 0 and t2 > 0 and t3 > 0)

    @staticmethod
    def _cross_product(p, point_a, point_b):
        return (point_a[0] - p[0])*(point_b[1] - p[1]) - (point_a[1] - p[1])*(point_b[0] - p[0])


class Rect(Shape):
    def __init__(self, pos, size, color, info):
        Shape.__init__(self, color, info)
        self.pos = pos  # (left, top)
        self.size = size  # (width, height)

    def draw(self, screen, active):
        pygame.draw.rect(screen, self.color, pygame.rect.Rect(self.pos, self.size), 3 if active else 1)

    def get_shape(self):
        return "矩形"

    def judge_point(self, point):
        return (0 < point[0] - self.pos[0] < self.size[0]) and (0 < point[1] - self.pos[1] < self.size[1])


class Square(Shape):
    def __init__(self, pos, side, color, info):
        Shape.__init__(self, color, info)
        self.pos = pos
        self.side = side

    def draw(self, screen, active):
        pygame.draw.rect(screen, self.color, pygame.rect.Rect(self.pos, (self.side, self.side)), 3 if active else 1)

    def get_shape(self):
        return "正方形"

    def judge_point(self, point):
        return (0 < point[0] - self.pos[0] < self.side) and (0 < point[1] - self.pos[1] < self.side)


class Circle(Shape):
    def __init__(self, pos, radius, color, info):
        Shape.__init__(self, color, info)
        self.pos = pos
        self.radius = radius

    def draw(self, screen, active):
        pygame.draw.circle(screen, self.color, self.pos, self.radius, 3 if active else 1)

    def get_shape(self):
        return "圆形"

    def judge_point(self, point):
        return math.sqrt((point[0] - self.pos[0])**2 + (point[1] - self.pos[1])**2) < self.radius
