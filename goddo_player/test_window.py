import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout

from goddo_player.sliders2 import VolumeControl

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QWidget()
    layout = QHBoxLayout()
    volume_controls = VolumeControl()
    # btn = QPushButton("Hello World!")
    layout.addWidget(volume_controls)
    w.setLayout(layout)
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()
    sys.exit(app.exec_())



