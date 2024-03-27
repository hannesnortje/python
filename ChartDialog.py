
""" Class to open Chart Dialog """
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QCheckBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

class ChartDialog(QDialog):
    """ Chart Dialog """
    dialogClosed = Signal(str)
    def __init__(self, chart, parent=None):
        super().__init__(parent)
        self.__chart = chart

        self.dialog()

    @property
    def chart(self):
        """ getter chart """
        return self.__chart
    
    @chart.setter
    def chart(self, chart):
        """ setter chart """
        self.__chart = chart

    def dialog(self):
        """ Dialog builder """

        try:
            
            self.setWindowTitle(f"{self.chart.title}")
            view_layout = QHBoxLayout()
            view_layout = QHBoxLayout()
            choice_layout = QVBoxLayout()

            choice_layout.addStretch(1)

            cb_volume = QCheckBox("Volume")
            cb_volume.setChecked(self.chart.show_volume)
            cb_volume.stateChanged.connect(lambda state: self.update_volume(state))

            choice_layout.addWidget(cb_volume)

            cb_mav = QCheckBox("MAV")
            cb_mav.setChecked(self.chart.show_mav)
            cb_mav.stateChanged.connect(lambda state: self.update_mav(state))

            choice_layout.addWidget(cb_mav)

            cb_apds = QCheckBox("Bollinger")
            cb_apds.setChecked(self.chart.show_apds)
            cb_apds.stateChanged.connect(lambda state: self.update_apds(state))

            choice_layout.addWidget(cb_apds)

            choice_layout.addStretch(1)


            view_layout.addLayout(choice_layout)


            view_layout.addLayout(choice_layout)

            layout = QVBoxLayout()
            self.chart_container = QWidget()
            self.chart_layout = self.build_chart()
            self.chart_container.setLayout(self.chart_layout)
            layout.addStretch(1)
            layout.addWidget(self.chart_container, alignment=Qt.AlignCenter)
            layout.addStretch(1)

            button_layout = QHBoxLayout()
            button_layout.addStretch(1)
            close_button = QPushButton("Close")
            close_button.clicked.connect(self.close)
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)
            view_layout.addLayout(layout)

            self.setLayout(view_layout)
        except Exception as e:
            print(f"Error creating chart: {e}")
    
    def build_chart(self):
        """ Build Chart """
        chart_layout = QVBoxLayout()
        figure = self.chart.get_figure()
        canvas = FigureCanvas(figure)
        chart_layout.addWidget(canvas) 
        toolbar = NavigationToolbar(canvas, self)
        chart_layout.addWidget(toolbar)
        return chart_layout

    def update_volume(self, state):
        """ Update Volume """
        self.chart.show_volume = (state == 2)
        self.update_chart()

    def update_mav(self, state):
        """ Update MAV """
        self.chart.show_mav = (state == 2)
        self.update_chart()
    
    def update_apds(self, state):
        """ Update Bollinger """
        self.chart.show_apds = (state == 2)
        self.update_chart()
    
    def update_chart(self):
        self.chart.show_chart()
        self.chart_container.layout().removeItem(self.chart_layout)
        self.chart_layout = self.build_chart()
        self.chart_container.setLayout(self.chart_layout)

    def closeEvent(self, event):
        """ Cloe Event """
        self.dialogClosed.emit(self.chart.symbol)
        super().closeEvent(event)

if __name__ == "__main__":
    ChartDialog(plt.gcf())
