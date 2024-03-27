""" Start Window for plotting Crypto Historical Data """
import io
from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel
import matplotlib.pyplot as plt
from ChartDialog import ChartDialog as cd
from BTC_history import CandlestickChart

class MainWindow(QtWidgets.QWidget):
    """ Main window class"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotting Historical Crypto Data")
        self.resize(800, 300)

        icon = QtGui.QIcon("currency_bitcoin_FILL0_wght400_GRAD0_opsz24.svg")
        self.setWindowIcon(icon)

        font = QtGui.QFont()
        font.setPointSize(12)

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)

        self.select_setting_button = QtWidgets.QPushButton("Select", self)
        self.select_setting_button.setFont(font)
        self.select_setting_button.clicked.connect(self.open_select_dialog)
        self.layout.addWidget(self.select_setting_button, 0, 0)

        self.plot_button = QtWidgets.QPushButton("Plot", self)
        self.plot_button.setFont(font)
        self.plot_button.clicked.connect(self.plotdata)
        self.layout.addWidget(self.plot_button, 1, 0)

        self.clear_button = QtWidgets.QPushButton("Clear", self)
        self.clear_button.setFont(font)
        self.clear_button.clicked.connect(self.clear)
        self.layout.addWidget(self.clear_button, 2, 0)

        self.close_button = QtWidgets.QPushButton("Close", self)
        self.close_button.setFont(font)
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button, 3, 0)

        self.layout_thumbs = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.layout_thumbs, 4, 0, alignment=Qt.AlignLeft)

        self.setting_label = QtWidgets.QLabel("No settings selected", self)
        self.setting_label.setFont(font)
        self.layout.addWidget(self.setting_label, 5, 0)

    def update_settings_label(self):
        """ update setting label """
        exchange = self.exchange_combobox.currentText()
        symbol = self.pair_combobox.currentText()
        timeframe = self.time_combobox.currentText()
        limit = self.limit_input.value()

        settings_text = f"Exchange: {exchange} - Symbol: {symbol} - Timeframe: {timeframe} - Limit: {limit}"
        self.setting_label.setText(settings_text)

    def plotdata(self):
        """ Plot the data """
        self.chart.plot_chart()
        text = f"{self.chart.symbol}"
        plt.close(self.chart.get_figure())
        dialog = cd(self.chart, parent=self)
        dialog.dialogClosed.connect(self.handle_dialog_closed)
        dialog.show()

        thumb_img = self.generate_thumbnail(self.chart)
        layout_thumb = QtWidgets.QVBoxLayout()
        thumb_label = QLabel()
        thumb_label.setPixmap(thumb_img)
        layout_thumb.addWidget(thumb_label)
        layout_thumb.addWidget(QLabel(text))
        self.layout_thumbs.addLayout(layout_thumb)
        self.clear()

    def handle_dialog_closed(self, message):
        """ Handle dialog close """
        for i in reversed(range(self.layout_thumbs.count())):
            layout = self.layout_thumbs.itemAt(i).layout()
            if layout is None:
                continue
            for j in reversed(range(layout.count())):
                widget = layout.itemAt(j).widget()
                if widget and widget.text() == message:
                    while layout.count():
                        child = layout.takeAt(0)
                        widget = child.widget()
                        if widget:
                            widget.deleteLater()
                    self.layout_thumbs.removeItem(layout)
                    layout.deleteLater()
                    break
        self.layout_thumbs.update()

    def clear(self):
        """ clear the data """
        self.setting_label.setText("No settings selected")

    def generate_thumbnail(self, chart, thumbnail_size=(100, 60)):
        """ Generate Thumbnail """
        fig = chart.get_figure()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='svg')
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap.scaled(QSize(*thumbnail_size))

    def set_combobox(self, title, items, font):
        """ Setting comboboxes """
        layout = QtWidgets.QHBoxLayout()

        combobox = QtWidgets.QComboBox()
        combobox.addItems(items)
        combobox.setFont(font)
        pair_label = QtWidgets.QLabel(title)
        pair_label.setFont(font)
        layout.addWidget(pair_label)
        layout.addWidget(combobox)

        return layout, combobox

    def open_select_dialog(self):
        """ Open Select dialogue """
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Select Chart Parameters")
        dialog.resize(400, 250)

        icon = QtGui.QIcon("monitoring_FILL0_wght400_GRAD0_opsz24.svg")
        dialog.setWindowIcon(icon)

        font = QtGui.QFont()
        font.setPointSize(12)

        layout = QtWidgets.QVBoxLayout()

        layout_combo, combo = self.set_combobox("Pair: ", ["BTC/USD", "ETH/USD", "LTC/USD", "BCH/USD"], font)

        self.pair_combobox = combo
        layout.addLayout(layout_combo)

        layout_combo, combo = self.set_combobox("Time: ", ["1d", "4h", "1h"], font)

        self.time_combobox = combo
        layout.addLayout(layout_combo)

        layout_combo, combo = self.set_combobox("Exchange: ", ["Binance", "Kraken"], font)

        self.exchange_combobox = combo
        layout.addLayout(layout_combo)

        layout_limit = QtWidgets.QHBoxLayout()

        self.limit_input = QtWidgets.QSpinBox()
        self.limit_input.setRange(50, 1000)
        self.limit_input.setValue(150)
        self.limit_input.setFont(font)
        limit_label = QtWidgets.QLabel("Limit: ")
        limit_label.setFont(font)
        layout_limit.addWidget(limit_label)
        layout_limit.addWidget(self.limit_input)
        layout.addLayout(layout_limit)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.setFont(font)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        result = dialog.exec()
        if result == QtWidgets.QDialog.Accepted:
            self.update_settings_label()
            self.chart = CandlestickChart(exchange=self.exchange_combobox.currentText(),
                                          symbol=self.pair_combobox.currentText(),
                                          timeframe=self.time_combobox.currentText(),
                                          limit=self.limit_input.value())

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = MainWindow()
    window.show()
    app.exec()
