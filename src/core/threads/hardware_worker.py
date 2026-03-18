from PyQt6.QtCore import QThread, pyqtSignal
import time
import random

class HardwareWorker(QThread):
    data_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        # Setup Modbus/Serial connections here
        # E.g. client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600)
        # client.connect()
        while self.running:
            # Poll hardware (Mocking data for now)
            # data = client.read_holding_registers(0x00, 10, unit=1)
            
            mock_data = {
                "grid_watts": random.uniform(1000, 2000),
                "load_watts": random.uniform(500, 1500),
                "mppt1_watts": random.uniform(0, 1000),
                "mppt2_watts": random.uniform(0, 1000),
                "total_pv_watts": random.uniform(0, 2000),
                "battery_watts": random.uniform(-1000, 1000),
                "battery_soc": random.uniform(40, 100),
                
                "grid_voltage": random.uniform(220, 240),
                "grid_freq": random.uniform(49.8, 50.2),
                
                "inv_voltage": 230.0,
                "inv_freq": 50.0,
                
                "mppt1_v": random.uniform(100, 200),
                "mppt1_a": random.uniform(0, 5),
                "mppt2_v": random.uniform(100, 200),
                "mppt2_a": random.uniform(0, 5),
                "pv_eff": random.uniform(90, 98),
                
                "bat_volts": random.uniform(48, 54),
                "bat_amps": random.uniform(-20, 20),
                "bat_cycles": 125,
                "bat_temp": random.uniform(20, 30),
            }
            
            self.data_updated.emit(mock_data)
            time.sleep(2)  # Update every 2 seconds

    def stop(self):
        self.running = False
        self.wait()
