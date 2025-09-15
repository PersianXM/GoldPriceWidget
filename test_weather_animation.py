#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight test to prototype the weather icon animation.
- Shows a small window with a weather icon and a label.
- On each simulated update, the icon animates from below (y-offset) to its final position,
  while fading in from 0 to 1 opacity.

Close the window to end the test.
"""
import sys
import time
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray, QPoint, QEasingCurve
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

# Reuse the SVG icons from app context (inline minimal sun icon for the test)
SUN_ICON_SVG = (
    """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="sun-gradient" cx="50%" cy="50%" r="50%">
<stop offset="0%" style="stop-color:#FFF176;stop-opacity:1"/>
<stop offset="100%" style="stop-color:#FF9800;stop-opacity:1"/>
</radialGradient></defs>
<circle cx="12" cy="12" r="5" fill="url(#sun-gradient)"/>
<path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" 
stroke="url(#sun-gradient)" stroke-width="2" fill="none"/>
</svg>
"""
).encode("utf-8")

class SvgIconLabel(QLabel):
    def __init__(self, svg_data: bytes, size: QSize = QSize(22, 22), parent=None):
        super().__init__(parent)
        self._svg_data = svg_data
        self._size = size
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")
        self.setPixmap(self._render_svg_to_pixmap(self._svg_data, self._size))

    def _render_svg_to_pixmap(self, svg_data, size=QSize(22, 22)):
        renderer = QSvgRenderer(QByteArray(svg_data))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

class WeatherAnimWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Animation Test")
        self.setFixedSize(280, 80)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Widgets
        # A holder to allow absolute positioning of the icon for animation
        self.icon_holder = QWidget(self)
        self.icon_holder.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.icon_holder.setStyleSheet("background-color: transparent;")
        self.icon_holder.setFixedSize(30, 48)  # enough height to animate from bottom

        # Icon inside the holder (absolute positioning)
        self.icon_label = SvgIconLabel(SUN_ICON_SVG, QSize(22, 22), parent=self.icon_holder)
        self.text_label = QLabel("30°C")
        self.text_label.setStyleSheet("color: white; background-color: transparent; font-size: 16px;")

        # Opacity effect for fade-in
        self.opacity_effect = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.opacity_effect)

        # Layout
        row = QHBoxLayout()
        row.setContentsMargins(20, 10, 20, 10)
        row.setSpacing(10)
        row.addStretch()
        row.addWidget(self.icon_holder)
        row.addWidget(self.text_label)
        row.addStretch()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(row)
        self.setStyleSheet("QWidget { background-color: rgba(0,0,0,70); border-radius: 10px; }")

        # Center icon initially in the holder
        self._center_icon()

        # Animate once on startup, then every few seconds to simulate updates
        QTimer.singleShot(300, self.play_icon_animation)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_icon_animation)
        self.timer.start(5000)

    def play_icon_animation(self):
        # Compute start (bottom-center) and end (vertical center) positions in holder coords
        holder_w = self.icon_holder.width()
        holder_h = self.icon_holder.height()
        icon_w = self.icon_label.width()
        icon_h = self.icon_label.height()

        start_x = (holder_w - icon_w) // 2
        start_y = holder_h - icon_h  # bottom edge
        end_x = start_x
        end_y = (holder_h - icon_h) // 2  # vertical middle

        # Reset starting state
        self.icon_label.move(start_x, start_y)
        self.opacity_effect.setOpacity(0.0)

        # Property animations: position (slide up) and opacity (fade in)
        from PyQt6.QtCore import QPropertyAnimation

        # Slide up
        pos_anim = QPropertyAnimation(self.icon_label, b"pos", self)
        pos_anim.setDuration(500)
        pos_anim.setStartValue(QPoint(start_x, start_y))
        pos_anim.setEndValue(QPoint(end_x, end_y))
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade in
        op_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        op_anim.setDuration(500)
        op_anim.setStartValue(0.0)
        op_anim.setEndValue(1.0)
        op_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Keep refs so GC doesn't stop animations
        self._anims = [pos_anim, op_anim]

        pos_anim.start()
        op_anim.start()

    def _center_icon(self):
        # Place icon in the center of the holder (final resting position)
        holder_w = self.icon_holder.width()
        holder_h = self.icon_holder.height()
        icon_w = self.icon_label.width()
        icon_h = self.icon_label.height()
        cx = (holder_w - icon_w) // 2
        cy = (holder_h - icon_h) // 2
        self.icon_label.move(cx, cy)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WeatherAnimWindow()
    w.show()
    sys.exit(app.exec())
