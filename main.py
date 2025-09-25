# main.py
import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QPushButton, QMessageBox
)
from PyQt5.QtCore import QSettings

from login_window import LoginWindow


class MainWindow(QMainWindow):
    def __init__(self, token, logout_callback):
        super().__init__()
        self.token = token
        self.logout_callback = logout_callback
        self.setWindowTitle("Auralis — Главное окно")
        self.resize(400, 300)

        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Добро пожаловать в Auralis!"))

        # Пробуем получить данные пользователя
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("http://127.0.0.1:8000/protected", headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                layout.addWidget(QLabel(f"Вы вошли как: <b>{user_data['username']}</b>"))
            elif response.status_code == 401:
                QMessageBox.warning(self, "Сессия истекла", "Ваш токен недействителен. Пожалуйста, войдите снова.")
                self.logout_callback()
                return
            else:
                layout.addWidget(QLabel("Не удалось загрузить профиль"))

        except requests.exceptions.ConnectionError:
            layout.addWidget(QLabel("❌ Сервер недоступен"))
        except Exception as e:
            layout.addWidget(QLabel(f"❌ Ошибка: {str(e)}"))

        # Кнопка выхода
        logout_button = QPushButton("🚪 Выйти")
        logout_button.setStyleSheet("background-color: #ff6b6b; color: white; padding: 8px;")
        logout_button.clicked.connect(self.logout_callback)
        layout.addWidget(logout_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.settings = QSettings("Auralis", "App")
        self.token = self.settings.value("auth_token", None)

        if self.token and self.validate_token(self.token):
            self.open_main_window()
        else:
            self.open_login_window()

    def validate_token(self, token):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("http://127.0.0.1:8000/protected", headers=headers)
            return response.status_code == 200
        except:
            return False

    def open_login_window(self):
        self.login_window = LoginWindow(on_success=self.open_main_window)
        self.login_window.show()

    def open_main_window(self, token=None):
        if token:
            self.settings.setValue("auth_token", token)
            self.token = token

        self.main_window = MainWindow(self.token, self.logout)
        self.main_window.show()

        # Закрыть окно логина, если оно было открыто
        if hasattr(self, 'login_window'):
            self.login_window.close()

    def logout(self):
        # Удаляем токен из настроек
        self.settings.remove("auth_token")
        self.token = None

        # Закрываем главное окно
        if hasattr(self, 'main_window'):
            self.main_window.close()

        # Открываем окно логина
        self.open_login_window()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = AppController()
    controller.run()