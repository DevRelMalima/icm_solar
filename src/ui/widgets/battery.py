from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRect

class BatteryGraphic(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.soc = 0  # State of Charge %
        self.setMinimumSize(80, 120)

    def set_soc(self, val):
        new_val = max(0, min(100, val))
        if self.soc != new_val:
            self.soc = new_val
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        padding = 10
        bw = width - padding * 2
        bh = height - padding * 2 - 10 # 10px for the nub at top

        # Draw nub
        painter.setBrush(QBrush(QColor("#555555")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(width // 2 - 10, padding, 20, 10, 2.0, 2.0)

        # Draw battery outline
        pen = QPen(QColor("#FFFFFF"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(padding, padding + 10, bw, bh, 5.0, 5.0)

        # Draw fill level
        fill_height = int(bh * (self.soc / 100.0))
        if self.soc > 20:
            fill_color = QColor("#4CAF50")
        else:
            fill_color = QColor("#F44336")
            
        painter.setBrush(QBrush(fill_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # We need to calculate y-offset so it fills from the bottom up
        painter.drawRoundedRect(padding + 2, padding + 10 + (bh - fill_height) + 2, bw - 4, max(0, fill_height - 4), 3.0, 3.0)

        # Draw text %
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(QRect(padding, padding + 10, bw, bh), Qt.AlignmentFlag.AlignCenter, f"{self.soc}%")
