import json
import os
import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from installer.loading import Window as LoadingUI
from urllib import request
from pathlib import Path
import webbrowser


def is_wifi_on() -> bool:
	try:
		request.urlopen('https://extras.snackbag.net/', timeout=1)
		return True
	except:
		return False


class QHLine(QFrame):
	def __init__(self):
		super(QHLine, self).__init__()
		self.setFrameShape(QFrame.Shape.HLine)
		self.setFrameShadow(QFrame.Shadow.Sunken)


class QErrorDialog(QMessageBox):
	def __init__(self, message: str = "Invalid Operation!", title: str = "Error"):
		super().__init__()

		self.resize(300, 250)
		self.setWindowTitle(title)
		self.setIcon(QMessageBox.Icon.Critical)

		dialog = QMessageBox(parent=self, text=message)
		dialog.setWindowTitle(title)
		dialog.setIcon(dialog.Icon.Critical)
		dialog.exec()


class Window(QWidget):
	def __init__(self, app_: QApplication):
		super().__init__()
		self.version = 1
		self.method_create_account = None

		self.w = None

		self.save_folder = None
		self.project_folder = None

		self.check_url = f"https://extras.snackbag.net/crystal/register/validate?username=%username%&password=%password%"
		self.register_url = f"https://extras.snackbag.net/crystal/register?username=%username%&password=%password%"
		self.installer_url = f"https://raw.githubusercontent.com/snackbag-net/CrystalStudio-Installer/main/installer/installer.json"
		self.login_url = f"http://extras.snackbag.net/crystal/login?username=%username%&password=%password%"

		if not is_wifi_on():
			QErrorDialog("The installer needs to be connected to the internet to install")
			sys.exit()

		self.check_latest_version()

		if sys.platform not in ["darwin", "win32"]:
			QErrorDialog("Unsupported operating system! If you are using Linux, try to clone the GitHub repository instead of using the installer")

		self.mk_default_folders()

		self.pages = []
		self.page_data = ["Welcome to the CrystalStudio Setup", "Choose save folder", "Choose project folder",
		                  "Installation Options", "CrystalStudio Account"]
		self.current_page = 0
		self.build_default()
		self.switch_page(0)

		self.developer_shortcut = QShortcut("Shift+Alt+D", self)
		self.developer_shortcut.activated.connect(self.enable_devmode)

	def mk_default_folders(self):
		# Save and projects folder
		if sys.platform == "darwin":
			self.save_folder = os.path.expanduser("~/Library/Application Support/SnackBag/CrystalStudio/")
			Path(self.save_folder).mkdir(parents=True, exist_ok=True)

			self.project_folder = os.path.expanduser("~/CrystalProjects/")
			Path(self.project_folder).mkdir(parents=True, exist_ok=True)
		elif sys.platform == "win32":
			self.save_folder = Path(Path(os.getenv('APPDATA')) / Path("/SnackBag/CrystalStudio/"))
			self.save_folder.mkdir(parents=True, exist_ok=True)

			self.project_folder = os.path.expanduser("~/CrystalProjects/")
			Path(self.project_folder).mkdir(parents=True, exist_ok=True)
		else:
			self.save_folder = Path("/")
			self.project_folder = os.path.expanduser("~/CrystalProjects/")
			Path(self.project_folder).mkdir(parents=True, exist_ok=True)

	def build_default(self):
		style_title = "font-size: 24px; font-weight: bold;"

		self.setFixedSize(640, 512)
		self.setWindowTitle("CrystalStudio Setup")
		self.setContentsMargins(0, 0, 0, 0)

		side_layout = QHBoxLayout(self)
		other_layout = QVBoxLayout(self)
		self.space = QLabel()
		self.space.setStyleSheet("background: url(\"installer/side.png\");")
		self.space.setFixedWidth(200)
		other_layout.addWidget(self.space)

		self.layout = QVBoxLayout()
		self.title = QLabel("Welcome to the CrystalStudio Setup")
		self.title.setWordWrap(True)
		self.title.setStyleSheet(style_title)
		self.layout.addWidget(self.title)
		self.layout.addLayout(side_layout)

		side_layout.addLayout(other_layout)
		side_layout.addLayout(self.layout)

		self.build_pages()
		self.layout.addStretch()

		btns_layout = QHBoxLayout(self)
		self.layout.addLayout(btns_layout)

		btns_layout.addStretch()

		self.back_btn = QPushButton("Back")
		self.back_btn.clicked.connect(self.last_page)
		btns_layout.addWidget(self.back_btn)

		self.next_btn = QPushButton("Next")
		self.next_btn.setDefault(True)
		self.next_btn.clicked.connect(self.next_page)
		btns_layout.addWidget(self.next_btn)

	def build_pages(self):
		style_title = "font-size: 14px; font-weight: 500;"

		# Page 1 (0)
		self.pages.append([])
		page: list = self.pages[0]

		text = QLabel(
			"Setup will guide you through the installation of CrystalStudio.\n\nIt is recommended that you close all other applications before starting Setup. This will make it possible to update relevant system files without having to reboot your computer.\n\nClick Next to continue.")
		text.setWordWrap(True)
		text.adjustSize()
		text.hide()
		self.layout.addWidget(text)

		page.append(text)

		# Page 2 (1)
		self.pages.append([])
		page: list = self.pages[1]

		text2 = QLabel(
			"Setup will save CrystalStudio addons and other data in the following folder. To select a different folder, click Browse and select another folder.\n\nNote: this is not the folder where CrystalStudio will be installed in!\n\nClick Next to continue.\n")
		text2.setWordWrap(True)
		text2.adjustSize()
		text2.hide()
		self.layout.addWidget(text2)

		save_folder_l = QHBoxLayout()
		self.layout.addLayout(save_folder_l)
		self.save_folder_i = QLineEdit(self.save_folder)
		self.save_folder_i.hide()
		save_folder_l.addWidget(self.save_folder_i)
		save_folder_b = QPushButton("Browse")
		save_folder_b.clicked.connect(self.update_save_folder)
		save_folder_b.hide()
		save_folder_l.addWidget(save_folder_b)

		page.append(text2)
		page.append(self.save_folder_i)
		page.append(save_folder_b)

		# Page 3 (2)
		self.pages.append([])
		page: list = self.pages[2]

		text3 = QLabel(
			"Setup will save CrystalStudio projects in the following folder. To select a different folder, click Browse and select another folder.\n\nNote: this is not the folder where CrystalStudio will be installed in!\n\nClick Next to continue.")
		text3.setWordWrap(True)
		text3.adjustSize()
		text3.hide()
		self.layout.addWidget(text3)

		project_folder_l = QHBoxLayout()
		self.layout.addLayout(project_folder_l)
		self.project_folder_i = QLineEdit(self.project_folder)
		self.project_folder_i.hide()
		project_folder_l.addWidget(self.project_folder_i)
		project_folder_b = QPushButton("Browse")
		project_folder_b.clicked.connect(self.update_project_folder)
		project_folder_b.hide()
		project_folder_l.addWidget(project_folder_b)

		page.append(text3)
		page.append(self.project_folder_i)
		page.append(project_folder_b)

		# Page 4 (3)
		self.pages.append([])
		page: list = self.pages[3]

		g1_title = QLabel("Create Desktop Shortcut (Windows-only)")
		g1_title.adjustSize()
		g1_title.hide()
		self.layout.addWidget(g1_title)

		g1_hbox = QHBoxLayout()
		g1_check = QCheckBox()

		# Desktop shortcut only for Windows users
		if sys.platform != 'win32':
			g1_check.setDisabled(True)

		g1_check.hide()
		g1_text = QLabel("CrystalStudio")
		g1_text.hide()
		g1_hbox.addWidget(g1_check)
		g1_hbox.addWidget(g1_text)
		g1_hbox.addStretch()
		self.layout.addLayout(g1_hbox)

		page.append(g1_title)
		page.append(g1_check)
		page.append(g1_text)

		g2_title = QLabel("Install optional default addons")
		g2_title.adjustSize()
		g2_title.hide()
		g2_line = QHLine()
		g2_line.hide()
		self.layout.addWidget(g2_line)
		self.layout.addWidget(g2_title)

		g2_hbox = QHBoxLayout()
		g2_check = QCheckBox()
		g2_check.setChecked(True)

		g2_check.hide()
		g2_text = QLabel("Discord Integration")
		g2_text.hide()
		g2_hbox.addWidget(g2_check)
		g2_hbox.addWidget(g2_text)
		g2_hbox.addStretch()
		self.layout.addLayout(g2_hbox)

		g2_hbox2 = QHBoxLayout()
		g2_check2 = QCheckBox()
		g2_check2.setChecked(True)

		g2_check2.hide()
		g2_text2 = QLabel("Game2D Generator")
		g2_text2.hide()
		g2_hbox2.addWidget(g2_check2)
		g2_hbox2.addWidget(g2_text2)
		g2_hbox2.addStretch()
		self.layout.addLayout(g2_hbox2)

		page.append(g2_title)
		page.append(g2_check)
		page.append(g2_text)
		page.append(g2_line)

		page.append(g2_check2)
		page.append(g2_text2)

		# Page 5 (4)
		self.pages.append([])
		page: list = self.pages[4]

		acc_info = QLabel("An account is needed to install addons, publish addons or games, use coop mode and much more! It will be hard to change this data after, so be careful.\n\nPress Finish to create or login to the account and install CrystalStudio. Don't forget to press Check first!\n")
		acc_info.setWordWrap(True)
		self.layout.addWidget(acc_info)

		acc_info.hide()
		page.append(acc_info)

		tab_wgt1 = QWidget()
		tab_layout1 = QVBoxLayout()
		tab_wgt1.setLayout(tab_layout1)
		tab_wgt2 = QWidget()
		tab_layout2 = QVBoxLayout()
		tab_wgt2.setLayout(tab_layout2)

		# Tab 1
		acc1_layout = QHBoxLayout(self)
		acc1_l = QLabel("Username")
		acc1_l.hide()
		self.acc1_i = QLineEdit()
		self.acc1_i.hide()
		acc1_layout.addWidget(acc1_l)
		acc1_layout.addWidget(self.acc1_i)
		tab_layout1.addLayout(acc1_layout)

		page.append(acc1_l)
		page.append(self.acc1_i)

		acc2_layout = QHBoxLayout(self)
		acc2_l = QLabel("Password")
		acc2_l.hide()
		self.acc2_i = QLineEdit()
		self.acc2_i.setEchoMode(QLineEdit.EchoMode.Password)
		self.acc2_i.hide()
		acc2_layout.addWidget(acc2_l)
		acc2_layout.addWidget(self.acc2_i)
		tab_layout1.addLayout(acc2_layout)

		page.append(acc2_l)
		page.append(self.acc2_i)

		acc3_layout = QHBoxLayout(self)
		acc3_l = QLabel("Repeat password")
		acc3_l.hide()
		self.acc3_i = QLineEdit()
		self.acc3_i.setEchoMode(QLineEdit.EchoMode.Password)
		self.acc3_i.hide()
		acc3_layout.addWidget(acc3_l)
		acc3_layout.addWidget(self.acc3_i)
		tab_layout1.addLayout(acc3_layout)

		self.check_btn = QPushButton("Check")
		self.check_btn.pressed.connect(self.check_userdata)
		self.check_btn.hide()
		tab_layout1.addWidget(self.check_btn)

		page.append(acc3_l)
		page.append(self.acc3_i)
		page.append(self.check_btn)

		# Tab 2
		login_acc1_layout = QHBoxLayout(self)
		login_acc1_l = QLabel("Username")
		login_acc1_l.hide()
		self.login_acc1_i = QLineEdit()
		self.login_acc1_i.hide()
		login_acc1_layout.addWidget(login_acc1_l)
		login_acc1_layout.addWidget(self.login_acc1_i)
		tab_layout2.addLayout(login_acc1_layout)

		page.append(login_acc1_l)
		page.append(self.login_acc1_i)

		login_acc2_layout = QHBoxLayout(self)
		login_acc2_l = QLabel("Password")
		login_acc2_l.hide()
		self.login_acc2_i = QLineEdit()
		self.login_acc2_i.setEchoMode(QLineEdit.EchoMode.Password)
		self.login_acc2_i.hide()
		login_acc2_layout.addWidget(login_acc2_l)
		login_acc2_layout.addWidget(self.login_acc2_i)
		tab_layout2.addLayout(login_acc2_layout)

		page.append(login_acc2_l)
		page.append(self.login_acc2_i)

		self.login_check_btn = QPushButton("Check")
		self.login_check_btn.pressed.connect(self.check_userdata_login)
		self.login_check_btn.hide()
		page.append(self.login_check_btn)
		tab_layout2.addWidget(self.login_check_btn)

		self.tabs = QTabWidget()
		self.tabs.addTab(tab_wgt1, "Register")
		self.tabs.addTab(tab_wgt2, "Login")
		self.tabs.hide()

		page.append(self.tabs)
		self.layout.addWidget(self.tabs)

	def check_userdata(self):
		username = self.acc1_i.text()
		pw1 = self.acc2_i.text()
		pw2 = self.acc3_i.text()

		if pw1 != pw2:
			QErrorDialog("Passwords aren't the same!")
			return

		check_url = self.check_url
		check_url = check_url.replace("%username%", username)
		check_url = check_url.replace("%password%", pw1)
		try:
			with request.urlopen(check_url) as resp:
				raw_data = resp.read().decode()
				data = json.loads(raw_data)
				print(f"Received answer from server: {data}")
				if data.get("state") is None:
					QErrorDialog("Something went wrong! Try again later. ('state' is None)")
					return

				state = data["state"]
				if state == "error":
					QErrorDialog(data["reason"])
				else:
					self.check_btn.setDisabled(True)
					self.login_check_btn.setDisabled(True)
					self.tabs.setDisabled(True)
					self.next_btn.setEnabled(True)

					self.method_create_account = True
		except:
			QErrorDialog("You can't use those characters")

	def check_userdata_login(self):
		username = self.login_acc1_i.text()
		pw = self.login_acc2_i.text()

		check_url = self.login_url
		check_url = check_url.replace("%username%", username)
		check_url = check_url.replace("%password%", pw)
		try:
			with request.urlopen(check_url) as resp:
				raw_data = resp.read().decode()
				data = json.loads(raw_data)
				print(f"Received answer from server: {data}")
				if data.get("state") is None:
					QErrorDialog("Something went wrong! Try again later. ('state' is None)")
					return

				state = data["state"]
				if state == "error":
					QErrorDialog(data["reason"])
				else:
					self.check_btn.setDisabled(True)
					self.login_check_btn.setDisabled(True)
					self.tabs.setDisabled(True)
					self.next_btn.setEnabled(True)

					self.method_create_account = False
		except:
			QErrorDialog("You can't use those characters")

	def switch_page(self, page: int):
		for elem in self.pages[self.current_page]:
			elem.hide()

		self.current_page = page

		user_url = "https://extras.snackbag.net/crystal/get/"
		if self.current_page >= len(self.pages):
			print("Installing")
			if self.method_create_account:
				username = json.loads(request.urlopen(user_url + self.acc1_i.text()).read().decode())["data"]["username"]
				password = self.acc2_i.text()
			else:
				username = json.loads(request.urlopen(user_url + self.login_acc1_i.text()).read().decode())["data"]["username"]
				password = self.login_acc2_i.text()

			self.hide()
			self.w = LoadingUI(
				app,
				self.method_create_account,
				self.save_folder,
				self.project_folder,
				username,
				password,
				self.check_url,
				self.register_url,
				self.login_url
			)
			self.w.show()
			return

		if self.current_page >= len(self.pages) - 1:
			self.next_btn.setText("Finish")
			self.next_btn.setDisabled(True)

		if self.current_page < len(self.pages) - 1:
			self.next_btn.setText("Next")
			self.next_btn.setEnabled(True)

		if self.current_page <= 0:
			self.back_btn.setDisabled(True)
		else:
			self.back_btn.setDisabled(False)

		for elem in self.pages[page]:
			elem.show()

		self.title.setText(self.page_data[page])

	def next_page(self):
		self.switch_page(self.current_page + 1)

	def last_page(self):
		self.switch_page(self.current_page - 1)

	def enable_devmode(self):
		def update_vars(din1: QLineEdit, din2: QLineEdit, din3: QLineEdit, din4: QLineEdit):
			self.check_url = din1.text()
			self.register_url = din2.text()
			self.version = int(din3.text())
			self.login_url = din4.text()
			print(f"Updated check url to {self.check_url}")
			print(f"Updated register url to {self.register_url}")
			print(f"Updated version to {self.version}")
			print(f"Updated login url to {self.login_url}")

		self.space.setStyleSheet("background: url(\"installer/side_dev.png\");")
		QErrorDialog("Developer mode activated - Use with caution. \n\nIF SOMEBODY HAS ASKED YOU TO OPEN THIS, THERE IS AN 11/10 CHANCE YOU ARE GETTING SCAMMED! CLOSE THE INSTALLER IMMEDIATELY")
		print("[INFO]")
		print("User has enabled developer mode - No support will be given")
		print("[INFO]")

		dialog = QDialog(self)
		dialog.setWindowTitle("Developer mode")
		dialog.setMinimumSize(500, 300)
		din1 = QLineEdit(dialog)
		din1.setFixedWidth(500)
		din1.setText(self.check_url)

		din2 = QLineEdit(dialog)
		din2.setFixedWidth(500)
		din2.move(0, 30)
		din2.setText(self.register_url)

		din3 = QLineEdit(dialog)
		din3.move(0, 60)
		din3.setText(str(self.version))

		din4 = QLineEdit(dialog)
		din4.setFixedWidth(500)
		din4.move(0, 90)
		din4.setText(self.login_url)

		dsb = QPushButton(dialog)
		dsb.move(10, 280)
		dsb.setText("Update")
		dsb.clicked.connect(lambda: update_vars(din1, din2, din3, din4))

		dvb = QPushButton(dialog)
		dvb.move(90, 280)
		dvb.setText("CLV()")
		dvb.clicked.connect(self.check_latest_version)

		dub = QPushButton(dialog)
		dub.move(160, 280)
		dub.setText("CUD()")
		dub.clicked.connect(self.check_userdata)

		dialog.exec()

	def check_latest_version(self):
		print(f"Checking for latest version at {self.installer_url}")
		with request.urlopen(self.installer_url) as resp:
			raw_data = resp.read()
			data = json.loads(raw_data.decode())

			if self.version < data['ver']:
				QErrorDialog("Installer is outdated. Please install new version!")
				print("[INFO]")
				print("Outdated installer, no support.")
				print("[INFO]")

	def update_save_folder(self):
		self.save_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.save_folder))
		self.save_folder_i.setText(self.save_folder)

	def update_project_folder(self):
		self.project_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.project_folder))
		self.project_folder_i.setText(self.project_folder)


app = QApplication(sys.argv)

window = Window(app)
window.show()

sys.exit(app.exec())
