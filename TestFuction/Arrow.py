import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt


class ArrowWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Draw Arrow with PyQt5')
        self.setGeometry(300, 300, 400, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置画笔
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # 箭头参数
        x, y = 100, -100
        h, m = 20, 5

        # 计算箭头的坐标
        arrow_body_start = (x, y - h)
        arrow_body_end = (x, y)
        arrow_head_left = (x - m, y - m)
        arrow_head_right = (x + m, y - m)

        # 绘制箭头主体
        painter.drawLine(arrow_body_start[0], -arrow_body_start[1], arrow_body_end[0], -arrow_body_end[1])

        # 绘制箭头斜线
        painter.drawLine(arrow_body_end[0], -arrow_body_end[1], arrow_head_left[0], -arrow_head_left[1])
        painter.drawLine(arrow_body_end[0], -arrow_body_end[1], arrow_head_right[0], -arrow_head_right[1])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ArrowWidget()
    window.show()
    sys.exit(app.exec_())
