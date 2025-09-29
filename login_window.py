import requests
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QMainWindow
from PyQt5.QtCore import QSettings

from capcha.caphca import CapchaWindow

from widgets.login_window_widgets import LoginForm, RegisterForm

class LoginWindow(QMainWindow):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success  # callback для перехода в главное окно
        self.setWindowTitle("Авторизация — Auralis")
        self.resize(300, 300)
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.login_form = LoginForm()
        self.register_form = RegisterForm()
        
        layout.addWidget(self.login_form)
        layout.addWidget(self.register_form)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.register_form.setVisible(False)

        self.login_form.login_button.clicked.connect(self.login)
        self.register_form.swith_btn.clicked.connect(self.swith_form)
        self.register_form.reg_button.clicked.connect(self.registration)
        self.login_form.swith_btn.clicked.connect(self.swith_form)
        
    def check_valid(self, username, password):
        if not username or not password:
            self.login_form.status_label.setText("Заполните все поля")
            return
        
    def swith_form(self):
        print("123")
        if self.register_form.isVisible():
            self.register_form.setVisible(False)
            self.login_form.setVisible(True)
        else:
            self.register_form.setVisible(True)
            self.login_form.setVisible(False)
            
        self.centralWidget().adjustSize()
        self.adjustSize()
        
    def registration(self):
        username = self.register_form.username_input.text().strip()
        password = self.register_form.password_input.text().strip()
        
        self.check_valid(username, password)
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/register",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                self.swith_form()
            else:
                error_detail = response.json().get("detail", "Неизвестная ошибка")
                self.login_form.status_label.setText(f"{error_detail}")
                self.capha = CapchaWindow()
                self.capha.show()
                

        except requests.exceptions.ConnectionError:
            self.login_form.status_label.setText("Сервер недоступен")
        except Exception as e:
            self.login_form.status_label.setText(f"Ошибка: {str(e)}")
        
        
                  
    def login(self):
        username = self.login_form.username_input.text().strip()
        password = self.login_form.password_input.text().strip()

        if not username or not password:
            self.login_form.status_label.setText("Заполните все поля")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:8000/login",
                params={"username": username, "password": password}
            )

            if response.status_code == 200:
                self.login_form.status_label.setText("Успешно!")
                token = response.json()["access_token"]

                settings = QSettings("Auralis", "App")
                settings.setValue("auth_token", token)

                self.on_success(token)
            else:
                error_detail = response.json().get("detail", "Неизвестная ошибка")
                self.login_form.status_label.setText(f"{error_detail}")
                self.capha = CapchaWindow()
                self.capha.show()
                

        except requests.exceptions.ConnectionError:
            self.login_form.status_label.setText("Сервер недоступен")
        except Exception as e:
            self.login_form.status_label.setText(f"Ошибка: {str(e)}")