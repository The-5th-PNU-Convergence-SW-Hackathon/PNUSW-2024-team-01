import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QFileDialog
from main import main

def execute():
    user_id = input_id.text()
    user_pw = input_pw.text()   
    main(user_id, user_pw, input_file.text())

def open_file_dialog():
    file_path, _ = QFileDialog.getOpenFileName()
    if file_path:
        input_file.setText(file_path)
# 애플리케이션 객체 생성
app = QApplication(sys.argv)

# 메인 윈도우 생성
window = QWidget()
window.setWindowTitle('PyQt5 Example')

# 레이아웃 생성
layout = QVBoxLayout()


# 아이디 레이블 및 입력 필드
label_id = QLabel('ID')
input_id = QLineEdit()
layout.addWidget(label_id)
layout.addWidget(input_id)

# 패스워드 레이블 및 입력 필드
label_pw = QLabel('Password')
input_pw = QLineEdit()
input_pw.setEchoMode(QLineEdit.Password)  # 입력 시 패스워드를 숨김 처리
layout.addWidget(label_pw)
layout.addWidget(input_pw)


# 파일 경로 레이블 및 입력 필드
label_file = QLabel('Select a File')
input_file = QLineEdit()
layout.addWidget(label_file)
layout.addWidget(input_file)

#실행 버튼
execute_button = QPushButton('execute')
execute_button.clicked.connect(execute)
layout.addWidget(execute_button)

# 파일 찾기 버튼
file_button = QPushButton('Browse')
file_button.clicked.connect(open_file_dialog)
layout.addWidget(file_button)

# 메인 윈도우에 레이아웃 설정
window.setLayout(layout)

# 윈도우 표시
window.show()

# 애플리케이션 실행
sys.exit(app.exec_())