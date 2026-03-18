import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from core.threads.hardware_worker import HardwareWorker
from core.threads.sys_worker import SysWorker
from core.db import DBManager

class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Logo Space
        self.logo_label = QLabel("LOGO")
        self.logo_label.setStyleSheet("font-weight: bold; font-size: 24px; color: #4CAF50;")
        layout.addWidget(self.logo_label)
        layout.addStretch(1)

        # Status Indicators
        self.btn_stop_start = QPushButton("Stop/Start")
        self.btn_stop_start.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        
        self.lbl_runtime = QLabel("00:00:00:00")
        self.lbl_runtime.setStyleSheet("background-color: #3d3d3d; padding: 10px; border-radius: 5px; font-weight: bold;")
        
        self.lbl_pi_temp = QLabel("PI Temp: --.-°C")
        self.lbl_pi_temp.setStyleSheet("background-color: #3d3d3d; padding: 10px; border-radius: 5px; font-weight: bold;")
        
        self.btn_change_mode = QPushButton("Change Inverter Mode")
        self.btn_change_mode.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        
        self.lbl_power_source = QLabel("Source: Battery/Solar")
        self.lbl_power_source.setStyleSheet("background-color: #FF9800; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")

        layout.addWidget(self.btn_stop_start)
        layout.addWidget(self.lbl_runtime)
        layout.addWidget(self.lbl_pi_temp)
        layout.addWidget(self.btn_change_mode)
        layout.addWidget(self.lbl_power_source)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solar/Inverter Monitoring Dashboard")
        self.resize(1280, 800)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Top Header
        self.header = HeaderWidget()
        self.main_layout.addWidget(self.header)

        # Main Content Area (Tabs + Right Panel)
        from PyQt6.QtWidgets import QSplitter
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.content_splitter)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { background: #333; color: white; padding: 10px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #4CAF50; font-weight: bold; }
        """)
        self.setup_tabs()
        self.content_splitter.addWidget(self.tabs)

        # Right-Side System Monitor Panel
        from ui.system_monitor import SystemMonitorPanel
        self.sys_monitor_panel = SystemMonitorPanel()
        self.content_splitter.addWidget(self.sys_monitor_panel)
        
        # Set stretch factor so Tabs take majority of space
        self.content_splitter.setStretchFactor(0, 4)
        self.content_splitter.setStretchFactor(1, 1)

        # Thread Setup & Data Integration
        self.latest_hw_data = {}
        self.db = DBManager()
        
        self.hw_worker = HardwareWorker()
        self.hw_worker.data_updated.connect(self.on_hardware_data)
        self.hw_worker.start()
        
        self.sys_worker = SysWorker()
        self.sys_worker.data_updated.connect(self.sys_monitor_panel.update_sys_data)
        self.sys_worker.start()
        
        self.db_timer = QTimer(self)
        self.db_timer.timeout.connect(self.save_to_db)
        self.db_timer.start(60000) # Save every minute

    def on_hardware_data(self, data):
        self.latest_hw_data = data
        if hasattr(self, 'dashboard1'):
            self.dashboard1.update_hardware_data(data)
            
    def save_to_db(self):
        if self.latest_hw_data:
            self.db.insert_metrics(self.latest_hw_data)

    def closeEvent(self, event):
        self.hw_worker.stop()
        self.sys_worker.stop()
        self.db.close()
        event.accept()

    def setup_tabs(self):
        tab_names = [
            "Dashboard 1", "Dashboard 2", "Inverter Values", "Pylontech", 
            "BMS Info", "Power Production", "Thread Info", "Settings", 
            "Power Management", "Log Info"
        ]
        
        from ui.dashboard import DashboardTab
        
        self.dashboard1 = DashboardTab()
        self.tabs.addTab(self.dashboard1, "Dashboard 1")

        for name in tab_names[1:]:
            tab = QWidget()
            layout = QVBoxLayout(tab)
            label = QLabel(f"{name} Content")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 24px; color: #888;")
            layout.addWidget(label)
            self.tabs.addTab(tab, name)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Initialize main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
