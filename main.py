from PyQt5 import QtCore, QtGui, QtWidgets
from design import Ui_MainWindow

import os
from tiny_scanner import Scanner
import tiny_parser
from tiny_parser import Parser
from tiny_parser import ParsingError
from anytree.exporter import DotExporter

# self.tabWidget.setStyleSheet("QTabBar::tab { height: 30;width: 430px; }")


class MainClass(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow); 

        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.clear_btn.clicked.connect(self.clear_code)
        self.run_btn.clicked.connect(self.run_code)

        self.output_text.setReadOnly(True)
        self.msg_text.setReadOnly(True)
        self.msg_2_text.setReadOnly(True)

        self.graph_area.setScaledContents(True)
        
    def open_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget)
        if filename[0]:
            with open(filename[0], 'r') as file:
                data = file.read()
                self.input_text.setPlainText(data)


    def save_file(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self.centralwidget)
        if filename[0]:
            with open(filename[0], 'w') as file:
                output = self.output_text.toPlainText()
                file.write(output)


    def clear_code(self):
        self.input_text.setPlainText('')
        self.output_text.setPlainText('')
        self.msg_text.setPlainText('')
        self.msg_2_text.setPlainText('')

        self.graph_area.setPixmap(QtGui.QPixmap(""))

    def run_code(self):
        data = self.input_text.toPlainText()
        scanner = Scanner(data)
        tokens, errors = scanner.get_tokens()

        msg = ''
        if errors:
            msg = 'Syntax Error in lines '
            
            self.input_text.setPlainText('')
            last_index = 0
            for e in errors:
                self.input_text.insertPlainText (''.join(data[last_index:e[0]]))
                self.input_text.appendHtml(f'<span style="color:#ff002b";>{data[e[0]:e[1]]}</span>')
                last_index = e[1]

                msg += '_ {}'.format(data.count("\n", 0, e[1])+1) 
                
            self.input_text.insertPlainText (''.join(data[last_index:]))

        else:
            if tokens:
                msg = 'Tokens generated with no errors'
            else:
                msg = 'Enter Code first!'
            
            
        self.msg_text.setPlainText(msg)  

        self.output_text.setPlainText('')
        for t in tokens:
            self.output_text.appendPlainText(f'{t[1]} , {t[0]}')

        
        self.graph_area.setPixmap(QtGui.QPixmap(""))

        if not errors and tokens:
            try:
                parser = Parser(scanner)
                syntax_tree = parser.get_syntax_tree()
                DotExporter(syntax_tree, nodeattrfunc=parser.nodeattrfunc).to_picture("syntax_tree.png")
                self.graph_area.setPixmap(QtGui.QPixmap("syntax_tree.png"))

                self.msg_text.appendPlainText('Parsing done and syntax tree generated!')
                self.msg_2_text.setPlainText('Syntax tree generated successfully!')

            except ParsingError as e:
                self.msg_text.appendPlainText(f'{e}')
                self.msg_2_text.setPlainText("Syntax tree couldn't be generated, fix the errors first!")

            except FileNotFoundError as e:
                self.msg_text.appendPlainText('Please install graphviz from the following link to visualize the syntax tree: \nhttps://graphviz.org/download/')
                self.msg_2_text.setPlainText('Please install graphviz from the following link to visualize the syntax tree: \nhttps://graphviz.org/download/')
        else:
            if tokens:
                self.msg_2_text.setPlainText("Syntax tree couldn't be generated, Fix the errors first!")
            else:
                self.msg_2_text.setPlainText("Syntax tree couldn't be generated, Enter code and run first!")
  

if __name__ == "__main__":
    import sys
    scanner = None
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainClass()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

