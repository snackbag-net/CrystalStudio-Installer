import threading
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class Window(QWidget):
	def __init__(self):
		super().__init__()
		self.theme = """
QWidget {
	background-color: #1e2022;
	font-size: 16px;
	font-family: "Lucida Grande";
	color: #f2f3f5;
}

QLabel {
	color: white;
	background: transparent;
}

QProgressBar::chunk {
	background-color: white;
	border-radius: 0;
}

		"""
		# Set window frameless
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
		self.setWindowTitle("Loading")

		# Set style
		self.setStyleSheet(self.theme)

		# Set background image
		self.bg = QPixmap("installer/loading.png").scaled(823, 246, Qt.AspectRatioMode.KeepAspectRatio)
		self.bg_holder = QLabel()
		self.bg_holder.move(0, 0)
		self.bg_holder.setPixmap(self.bg)

		# Layout required, otherwise image does not show up
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.bg_holder)

		self.activity_title = QLabel(self)
		self.activity_title.setText("Installing: Creating CrystalStudio Account")
		self.activity_title.adjustSize()
		self.activity_title.move(10, 200)

		self.progress_bar = QProgressBar(self)
		self.progress_bar.setFixedWidth(803)
		self.progress_bar.setFixedHeight(3)
		self.progress_bar.move(10, 230)
		self.progress_bar.setValue(10)

		# Finally, set the window size
		self.setFixedSize(823, 246)

		self.show()

	def update_progress(self, args: dict):
		self.activity_title.setText(args["text"])
		self.progress_bar.setValue(args["value"])

	def finish_progress(self, args: dict):
		self.hide()
