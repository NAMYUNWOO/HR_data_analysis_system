from PyQt5.QtWidgets import *

class MyDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        # 레이블,Edit,버튼 컨트롤

        btnrun = QPushButton("실행")
        btnstop = QPushButton("종료")

        # 레이아웃
        layout = QVBoxLayout()

        layout.addWidget(btnrun)
        layout.addWidget(btnstop)

        # 다이얼로그에 레이아웃 지정
        self.setLayout(layout)
        btnOk.clicked.connect(self.btnOkClicked)
        btnstop.clicked.connect(self.btnStopClicked)
    def btnOkClicked(self):
        return 0

    def btnStopClicked(self):
        return 0

def main():
    app = QApplication([])
    dialog = MyDialog()
    dialog.show()
    app.exec_()

if __name__ == "__main__":
    main()
