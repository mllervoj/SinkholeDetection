from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QHBoxLayout, QCheckBox, QSizePolicy, QTextEdit, QGroupBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt

from main import Main

import os
import datetime

class ProcesThread(QThread):
    finished = pyqtSignal()
    
    def __init__(self, input, output, parameters):
        super().__init__()
        self.input = input
        self.output = output
        self.parameters = parameters

    def run(self):
        Main(self.input, self.output, self.parameters)
        self.finished.emit()


class Ui_MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowTitle("Detekce terénních depresí")
        
    def setupUi(self):
        self.setFixedWidth(600)
        layout = QVBoxLayout()

        # Výběr souboru LAZ/LAS
        self.file_label = QLabel("Vstupní soubor (.shp)*")
        self.file_path = QLineEdit()
        self.file_button = QPushButton("Vybrat soubor")
        self.file_button.clicked.connect(self.select_file)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.file_button)

        layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        # Výběr výstupní složky
        self.folder_label = QLabel("Výstupní složka:*")
        self.folder_path = QLineEdit()
        self.folder_button = QPushButton("Vybrat složku")
        self.folder_button.clicked.connect(self.select_folder)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(self.folder_button)

        layout.addWidget(self.folder_label)
        layout.addLayout(folder_layout)

        # Název souboru
        self.name_label = QLabel("Název výstupního souboru:*")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # 5 číselných parametrů
        self.parameters_label = QLabel("Parametry:")
        layout.addWidget(self.parameters_label)
        
        self.param_inputs = []
        self.param_checks = []
        parameters = ['Minimální plocha vrstevnice [m2]', 'Maximální plocha vrstevnice [m2]', 'Minimální hloubka [cm]', 'Maximální hloubka [cm]', 'Maximální poměr šířky a délky MMB vrstevnice']
        for i in parameters:
            param_layout = QHBoxLayout()
            param_label = QLabel(f"{i}:")
            param_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            param_input = QLineEdit()
            param_input.setAlignment(Qt.AlignmentFlag.AlignRight)
            param_input.setFixedWidth(200)
            param_input.setDisabled(True)
            validator = QIntValidator()
            validator.setRange(0,1000000)
            param_input.setValidator(validator)
            param_check = QCheckBox()
            param_check.setStyleSheet("QCheckBox { margin-left: 10px; }")
            
            def on_state_change(state, le=param_input, cb=param_check):
                is_checked = cb.isChecked()
                le.setEnabled(is_checked)
                if not is_checked:
                    le.clear()
            
            param_check.stateChanged.connect(on_state_change)
            
            param_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            param_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            param_check.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            
            self.param_inputs.append(param_input)
            self.param_checks.append(param_check)
            
            param_layout.addWidget(param_label)
            param_layout.addWidget(param_input)
            param_layout.addWidget(param_check)
            param_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addLayout(param_layout)     
            
        # Spouštěcí tlačítko
        self.run_button = QPushButton("Spustit proces")
        self.run_button.clicked.connect(self.run_process)
        layout.addWidget(self.run_button)

        groupbox = QGroupBox("Výsledky")
        groupbox_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setFixedHeight(300)
        groupbox_layout.addWidget(self.text_output)
        groupbox.setLayout(groupbox_layout)
        layout.addWidget(groupbox)
        
        self.setLayout(layout)
        self.setWindowTitle("Moje aplikace v PyQt6")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyberte soubor", "", "SHP Files (*.shp)")
        if file_path:
            self.file_path.setText(file_path)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Vyberte složku")
        if folder_path:
            self.folder_path.setText(folder_path)

    def run_process(self):
        self.file_input = self.file_path.text()
        self.folder = self.folder_path.text()
        name = self.name_input.text()
        self.file_output = f"{self.folder}/{name}.shp"
        self.params = [param.text() for param in self.param_inputs]
        
        output_files = [
            os.path.join(self.folder, f"{name}.shp"),
            os.path.join(self.folder, f"{name}.shx"),
            os.path.join(self.folder, f"{name}.prj"),
            os.path.join(self.folder, f"{name}.dbf"),
            os.path.join(self.folder, f"{name}.cpg"),
        ]
        
        if not self.file_input or not self.folder or not name:
            self.text_output.clear()
            self.text_output.append("Chyba ve vstupních parametrech:")
            self.text_output.append("")
            self.text_output.append("Všechny povinné parametry musí být vyplněny!")
            self.text_output.append("")
            self.text_output.append("Proces nebyl spuštěn!")
            return
        
        if not self.file_input.lower().endswith(('.shp')):
            self.text_output.clear()
            self.text_output.append("Chyba ve vstupních parametrech:")
            self.text_output.append("")
            self.text_output.append("Vybraný soubor musí mít koncovku .shp!")
            self.text_output.append("")
            self.text_output.append("Proces nebyl spuštěn!")
            return
        
        if not os.path.exists(self.file_input):
            self.text_output.clear()
            self.text_output.append("Chyba ve vstupních parametrech:")
            self.text_output.append("")
            self.text_output.append("Vybraný soubor neexistuje!")
            self.text_output.append("")
            self.text_output.append("Proces nebyl spuštěn!")
            return
        
        if not os.path.isdir(self.folder):
            self.text_output.clear()
            self.text_output.append("Chyba ve vstupních parametrech:")
            self.text_output.append("")
            self.text_output.append("Vybraná cesta není platná složka!")
            self.text_output.append("")
            self.text_output.append("Proces nebyl spuštěn!")
            return
        
        if any(os.path.exists(f) for f in output_files):
            self.text_output.clear()
            self.text_output.append("Chyba ve vstupních parametrech:")
            self.text_output.append("")
            self.text_output.append("Výstupní soubor již existuje!")
            self.text_output.append("")
            self.text_output.append("Proces nebyl spuštěn!")
            return
        
        for i in range(len(self.params)):
            if self.params[i] == '':
                self.params[i] = -1
            else:
                self.params[i] = int(self.params[i])

        if any(self.params) == 0:
            self.text_output.clear()
            self.text_output.append("Chyba ve vstupních parametrech:")
            self.text_output.append("")
            self.text_output.append("Vstupní parametry musí být kladná čísla!")
            self.text_output.append("")
            self.text_output.append("Proces nebyl spuštěn!")
            return
        
        try:    
            self.proces_start()
                            
            self.vlakno = ProcesThread(self.file_input, self.file_output, self.params)
            self.vlakno.start()
            self.error = False
            self.vlakno.finished.connect(self.proces_end)

        except Exception as e:
            self.error = True
            self.er = e
            self.proces_end()
            
    def proces_start(self):
        self.run_button.setDisabled(True)
        
        self.text_output.clear()
        
        self.now1 = datetime.datetime.now()
        now1_str = self.now1.strftime('%d.%m.%Y-%H:%M:%S')
        self.text_output.append('Začátek procesu: ' + now1_str)            
        self.text_output.append('')
        self.text_output.append('Byl zahájen proces vyhledávání teréních depresí s parametry:')
        self.text_output.append(f'Vstupní soubor: {self.file_input}')
        self.text_output.append(f'Výstupní soubor: {self.file_output}')
        self.text_output.append(f'Parametry: {self.params}')
        self.text_output.append('')
        self.text_output.append('Proces může trvat několik minut, prosím, nezavírejte okno aplikace!!!')
        
        QApplication.processEvents()
        
    def proces_end(self):
        self.run_button.setEnabled(True)
        now2 = datetime.datetime.now()
        now2_str = now2.strftime('%d.%m.%Y-%H:%M:%S')
        time = now2-self.now1
        
        if os.path.exists(self.file_output):
            self.text_output.append('')
            self.text_output.append(f'Výstupní soubory byly vytvořeny ve složce {self.folder}.')
        elif self.error:
            self.text_output.append('')
            self.text_output.append(f"Chyba skriptu: {self.er}!!")
        else:
            self.text_output.append('')
            self.text_output.append(f'Chyba procesu!!')
           
        self.text_output.append('') 
        self.text_output.append('Konec Procesu: ' + now2_str + ' (' + str(time) + ')')