from rezgui.qt import QtCore, QtGui
from rezgui.util import create_pane


class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.interactive = True
        self.press_pos = None

    def mousePressEvent(self, event):
        if self.interactive:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.press_pos = QtGui.QCursor.pos()
            self.press_scroll_pos = self._scroll_pos()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self.interactive:
            self.unsetCursor()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.interactive:
            pos = QtGui.QCursor.pos()
            pos_delta = pos - self.press_pos
            scroll_pos = self.press_scroll_pos - pos_delta
            self._set_scroll_pos(scroll_pos)
            event.accept()
        else:
            event.ignore()

    def wheelEvent(self, event):
        if self.fit:
            event.ignore()
        else:
            scale = 1.0 + (event.delta() * 0.001)
            self.scale(scale, scale)
            event.accept()

    def _scroll_pos(self):
        hs = self.horizontalScrollBar()
        vs = self.verticalScrollBar()
        return QtCore.QPoint(hs.value(), vs.value())

    def _set_scroll_pos(self, pos):
        hs = self.horizontalScrollBar()
        vs = self.verticalScrollBar()
        hs.setValue(pos.x())
        vs.setValue(pos.y())


class ImageViewerWidget(QtGui.QWidget):
    def __init__(self, image_file, parent=None):
        super(ImageViewerWidget, self).__init__(parent)
        self.fit = False
        self.prev_scale = 1.0

        self.scene = QtGui.QGraphicsScene()
        image = QtGui.QPixmap(image_file)
        self.image_item = self.scene.addPixmap(image)
        self.image_item.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.view = GraphicsView(self.scene)

        create_pane([self.view], False, parent_widget=self)
        self.view.setRenderHints(QtGui.QPainter.Antialiasing
                                 | QtGui.QPainter.SmoothPixmapTransform)
        self.view.show()

    def resizeEvent(self, event):
        if self.fit:
            self._fit_in_view()
            event.accept()
        else:
            event.ignore()

    def fit_to_window(self, enabled):
        if enabled != self.fit:
            self.fit = enabled
            self.view.interactive = not enabled
            current_scale = self.view.transform().m11()

            if enabled:
                self.prev_scale = current_scale
                self._fit_in_view()
            else:
                factor = self.prev_scale / current_scale
                self.view.scale(factor, factor)

    def _fit_in_view(self):
        if self.fit:
            self.view.fitInView(self.image_item, QtCore.Qt.KeepAspectRatio)
