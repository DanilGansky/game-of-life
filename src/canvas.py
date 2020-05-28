from typing import Dict, Optional

from PyQt5.QtCore import (QEvent, QLine, QObject, QRect, QRectF, QTimer,
                          pyqtSignal)
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from src.game import Game


class GenerationUpdateSignal(QObject):
    generation_update = pyqtSignal(int)


class Canvas(QWidget):
    def __init__(self, size: int = 10,
                 parent: Optional[QWidget] = None,
                 *args, **kwargs) -> None:
        super(Canvas, self).__init__(*args, **kwargs)
        self._qp = QPainter()
        self._timer = QTimer()
        self._timer.timeout.connect(self.redraw)
        self._colors = {
            0: {
                'cells': QColor('green'),
                'background': QColor('white'),
                'grid': QColor('black')
            }, 1: {
                'cells': QColor('black'),
                'background': QColor('white'),
                'grid': QColor('black')
            }}

        self.next_generation_signal = GenerationUpdateSignal()

        self.game = Game()
        self.size = size
        self._color_scheme = self._colors[0]
        self._grid = []
        self._rects = []

    @property
    def color_scheme(self) -> Dict[str, QColor]:
        return self._color_scheme

    @color_scheme.setter
    def color_scheme(self, color_index: int) -> None:
        self._color_scheme = self._colors[color_index]

    def start(self) -> None:
        self.game.width = self.width() // self.size
        self.game.height = self.height() // self.size
        self._grid.clear()
        self.clear()
        self.spawn()

    def continue_game(self, upd_time: int) -> None:
        self._timer.start(upd_time)

    def pause(self) -> None:
        self._timer.stop()

    def clear(self) -> None:
        self.game.reset()
        self.redraw(next_generation=False)

    def redraw(self, next_generation: bool = True) -> None:
        self.draw_grid()

        if next_generation:
            self.game.next_generation()

        self.draw_rects()
        self.update()
        self.next_generation_signal.generation_update.emit(
            self.game.generation)

    def spawn(self) -> None:
        self.game.random_generate(count=1000)
        self.redraw(next_generation=False)

    def draw_grid(self) -> None:
        if not self._grid:
            for x in range(0, self.width() + self.size, self.size):
                self._grid.append(QLine(x, 0, x, self.height()))
            for y in range(0, self.height() + self.size, self.size):
                self._grid.append(QLine(0, y, self.width(), y))

    def draw_rects(self) -> None:
        self._rects.clear()
        for x in range(self.game.width):
            for y in range(self.game.height):
                if self.game.area[y][x]:
                    rect = QRect(x * self.size, y * self.size,
                                 self.size, self.size)
                    value = self.game.area[y][x]
                    self._rects.append((rect, value))

    def draw_rect(self, x: int, y: int) -> None:
        x, y = x // self.size, y // self.size
        self.game.spawn_or_destroy(x, y)
        self.redraw(next_generation=False)

    def set_aging(self, mode: bool,
                  max_age: int, end_breeding_age: int) -> None:
        self.clear()
        self.game.aging = mode
        self.game.max_age = max_age
        self.game.end_breeding_age = end_breeding_age

    def paintEvent(self, event: QEvent) -> None:
        import copy

        self._qp.begin(self)
        self._qp.setBrush(QBrush(self._color_scheme['background']))
        self._qp.drawRect(QRectF(0, 0, self.width(), self.height()))

        self._qp.setPen(QPen(self._color_scheme['grid']))

        for line in self._grid:
            self._qp.drawLine(line)

        for rect, value in self._rects:
            color = copy.copy(self._color_scheme['cells'])

            if self.game.aging:
                color.setAlpha(value * self.game.alpha)

            self._qp.setBrush(QBrush(color))
            self._qp.drawRect(rect)

        self._qp.end()

    def mousePressEvent(self, event: QEvent) -> None:
        self.draw_rect(event.x(), event.y())
