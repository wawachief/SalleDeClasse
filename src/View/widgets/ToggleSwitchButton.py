# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

from PySide2.QtCore import Qt, QPropertyAnimation, QSize, QPoint, Signal
from PySide2.QtGui import QPainter, QLinearGradient, QColor, QPen, QRadialGradient, QBrush, QPixmap, QImage
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout

from src.assets_manager import ASSETS_PATH, ICONS_PATH


class ToggleSwitchButton(QWidget):

    def __init__(self, parent, on_icon: str, off_icon: str, callback):
        """
        Creates a widget that contains a toggle switch button, and a state label above it

        :param parent: parent widget
        :param on_icon: Icon to display when toggle is ON
        :param off_icon: Icon to display when toggle is OFF
        :param callback: Callback to trigger upon switch click
        """
        QWidget.__init__(self)

        self.on = f"{ASSETS_PATH}{ICONS_PATH}{on_icon}.png"
        self.off = f"{ASSETS_PATH}{ICONS_PATH}{off_icon}.png"

        # Widtgets
        self.switch = SwitchButton(parent, "", 10, "", 30, 45)
        # 2 actions to perform
        self.switch.clicked.connect(callback)
        self.switch.clicked.connect(lambda v: self.lab.setPixmap(QPixmap(QImage(self.on if v else self.off))))

        self.lab = QLabel()
        self.lab.setFixedSize(35, 35)
        self.lab.setScaledContents(True)
        self.lab.setPixmap(QPixmap(QImage(self.off)))

        # A click on the label will also trigger the toggle switch
        self.lab.mousePressEvent = self.switch.mousePressEvent

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.lab)
        layout.setAlignment(self.lab, Qt.AlignCenter)
        layout.addWidget(self.switch)
        layout.setAlignment(self.switch, Qt.AlignCenter)
        self.setLayout(layout)


