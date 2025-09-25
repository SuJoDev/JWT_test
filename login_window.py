import requests
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QSettings

from capcha.caphca import CapchaWindow

class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success  # callback для перехода в главное окно
        self.setWindowTitle("Авторизация — Auralis")
        self.resize(300, 200)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Войти")
        self.status_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_label.setText("❌ Заполните все поля")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:8000/login",
                params={"username": username, "password": password}
            )

            if response.status_code == 200:
                self.status_label.setText("✅ Успешно!")
                token = response.json()["access_token"]

                settings = QSettings("Auralis", "App")
                settings.setValue("auth_token", token)

                self.on_success(token)
            else:
                error_detail = response.json().get("detail", "Неизвестная ошибка")
                self.status_label.setText(f"❌ {error_detail}")
                self.capha = CapchaWindow()
                self.capha.show()
                

        except requests.exceptions.ConnectionError:
            self.status_label.setText("❌ Сервер недоступен")
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")