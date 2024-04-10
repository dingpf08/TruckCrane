from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QPixmap
from PyQt5.QtCore import QRectF, Qt
import sys

class TextureShape(QGraphicsItem):
    def __init__(self, parent=None):
        super(TextureShape, self).__init__(parent)
        # 设置图形项的边界矩形
        self.rect = QRectF(0, 0, 1000, 1000)

    def boundingRect(self):
        # 返回图形项的边界矩形
        return self.rect

    def paint(self, painter, option, widget=None):
        # 加载图片作为纹理
        texture = QPixmap("texture.png")
        # 设置纹理样式的画刷
        painter.setBrush(QBrush(texture))
        # 设置边界
        painter.setPen(QPen(QColor('black'), 2))
        # 绘制矩形（或其他闭合图形）
        painter.drawRect(self.rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    # 添加自定义的图形项到场景中
    shape = TextureShape()
    scene.addItem(shape)
    view.show()
    sys.exit(app.exec_())