# --- Following widget found on: https://stackoverflow.com/a/51023362 ---
class SwitchButton(QWidget):

    clicked = Signal(bool)

    def __init__(self, parent=None, w1="Yes", l1=12, w2="No", l2=33, width=60):
        super(SwitchButton, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__labeloff = QLabel(self)
        self.__labeloff.setText(w2)
        self.__labeloff.setStyleSheet("""color: rgb(120, 120, 120); font-weight: bold;""")
        self.__background  = Background(self)
        self.__labelon = QLabel(self)
        self.__labelon.setText(w1)
        self.__labelon.setStyleSheet("""color: rgb(255, 255, 255); font-weight: bold;""")
        self.__circle      = Circle(self)
        self.__circlemove  = None
        self.__ellipsemove = None
        self.__enabled     = True
        self.__duration    = 100
        self.__value       = False
        self.setFixedSize(width, 24)

        self.__background.resize(20, 20)
        self.__background.move(2, 2)
        self.__circle.move(2, 2)
        self.__labelon.move(l1, 5)
        self.__labeloff.move(l2, 5)

    def setDuration(self, time):
        self.__duration = time

    def mousePressEvent(self, event):
        if not self.__enabled:
            return

        self.__circlemove = QPropertyAnimation(self.__circle, b"pos")
        self.__circlemove.setDuration(self.__duration)

        self.__ellipsemove = QPropertyAnimation(self.__background, b"size")
        self.__ellipsemove.setDuration(self.__duration)

        xs = 2
        y  = 2
        xf = self.width()-22
        hback = 20
        isize = QSize(hback, hback)
        bsize = QSize(self.width()-4, hback)
        if self.__value:
            xf = 2
            xs = self.width()-22
            bsize = QSize(hback, hback)
            isize = QSize(self.width()-4, hback)

        self.__circlemove.setStartValue(QPoint(xs, y))
        self.__circlemove.setEndValue(QPoint(xf, y))

        self.__ellipsemove.setStartValue(isize)
        self.__ellipsemove.setEndValue(bsize)

        self.__circlemove.start()
        self.__ellipsemove.start()
        self.__value = not self.__value

        self.clicked.emit(self.__value)  # Emits current value

    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(Qt.NoPen)
        qp.setPen(pen)
        qp.setBrush(QColor(120, 120, 120))
        qp.drawRoundedRect(0, 0, s.width(), s.height(), 12, 12)
        lg = QLinearGradient(35, 30, 35, 0)
        lg.setColorAt(0, QColor(210, 210, 210, 255))
        lg.setColorAt(0.25, QColor(255, 255, 255, 255))
        lg.setColorAt(0.82, QColor(255, 255, 255, 255))
        lg.setColorAt(1, QColor(210, 210, 210, 255))
        qp.setBrush(lg)
        qp.drawRoundedRect(1, 1, s.width()-2, s.height()-2, 10, 10)

        qp.setBrush(QColor(210, 210, 210))
        qp.drawRoundedRect(2, 2, s.width() - 4, s.height() - 4, 10, 10)

        if self.__enabled:
            lg = QLinearGradient(50, 30, 35, 0)
            lg.setColorAt(0, QColor(230, 230, 230, 255))
            lg.setColorAt(0.25, QColor(255, 255, 255, 255))
            lg.setColorAt(0.82, QColor(255, 255, 255, 255))
            lg.setColorAt(1, QColor(230, 230, 230, 255))
            qp.setBrush(lg)
            qp.drawRoundedRect(3, 3, s.width() - 6, s.height() - 6, 7, 7)
        else:
            lg = QLinearGradient(50, 30, 35, 0)
            lg.setColorAt(0, QColor(200, 200, 200, 255))
            lg.setColorAt(0.25, QColor(230, 230, 230, 255))
            lg.setColorAt(0.82, QColor(230, 230, 230, 255))
            lg.setColorAt(1, QColor(200, 200, 200, 255))
            qp.setBrush(lg)
            qp.drawRoundedRect(3, 3, s.width() - 6, s.height() - 6, 7, 7)
        qp.end()


class Circle(QWidget):
    def __init__(self, parent=None):
        super(Circle, self).__init__(parent)
        self.__enabled = True
        self.setFixedSize(20, 20)

    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(120, 120, 120))
        qp.drawEllipse(0, 0, 20, 20)
        rg = QRadialGradient(int(self.width() / 2), int(self.height() / 2), 12)
        rg.setColorAt(0, QColor(255, 255, 255))
        rg.setColorAt(0.6, QColor(255, 255, 255))
        rg.setColorAt(1, QColor(205, 205, 205))
        qp.setBrush(QBrush(rg))
        qp.drawEllipse(1, 1, 18, 18)

        qp.setBrush(QColor(210, 210, 210))
        qp.drawEllipse(2, 2, 16, 16)

        if self.__enabled:
            lg = QLinearGradient(3, 18, 20, 4)
            lg.setColorAt(0, QColor(255, 255, 255, 255))
            lg.setColorAt(0.55, QColor(230, 230, 230, 255))
            lg.setColorAt(0.72, QColor(255, 255, 255, 255))
            lg.setColorAt(1, QColor(255, 255, 255, 255))
            qp.setBrush(lg)
            qp.drawEllipse(3, 3, 14, 14)
        else:
            lg = QLinearGradient(3, 18, 20, 4)
            lg.setColorAt(0, QColor(230, 230, 230))
            lg.setColorAt(0.55, QColor(210, 210, 210))
            lg.setColorAt(0.72, QColor(230, 230, 230))
            lg.setColorAt(1, QColor(230, 230, 230))
            qp.setBrush(lg)
            qp.drawEllipse(3, 3, 14, 14)
        qp.end()


class Background(QWidget):
    def __init__(self, parent=None):
        super(Background, self).__init__(parent)
        self.__enabled = True
        self.setFixedHeight(20)

    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(Qt.NoPen)
        qp.setPen(pen)
        qp.setBrush(QColor(154, 205, 50))
        if self.__enabled:
            qp.setBrush(QColor(154, 190, 50))
            qp.drawRoundedRect(0, 0, s.width(), s.height(), 10, 10)

            lg = QLinearGradient(0, 25, 70, 0)
            lg.setColorAt(0, QColor(154, 184, 50))
            lg.setColorAt(0.35, QColor(154, 210, 50))
            lg.setColorAt(0.85, QColor(154, 184, 50))
            qp.setBrush(lg)
            qp.drawRoundedRect(1, 1, s.width() - 2, s.height() - 2, 8, 8)
        else:
            qp.setBrush(QColor(150, 150, 150))
            qp.drawRoundedRect(0, 0, s.width(), s.height(), 10, 10)

            lg = QLinearGradient(5, 25, 60, 0)
            lg.setColorAt(0, QColor(190, 190, 190))
            lg.setColorAt(0.35, QColor(230, 230, 230))
            lg.setColorAt(0.85, QColor(190, 190, 190))
            qp.setBrush(lg)
            qp.drawRoundedRect(1, 1, s.width() - 2, s.height() - 2, 8, 8)
        qp.end()
