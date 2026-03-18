import psutil
from PyQt6.QtCore import QThread, pyqtSignal
import time
import socket

class SysWorker(QThread):
    data_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        last_net = psutil.net_io_counters()
        last_time = time.time()
        
        while self.running:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
            # Try to get temp (might not work on all systems, especially Windows, but fine for RPi)
            try:
                temps = psutil.sensors_temperatures()
                cpu_temp = temps['coretemp'][0].current if 'coretemp' in temps else 0.0
            except:
                cpu_temp = 45.0 # Mock

            # RAM & Swap
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk
            disk = psutil.disk_usage('/')

            # Network
            time.sleep(1) # We sleep here to measure rate
            now = time.time()
            current_net = psutil.net_io_counters()
            dt = now - last_time
            
            up_speed = (current_net.bytes_sent - last_net.bytes_sent) * 8 / (1024 * 1024 * dt) # Mbps
            down_speed = (current_net.bytes_recv - last_net.bytes_recv) * 8 / (1024 * 1024 * dt)
            
            last_net = current_net
            last_time = now

            # Processes
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    procs.append((p.info['name'], p.info['cpu_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            procs = sorted(procs, key=lambda x: x[1] if x[1] else 0, reverse=True)[:5]
            
            data = {
                "cpu_cores": cpu_percent,
                "cpu_temp": cpu_temp,
                "ram_used": mem.used / (1024**3),
                "ram_total": mem.total / (1024**3),
                "swap_used": swap.used / (1024**3),
                "swap_total": swap.total / (1024**3),
                "disk_used": disk.used / (1024**3),
                "disk_total": disk.total / (1024**3),
                "net_up": up_speed,
                "net_down": down_speed,
                "top_procs": procs
            }
            
            self.data_updated.emit(data)

    def stop(self):
        self.running = False
        self.wait()
