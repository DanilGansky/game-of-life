from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMainWindow

from src.canvas import Canvas
from src.window import Ui_MainWindow


class App(Ui_MainWindow, QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.canvas = Canvas(size=self.cell_size.value(),
                             parent=self.centralwidget)
        self.horizontalLayout.addWidget(self.canvas)

        self.play.clicked.connect(self.start_game)
        self.pause.clicked.connect(self.pause_game)
        self.clear.clicked.connect(self.canvas.clear)
        self.new_btn.clicked.connect(self.new_game)
        self.spawn_btn.clicked.connect(self.canvas.spawn)
        self.max_age.valueChanged.connect(self.control_aging)
        self.end_breeding_age.valueChanged.connect(self.control_aging)
        self.enable_aging_btn.stateChanged.connect(
            lambda x: self.control_aging(x))
        self.color_scheme.currentIndexChanged.connect(
            lambda x: self.set_color_scheme(x))

        self.upd_time_slider.valueChanged.connect(
            lambda x: self.set_upd_time(x))

        self.canvas.next_generation_signal.generation_update.connect(
            lambda x: self.generationUpdateEvent(x))

    def new_game(self) -> None:
        self.canvas.size = self.cell_size.value()
        self.canvas.start()

    def start_game(self) -> None:
        if self.play.isChecked():
            upd_time = self.upd_time_slider.value()
            self.canvas.continue_game(upd_time)
        self.pause.setChecked(False)
        self.play.setChecked(True)

    def pause_game(self) -> None:
        if self.pause.isChecked():
            self.canvas.pause()
        self.play.setChecked(False)
        self.pause.setChecked(True)

    def set_upd_time(self, update_interval: int) -> None:
        self.upd_time.setText(f'{update_interval}ms')
        if self.play.isChecked():
            self.canvas.continue_game(update_interval)

    def set_color_scheme(self, index: int) -> None:
        self.canvas.color_scheme = index
        self.canvas.redraw(next_generation=False)

    def control_aging(self, state: bool = True) -> None:
        max_age = self.max_age.value()
        end_breeding_age = self.end_breeding_age.value()
        self.groupBox_2.setEnabled(state)
        self.canvas.set_aging(state, max_age, end_breeding_age)

    def generationUpdateEvent(self, generation: int) -> None:
        self.generation_value.setText(str(generation))

    def showEvent(self, event: QEvent) -> None:
        self.new_game()
