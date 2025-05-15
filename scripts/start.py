import traceback
import sys
from PyQt6.QtWidgets import QApplication

from GUI import Ui_MainWindow

if __name__ == "__main__":
	try:
		app = QApplication(sys.argv)
		window = Ui_MainWindow()
		window.show()
		sys.exit(app.exec())
	except Exception:
		traceback.print_exc()
		input("Chyba skriptu!")