from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF
import math

class CustomGauge(QWidget):
    def __init__(self, title, min_val=0, max_val=1000, parent=None):
        super().__init__(parent)
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.setMinimumSize(120, 120)

    def set_value(self, val):
        new_val = max(self.min_val, min(self.max_val, val))
        if abs(self.value - new_val) > 0.1:  # Only repaint if changed significantly
            self.value = new_val
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)
        
        # Translate heavily to center
        painter.translate(width / 2.0, height / 2.0)
        # Scale to a standard [-100, 100] coordinate system
        painter.scale(side / 200.0, side / 200.0)

        # Draw circle background
        pen = QPen(QColor("#333333"))
        pen.setWidth(10)
        painter.setPen(pen)
        painter.drawArc(QRectF(-80.0, -80.0, 160.0, 160.0), -30 * 16, 240 * 16)

        # Draw filled arc based on value
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val) if self.max_val > self.min_val else 0
        pen_filled = QPen(QColor("#4CAF50"))
        if ratio > 0.8:
            pen_filled = QPen(QColor("#F44336")) # Red if high
        elif ratio > 0.6:
            pen_filled = QPen(QColor("#FF9800")) # Orange if medium-high
            
        pen_filled.setWidth(10)
        pen_filled.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_filled)
        painter.drawArc(QRectF(-80.0, -80.0, 160.0, 160.0), 210 * 16, int(-240 * ratio * 16))

        # Title
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(-80.0, 10.0, 160.0, 30.0), Qt.AlignmentFlag.AlignCenter, self.title)

        # Value
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(-80.0, 40.0, 160.0, 40.0), Qt.AlignmentFlag.AlignCenter, f"{self.value:.1f}")

        # Label/Unit (e.g., W)
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(QRectF(-80.0, -30.0, 160.0, 30.0), Qt.AlignmentFlag.AlignCenter, "W")
