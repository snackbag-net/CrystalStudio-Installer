import json
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path
from urllib import request

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


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


class InstallThread(QThread):
	update_progress = pyqtSignal(object)
	finish_progress = pyqtSignal(object)

	def __init__(
			self,
			parent,
			create_account: bool,
			save_folder: Path,
			projects_folder: Path,
			username: str,
			password: str,
			check_url: str,
			register_url: str,
			login_url: str
	):
		QThread.__init__(self, parent)
		print("Initializing install thread")
		self.create_account = create_account
		self.save_folder = save_folder
		self.projects_folder = projects_folder
		self.token = None
		self.username = username
		self.password = password
		self.check_url = check_url
		self.register_url = register_url
		self.login_url = login_url

	def run(self):
		print("Fixing URLs")
		# Update URLs to correct username and password
		self.check_url = self.check_url.replace("%username%", self.username)
		self.check_url = self.check_url.replace("%password%", self.password)

		self.register_url = self.register_url.replace("%username%", self.username)
		self.register_url = self.register_url.replace("%password%", self.password)

		self.login_url = self.login_url.replace("%username%", self.username)
		self.login_url = self.login_url.replace("%password%", self.password)

		print("Install thread: run")
		if self.create_account:
			print("Registering pre-emit")
			self.update_progress.emit({"text": "Installing: Registering CrystalStudio account", "value": 10})
			with request.urlopen(self.register_url) as resp:
				data = json.loads(resp.read().decode())
				if data.get("state") != "success":
					print(f"Failed register. {self.register_url=}, {self.login_url=}, {self.check_url=}, {data=}")
					QErrorDialog(f"Could not create account due to an error: {data.get('reason')}")
					sys.exit(0)

				self.token = data["token"]
				secrets = {"username": self.username, "token": self.token}
				self.dump_secrets(secrets)
				print("Dumped secrets")
		else:
			print("Login pre-emit")
			self.update_progress.emit({"text": "Logging in CrystalStudio account", "value": 10})
			with request.urlopen(self.login_url) as resp:
				data = json.loads(resp.read().decode())
				if data.get("state") != "success":
					print(f"Failed login. {self.register_url=}, {self.login_url=}, {self.check_url=}, {data=}")
				if data.get("state") != "success":
					QErrorDialog(f"Could not login due to an error: {data.get('reason')}")
					sys.exit(0)

				self.token = data["token"]
				secrets = {"username": self.username, "token": self.token}
				self.dump_secrets(secrets)
				print("Dumped secrets")

		time.sleep(0.2)  # control time
		print(f"Created/logged into account {self.username}")
		download_url = "https://github.com/snackbag-net/empty-installation/archive/refs/tags/test-3.zip"  # TODO: Needs to be automated (High priority)
		unzipped_name = download_url.split("/")[4] + "-" + download_url.split("/")[8][:-4]
		self.update_progress.emit({"text": "Installing: Preparing download", "value": 20})
		if not os.path.exists("installation"):
			os.mkdir("installation")
		installation_location = Path("installation/download.zip")
		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Installing: Downloading latest release...", "value": 40})

		with request.urlopen(download_url) as dl_file:
			with open(installation_location, 'wb') as out_file:
				out_file.write(dl_file.read())

		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Installing: Unpacking latest release...", "value": 50})
		with zipfile.ZipFile(installation_location, "r") as zip_ref:
			zip_ref.extractall(installation_location.parent)

		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Installing: Setting up safe installation...", "value": 60})
		unpacked_installation = installation_location.parent / Path(unzipped_name)
		installation_json = json.load(open(unpacked_installation / "installation.json", "r"))
		libs: list[str] = installation_json["libs"]
		content: list[str] = installation_json["content"]

		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Installing: Installing libraries...", "value": 70})
		os.system("python -m pip install --upgrade pip")
		for lib in libs:
			os.system(f"python -m pip install {lib}")

		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Installing: Installing CrystalStudio...", "value": 80})
		for cnt in content:
			print(f"Installing content '{cnt}'")
			if cnt.endswith("/"):
				if os.path.exists(cnt):
					print("Removing original...")
					shutil.rmtree(cnt)
			else:
				if os.path.exists(cnt):
					print("Removing original...")
					os.remove(cnt)

			shutil.move(unpacked_installation / cnt, os.getcwd())
			print(f"Finished installing content '{cnt}'")

		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Installing: Setting up CrystalStudio...", "value": 90})

		time.sleep(0.2)  # control time
		self.update_progress.emit({"text": "Finishing...", "value": 100})

		shutil.rmtree("installation")

		time.sleep(0.2)  # control time
		self.finish_progress.emit(None)

	def dump_secrets(self, secrets: dict):
		with open(Path(self.save_folder) / "secrets.json", "w") as f:
			json.dump(secrets, f, indent=4)


class Window(QWidget):
	def __init__(self, app: QApplication, create_account: bool, save_folder: Path, projects_folder: Path, username: str,
	             password: str, check_url: str, register_url: str, login_url: str):
		super().__init__()
		self.app = app
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
		self.activity_title.setText("Setting up installation...")
		self.activity_title.adjustSize()
		self.activity_title.move(10, 200)

		self.progress_bar = QProgressBar(self)
		self.progress_bar.setFixedWidth(803)
		self.progress_bar.setFixedHeight(3)
		self.progress_bar.move(10, 230)
		self.progress_bar.setValue(0)

		# Finally, set the window size
		self.setFixedSize(823, 246)

		self.show()

		install_thread = InstallThread(self, create_account, save_folder, projects_folder, username, password, check_url, register_url, login_url)
		install_thread.update_progress.connect(self.update_progress)
		install_thread.finish_progress.connect(self.finish_progress)
		install_thread.start()

	def update_progress(self, args: dict):
		self.activity_title.setText(args["text"])
		self.progress_bar.setValue(args["value"])
		self.activity_title.adjustSize()
		print(f"updating to {args['text']} - {args['value']}")

	def finish_progress(self):
		print("Finished installation")
		self.hide()
		dialog = QMessageBox(parent=self, text="Successfully installed CrystalStudio! Please restart the app.")
		dialog.setWindowTitle("Finished")
		dialog.setIcon(dialog.Icon.Information)
		dialog.exec()

		sys.exit()
