from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from .widgets.gauge import CustomGauge
from .widgets.battery import BatteryGraphic

class DataBlock(QWidget):
    def __init__(self, title, color, initial_val="--"):
        super().__init__()
        self.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: rgba(255,255,255,0.7); font-weight: bold; font-size: 12px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_value = QLabel(initial_val)
        self.lbl_value.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addStretch()

    def set_value(self, val_str):
        self.lbl_value.setText(val_str)

class DashboardTab(QScrollArea):
    def update_hardware_data(self, data):
        # Update Gauges
        if 'grid_watts' in data: self.gauges['Grid Watts'].set_value(data['grid_watts'])
        if 'load_watts' in data: self.gauges['Load Watts'].set_value(data['load_watts'])
        if 'mppt1_watts' in data: self.gauges['MPPT 1 W'].set_value(data['mppt1_watts'])
        if 'mppt2_watts' in data: self.gauges['MPPT 2 W'].set_value(data['mppt2_watts'])
        if 'total_pv_watts' in data: self.gauges['Total PV W'].set_value(data['total_pv_watts'])
        if 'battery_watts' in data: self.gauges['Battery W'].set_value(data['battery_watts'])
        
        # Update Battery SOC
        if 'battery_soc' in data: self.battery_graphic.set_soc(data['battery_soc'])
        
        # Plot Logic Update
        if not hasattr(self, 'plot_data'):
            self.plot_data = {'time': [], 'grid': [], 'load': [], 'pv': [], 'batt': []}
            
        import time
        self.plot_data['time'].append(time.time())
        self.plot_data['grid'].append(data.get('grid_watts', 0))
        self.plot_data['load'].append(data.get('load_watts', 0))
        self.plot_data['pv'].append(data.get('total_pv_watts', 0))
        self.plot_data['batt'].append(data.get('battery_watts', 0))
        
        # Keep rolling window of 100 points
        if len(self.plot_data['time']) > 100:
            for k in self.plot_data:
                self.plot_data[k] = self.plot_data[k][-100:]
                
        # Normalize relative time axis to seconds since first ping
        start_t = self.plot_data['time'][0]
        x_axis = [t - start_t for t in self.plot_data['time']]
        
        self.curve_grid.setData(x_axis, self.plot_data['grid'])
        self.curve_load.setData(x_axis, self.plot_data['load'])
        self.curve_pv.setData(x_axis, self.plot_data['pv'])
        self.curve_batt.setData(x_axis, self.plot_data['batt'])
        
        # Update Blocks
        if 'grid_voltage' in data: self.blocks['Grid Voltage'].set_value(f"{data['grid_voltage']:.1f} V")
        if 'grid_freq' in data: self.blocks['Grid Freq'].set_value(f"{data['grid_freq']:.1f} Hz")
        if 'load_watts' in data: self.blocks['Load Watts'].set_value(f"{data['load_watts']:.1f} W")
        if 'inv_voltage' in data: self.blocks['Inv Voltage'].set_value(f"{data['inv_voltage']:.1f} V")
        if 'inv_freq' in data: self.blocks['Inv Freq'].set_value(f"{data['inv_freq']:.1f} Hz")
        
        if 'mppt1_v' in data: self.blocks['MPPT 1 V'].set_value(f"{data['mppt1_v']:.1f} V")
        if 'mppt1_a' in data: self.blocks['MPPT 1 A'].set_value(f"{data['mppt1_a']:.1f} A")
        if 'mppt2_v' in data: self.blocks['MPPT 2 V'].set_value(f"{data['mppt2_v']:.1f} V")
        if 'mppt2_a' in data: self.blocks['MPPT 2 A'].set_value(f"{data['mppt2_a']:.1f} A")
        if 'pv_eff' in data: self.blocks['PV EFF'].set_value(f"{data['pv_eff']:.1f} %")
        
        if 'bat_volts' in data: self.blocks['Bat Volts'].set_value(f"{data['bat_volts']:.1f} V")
        if 'bat_amps' in data: self.blocks['Bat Amps'].set_value(f"{data['bat_amps']:.1f} A")
        if 'bat_cycles' in data: self.blocks['Bat Cycles'].set_value(f"{data['bat_cycles']}")
        if 'bat_temp' in data: self.blocks['Bat Temp'].set_value(f"{data['bat_temp']:.1f} °C")
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        self.setWidget(container)
        
        # 1. Top Row: Analog Gauges + Battery Graphic
        top_layout = QHBoxLayout()
        self.gauges = {
            "Grid Watts": CustomGauge("Grid Watts", 0, 8000),
            "Load Watts": CustomGauge("Load Watts", 0, 8000),
            "MPPT 1 W": CustomGauge("MPPT 1 W", 0, 4000),
            "MPPT 2 W": CustomGauge("MPPT 2 W", 0, 4000),
            "Total PV W": CustomGauge("Total PV W", 0, 8000),
            "Battery W": CustomGauge("Battery W", -5000, 5000),
        }
        for name, gauge in self.gauges.items():
            top_layout.addWidget(gauge)
            
        self.battery_graphic = BatteryGraphic()
        top_layout.addWidget(self.battery_graphic)
        
        layout.addLayout(top_layout)
        
        # 2. Middle Row: Data Grid Key-Value blocks
        mid_layout = QGridLayout()
        self.blocks = {}
        
        # Red blocks: Grid Voltage, Grid Freq.
        self.blocks['Grid Voltage'] = DataBlock("Grid Voltage", "#D32F2F", "230 V")
        self.blocks['Grid Freq'] = DataBlock("Grid Freq", "#D32F2F", "50.0 Hz")
        
        # Blue blocks: Load Watts, Inverter Voltage, Inverter Freq.
        self.blocks['Load Watts'] = DataBlock("Load Watts", "#1976D2", "0 W")
        self.blocks['Inv Voltage'] = DataBlock("Inv Voltage", "#1976D2", "230 V")
        self.blocks['Inv Freq'] = DataBlock("Inv Freq", "#1976D2", "50.0 Hz")
        
        # Green blocks: MPPT Voltages, MPPT Amperages, PV EFF.
        self.blocks['MPPT 1 V'] = DataBlock("MPPT 1 V", "#388E3C", "0 V")
        self.blocks['MPPT 1 A'] = DataBlock("MPPT 1 A", "#388E3C", "0 A")
        self.blocks['MPPT 2 V'] = DataBlock("MPPT 2 V", "#388E3C", "0 V")
        self.blocks['MPPT 2 A'] = DataBlock("MPPT 2 A", "#388E3C", "0 A")
        self.blocks['PV EFF'] = DataBlock("PV EFF", "#388E3C", "0 %")
        
        # Purple/Grey blocks: Battery Volts, Amps, Cycles, Time to 100%, Temperature.
        self.blocks['Bat Volts'] = DataBlock("Bat Volts", "#7B1FA2", "50.0 V")
        self.blocks['Bat Amps'] = DataBlock("Bat Amps", "#7B1FA2", "0 A")
        self.blocks['Bat Cycles'] = DataBlock("Cycles", "#616161", "0")
        self.blocks['Time to 100%'] = DataBlock("Time to 100%", "#616161", "--:--")
        self.blocks['Bat Temp'] = DataBlock("Bat Temp", "#616161", "25 °C")

        # Organize into grid (2 rows)
        row1_keys = ['Grid Voltage', 'Grid Freq', 'Load Watts', 'Inv Voltage', 'Inv Freq', 'MPPT 1 V', 'MPPT 1 A', 'Bat Volts']
        row2_keys = ['MPPT 2 V', 'MPPT 2 A', 'PV EFF', 'Bat Amps', 'Bat Cycles', 'Time to 100%', 'Bat Temp']
        
        # Adding some spacing to the grid to separate it
        mid_layout.setSpacing(10)
        
        for i, key in enumerate(row1_keys):
            mid_layout.addWidget(self.blocks[key], 0, i)
        for i, key in enumerate(row2_keys):
            mid_layout.addWidget(self.blocks[key], 1, i)
            
        layout.addLayout(mid_layout)
        
        # 3. Chart Area
        self.plot_widget = pg.PlotWidget(title="24-Hour Power Overview (Watts)")
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend(offset=(10, 10))
        self.plot_widget.setLabel('left', 'Watts', units='W')
        self.plot_widget.setLabel('bottom', 'Time') # TODO: AxisTimeItem setup for proper time
        
        # Dummy series setup
        self.curve_grid = self.plot_widget.plot(name="Grid", pen=pg.mkPen(color='#D32F2F', width=2))
        self.curve_load = self.plot_widget.plot(name="Load", pen=pg.mkPen(color='#1976D2', width=2))
        self.curve_pv = self.plot_widget.plot(name="PV", pen=pg.mkPen(color='#388E3C', width=2))
        self.curve_batt = self.plot_widget.plot(name="Battery", pen=pg.mkPen(color='#7B1FA2', width=2))
        
        layout.addWidget(self.plot_widget, stretch=1)
        
        # 4. Bottom Row: Aggregates
        bottom_layout = QHBoxLayout()
        agg_keys = ["Daily Grid kWh", "Total kWh Used", "PV kWh Produced", "Bat Chg/Dis kWh", "Max Load Day", "Monthly Summary"]
        for key in agg_keys:
            block = DataBlock(key, "#455A64", "0.0")
            bottom_layout.addWidget(block)
            self.blocks[f"agg_{key}"] = block
            
        layout.addLayout(bottom_layout)
