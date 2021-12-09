

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QMessageBox, QPushButton)

class MainWindow:
    def creareFereastra(self, mesaj):
        app = QApplication(sys.argv)
        Aplicatie = QWidget()
        Aplicatie.setWindowTitle('Aplicatie')
        Aplicatie.resize(800, 800)

        self.n_Label = QLabel(Aplicatie)
        self.n_Label.setText('Proiect RC')

        self.afisare_line=QLineEdit(Aplicatie)
        self.afisare_line.setReadOnly(True)
        self.afisare_line.move(80,200)
        self.afisare_line.resize(650,500)


        self.title_Label = QLabel(Aplicatie)
        self.title_Label.setText('Aplicatie pentru descoperirea unei topologii de retea ')
        self.title_Label.move(130, 40)
        self.title_Label.setFont(QFont('Arial',15))
        self.title_Label2 = QLabel(Aplicatie)
        self.title_Label2.setText('pe baza mecanismului de comunicație RIPv2')
        self.title_Label2.move(140, 80)
        self.title_Label2.setFont(QFont('Arial',15))


        self.afisare_Btn = QPushButton('Afisare tabela de rutare', Aplicatie)

        def on_button_clicked():
            #for x in mesaj:
                self.afisare_line.setText(mesaj)
        self.afisare_Btn.clicked.connect(on_button_clicked)

        self.afisare_Btn.move(80,150)



        Aplicatie.show()
        sys.exit(app.exec_())

