from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import numpy as np


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.points = []  # 存储点
        self.lines = []  # 存储线段
        self.start_point = None
        self.current_point = None
        self.is_drawing = False

        # 添加旋转相关变量
        self.last_pos = QPoint()
        self.xRotation = 0
        self.yRotation = 0
        self.zRotation = 0

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 设置黑色背景
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glEnable(GL_LIGHTING)  # 启用光照
        glEnable(GL_LIGHT0)  # 启用光源0
        glEnable(GL_COLOR_MATERIAL)  # 启用材质颜色跟踪

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 设置相机位置
        gluLookAt(0, 0, 5,  # 相机位置
                  0, 0, 0,  # 观察点
                  0, 1, 0)  # 上方向

        # 应用旋转
        glRotated(self.xRotation / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRotation / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRotation / 16.0, 0.0, 0.0, 1.0)

        # 绘制坐标轴
        glBegin(GL_LINES)
        # X轴 (红色)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        # Y轴 (绿色)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        # Z轴 (蓝色)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()

        # 绘制已保存的线段
        glColor3f(1.0, 1.0, 1.0)  # 设置白色
        glBegin(GL_LINES)
        for line in self.lines:
            glVertex3fv(line[0])
            glVertex3fv(line[1])
        glEnd()

        # 绘制当前正在画的线段
        if self.start_point and self.current_point:
            glColor3f(1.0, 1.0, 0.0)  # 设置黄色
            glBegin(GL_LINES)
            glVertex3fv(self.start_point)
            glVertex3fv(self.current_point)
            glEnd()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()
        if event.button() == Qt.LeftButton:
            # 获取归一化设备坐标
            x = event.x()
            y = event.y()
            # 将屏幕坐标转换为3D空间坐标
            world_pos = self.screen_to_world(x, y)

            if not self.is_drawing:
                self.start_point = world_pos
                self.current_point = world_pos
                self.is_drawing = True
            else:
                self.lines.append((self.start_point, world_pos))
                self.start_point = None
                self.current_point = None
                self.is_drawing = False
            self.update()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if event.buttons() & Qt.RightButton:
            # 右键拖动进行旋转
            self.setXRotation(self.xRotation + 8 * dy)
            self.setYRotation(self.yRotation + 8 * dx)
        elif self.is_drawing:
            # 左键绘制线段
            x = event.x()
            y = event.y()
            self.current_point = self.screen_to_world(x, y)

        self.last_pos = event.pos()
        self.update()

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRotation:
            self.xRotation = angle
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRotation:
            self.yRotation = angle
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRotation:
            self.zRotation = angle
            self.update()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def screen_to_world(self, x, y):
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        win_y = viewport[3] - y

        z = 0.5  # 假设点在z=0.5平面上
        wx, wy, wz = gluUnProject(x, win_y, z, modelview, projection, viewport)
        return [wx, wy, wz]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.gl_widget = GLWidget()
        self.setCentralWidget(self.gl_widget)
        self.setWindowTitle("3D Line Drawing")
        self.resize(800, 600)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())