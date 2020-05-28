from PyQt5.QtWidgets import QApplication

from src.app import App


def main() -> None:
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
