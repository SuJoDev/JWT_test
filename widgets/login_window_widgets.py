from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                             QLabel, QPushButton)


class RegisterForm(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.swith_btn = QPushButton("Форма авторизации")
        self.reg_button = QPushButton("Зарегестрироваться")
        self.status_label = QLabel()
        
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.swith_btn)
        layout.addWidget(self.reg_button)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
         
        #login
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.swith_btn = QPushButton("Зарегестрироваться")
        self.login_button = QPushButton("Войти")
        self.status_label = QLabel()
        

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.swith_btn)
        layout.addWidget(self.login_button)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)