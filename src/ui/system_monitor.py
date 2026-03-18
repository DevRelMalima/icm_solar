from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt

class SysProgressBar(QProgressBar):
    def __init__(self, color="#4CAF50"):
        super().__init__()
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                color: white;
                background-color: #2b2b2b;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        self.setFixedHeight(15)

class SystemMonitorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(280)
        self.setStyleSheet("background-color: #252526; border-left: 1px solid #333;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("System Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff; border: none;")
        layout.addWidget(title)

        # CPU Temp
        self.lbl_cpu_temp = QLabel("CPU Temp: --.- °C")
        self.lbl_cpu_temp.setStyleSheet("color: #FF9800; font-weight: bold; border: none;")
        layout.addWidget(self.lbl_cpu_temp)

        # CPU Usage Bars
        layout.addWidget(self._create_header("CPU Usage"))
        self.cpu_bars = []
        cpu_layout = QGridLayout()
        cpu_layout.setVerticalSpacing(5)
        for i in range(4):
            lbl = QLabel(f"Core {i+1}")
            lbl.setStyleSheet("color: #bbb; font-size: 10px; border: none;")
            bar = SysProgressBar(color="#2196F3")
            bar.setValue(0)
            self.cpu_bars.append(bar)
            cpu_layout.addWidget(lbl, i, 0)
            cpu_layout.addWidget(bar, i, 1)
        layout.addLayout(cpu_layout)

        # Memory (RAM & Swap)
        layout.addWidget(self._create_header("Memory"))
        
        self.lbl_ram = QLabel("RAM: -- / -- GB")
        self.lbl_ram.setStyleSheet("color: #bbb; font-size: 11px; border: none;")
        self.bar_ram = SysProgressBar(color="#9C27B0")
        
        self.lbl_swap = QLabel("Swap: -- / -- GB")
        self.lbl_swap.setStyleSheet("color: #bbb; font-size: 11px; border: none;")
        self.bar_swap = SysProgressBar(color="#7B1FA2")
        
        layout.addWidget(self.lbl_ram)
        layout.addWidget(self.bar_ram)
        layout.addWidget(self.lbl_swap)
        layout.addWidget(self.bar_swap)

        # Disk
        layout.addWidget(self._create_header("Disk (/home)"))
        self.lbl_disk = QLabel("Used: -- / -- GB")
        self.lbl_disk.setStyleSheet("color: #bbb; font-size: 11px; border: none;")
        self.bar_disk = SysProgressBar(color="#4CAF50")
        layout.addWidget(self.lbl_disk)
        layout.addWidget(self.bar_disk)

        # Network
        layout.addWidget(self._create_header("Network (Mbps)"))
        self.lbl_net_up = QLabel("↑ Up: -- Mbps")
        self.lbl_net_up.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold; border: none;")
        self.lbl_net_down = QLabel("↓ Down: -- Mbps")
        self.lbl_net_down.setStyleSheet("color: #2196F3; font-size: 12px; font-weight: bold; border: none;")
        layout.addWidget(self.lbl_net_up)
        layout.addWidget(self.lbl_net_down)

        # Processes
        layout.addWidget(self._create_header("Top Processes"))
        self.lbl_procs = QLabel("1. --\n2. --\n3. --\n4. --\n5. --")
        self.lbl_procs.setStyleSheet("color: #bbb; font-size: 11px; border: none; font-family: monospace;")
        layout.addWidget(self.lbl_procs)

        layout.addStretch()

    def _create_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px; margin-top: 10px; border: none;")
        return lbl

    def update_sys_data(self, data):
        self.lbl_cpu_temp.setText(f"CPU Temp: {data.get('cpu_temp', 0):.1f} °C")
        
        cores = data.get('cpu_cores', [])
        for i, bar in enumerate(self.cpu_bars):
            if i < len(cores):
                bar.setValue(int(cores[i]))
                
        ram_u = data.get('ram_used', 0)
        ram_t = data.get('ram_total', 1)
        self.lbl_ram.setText(f"RAM: {ram_u:.1f} / {ram_t:.1f} GB")
        self.bar_ram.setValue(int(ram_u / ram_t * 100) if ram_t else 0)
        
        sw_u = data.get('swap_used', 0)
        sw_t = data.get('swap_total', 1)
        self.lbl_swap.setText(f"Swap: {sw_u:.1f} / {sw_t:.1f} GB")
        if sw_t > 0:
            self.bar_swap.setValue(int(sw_u / sw_t * 100))
            
        d_u = data.get('disk_used', 0)
        d_t = data.get('disk_total', 1)
        self.lbl_disk.setText(f"Used: {d_u:.1f} / {d_t:.1f} GB")
        self.bar_disk.setValue(int(d_u / d_t * 100) if d_t else 0)
        
        self.lbl_net_up.setText(f"↑ Up: {data.get('net_up', 0):.2f} Mbps")
        self.lbl_net_down.setText(f"↓ Down: {data.get('net_down', 0):.2f} Mbps")
        
        procs = data.get('top_procs', [])
        proc_str = "\n".join([f"{i+1}. {p[0][:12]:<12} {p[1]:.1f}%" for i, p in enumerate(procs)])
        self.lbl_procs.setText(proc_str)
