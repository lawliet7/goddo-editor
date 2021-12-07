from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QStyleOptionSlider, QStyle


class ClickSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.opt = QStyleOptionSlider()
        self.initStyleOption(self.opt)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)

        # needs to be reinitialized when resized to calculate position properly
        self.initStyleOption(self.opt)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            val = self.pixel_pos_to_range_value(event.pos())
            self.setValue(val)

    def pixel_pos_to_range_value(self, pos):

        gr = self.style().subControlRect(QStyle.CC_Slider, self.opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, self.opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - slider_min,
                                              slider_max - slider_min, self.opt.upsideDown)

    def slider_value_to_pct(self, value):
        return 100 / self.maximum() * value / 100

    def pct_to_slider_value(self, pct):
        return int(round(pct / (100 / self.maximum()) * 100))
