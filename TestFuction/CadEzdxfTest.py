import ezdxf
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtGui import QPainterPath, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QTimer
import sys


class DXFViewer(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene().sceneRect(), Qt.IgnoreAspectRatio)


def load_dxf_and_draw(filename, scene):
    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()
    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            path = QPainterPath()
            path.moveTo(start.x, start.y)
            path.lineTo(end.x, end.y)
            # 增加线条宽度，并设置颜色为红色
            scene.addPath(path, QPen(QColor(255, 0, 0), 20))
        elif entity.dxftype() == 'ARC':
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            path = QPainterPath()
            rect = QRectF(center.x - radius, center.y - radius, 2 * radius, 2 * radius)
            path.arcMoveTo(rect, start_angle)
            path.arcTo(rect, start_angle, end_angle - start_angle)
            # 增加线条宽度，并设置颜色为红色
            scene.addPath(path, QPen(QColor(255, 0, 0), 4))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    # 设置场景背景色为浅灰色，以提高对比度
    scene.setBackgroundBrush(QColor(230, 230, 230))
    view = DXFViewer(scene)

    dxf_file = "楼梯2.dxf"  # 确保路径是正确的
    load_dxf_and_draw(dxf_file, scene)

    view.show()
    # 使用 QTimer 来延迟 fitInView 的调用
    QTimer.singleShot(0, lambda: view.fitInView(scene.sceneRect(), Qt.IgnoreAspectRatio))

    sys.exit(app.exec_())
