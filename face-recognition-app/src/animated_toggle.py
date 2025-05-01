from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPainter, QColor


class AnimatedToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)
        self.setCursor(Qt.PointingHandCursor)
        self._animation = QPropertyAnimation(self, b"geometry", self)
        self._animation.setDuration(200)
        self._checked_color = QColor("#001f3f")  # Orange color for checked state
        self._unchecked_color = QColor("#ddd")  # Gray color for unchecked state
        self._circle_color = QColor("#ffffff")  # White color for the circle
        self._circle_position = 2  # Initial position of the circle

        self.stateChanged.connect(self.start_animation)

    def start_animation(self):
        if self.isChecked():
            self._circle_position = self.width() - 23  # Move to the right
        else:
            self._circle_position = 2  # Move to the left
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background
        rect = self.rect()
        painter.setBrush(self._checked_color if self.isChecked() else self._unchecked_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        # Draw the circle
        circle_rect = QRect(self._circle_position, 2, 21, 21)
        painter.setBrush(self._circle_color)
        painter.drawEllipse(circle_rect)

    def mousePressEvent(self, event):
        # Toggle the state when the toggle box is clicked
        self.setChecked(not self.isChecked())
        super().mousePressEvent(event)